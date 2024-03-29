from django.db.models import Q
from web.models import User, Account, Contact, Lead, Opportunity, Organization, Location, Route, Event
from .conf import OBJECTS
from .util import get_locations_related_to_map, get_routes_for_location_ids, get_timezone_for, get_org_id
from ..util import init_matrix, map_by, get_deep, find_deep, select
from ..common import RecordSet, DataSet
from app.util import env, lenv, boolean, clamp, DAY, get_default_date
from pytz import timezone
from operator import attrgetter
from functools import partial
import random
import datetime as dt
import logging
import os

logger = logging.getLogger(__name__)

PENALTY = env('PENALTY', 9*60*60, int)
DAY_START = lenv('DAY_START', '9:0:0', int, sep=':')
DAY_END = lenv('DAY_END', '18:0:0', int, sep=':')
MORNING = dt.time(*DAY_START)
EVENING = dt.time(*DAY_END)
DEFAULT_DRIVING_TIME = env('DEFAULT_DRIVING_TIME', 30*60, int)
OVERRIDE_DRIVING_TIME = env('OVERRIDE_DRIVING_TIME', None, int)
ENABLE_EVENTS = env('ENABLE_EVENTS', True, boolean)
ENABLE_REMOTE_SERVICES = env('ENABLE_REMOTE_SERVICES', True, boolean)
SERVICES = [
    { 'type': 'meeting', 'time': 1 * 60 * 60, 'penalty': 1 },
]

if ENABLE_REMOTE_SERVICES:
    SERVICE_CALL_PENALTY = env('SERVICE_CALL_PENALTY', 0.1, float)
    SERVICE_EMAIL_PENALTY = env('SERVICE_EMAIL_PENALTY', 0.05, float)
    SERVICE_CALL_TIME = env('SERVICE_CALL_TIME', 30 * 60, int)
    SERVICE_EMAIL_TIME = env('SERVICE_EMAIL_TIME', 30 * 60, int)
    REMOTE_SERVICES = [
        { 'type': 'call', 'time': SERVICE_CALL_TIME, 'penalty': SERVICE_CALL_PENALTY, 'fields': 'phone_fields' },
        { 'type': 'email', 'time': SERVICE_EMAIL_TIME, 'penalty': SERVICE_EMAIL_PENALTY, 'fields': 'email_fields' },
    ]

class DBDataSet(DataSet):
    def __init__(self, user, accounts, contacts, leads, opportunities, events, orgs, date):
        self.user = user
        self.account = RecordSet(accounts)
        self.contact = RecordSet(contacts)
        self.lead = RecordSet(leads)
        self.opportunity = RecordSet(opportunities)
        if ENABLE_EVENTS:
            self.event = RecordSet(events)
        if ENABLE_REMOTE_SERVICES:
            self.organization = RecordSet(orgs)
        self.stops = []
        self.date = date
        self.day = {
            'start': dt.datetime.combine(date, MORNING),
            'end': dt.datetime.combine(date, EVENING)
        }
        
        self._fetch_locations()
        self._fetch_routes()
        self._create_basic_stops()
        
        if ENABLE_EVENTS:
            self._create_existing_stops(date)
        
        if ENABLE_REMOTE_SERVICES:
            self._create_remote_stops()
        
        logger.debug('All stops:')
        for i in range(len(self.stops)):
            stop = self.stops[i]
            logger.debug(
                '%d. %s: %s/%s/%d/%d/%s/%d/%d/%s' % (
                    i + 1,
                    stop.obj_name,
                    stop.record.pk,
                    stop.location.related_to_component if stop.location else '<empty>',
                    stop.record.score if hasattr(stop.record, 'score') else -1,
                    stop.penalty if stop.penalty != None else -1,
                    stop.service_type,
                    stop.service_time,
                    stop.time_window[0] if stop.time_window else -1,
                    stop.remote
                )
            )
    
    def _fetch_locations(self):
        # IDs of the records we have to fetch locations for
        id_map = {
            'account': set(self.account.ids),
            'contact': set(self.contact.ids),
            'lead': set(self.lead.ids),
        }
        
        if ENABLE_EVENTS:
            id_map['event'] = set(self.event.ids)
        
        if ENABLE_REMOTE_SERVICES:
            id_map['organization'] = set(self.organization.ids)
        
        # Opportunities get their locations from related Accounts
        for opp in self.opportunity.all:
            if opp.account_id:
                id_map['account'].add(opp.account_id)
        
        if ENABLE_EVENTS:
            # Events get their locations from various sources...
            for event in self.event.all:
                if event.who_id:
                    # It doesn't matter that we add the WhoId to both,
                    # only one will match
                    id_map['contact'].add(event.who_id)
                    id_map['lead'].add(event.who_id)
                if event.account_id:
                    id_map['account'].add(event.account_id)
        
        locations = get_locations_related_to_map(id_map)
        self.location = RecordSet(locations)
        self.location_map = map_by(self.location.all, ('related_to', 'related_to_id', 'related_to_component'))
    
    def _fetch_routes(self):
        routes = Route.objects.filter(
            start_id__in=self.location.ids,
            end_id__in=self.location.ids
        )
        
        self.route = RecordSet(routes)
        self.route_map = map_by(routes, ('start_id', 'end_id'))
    
    def _create_basic_stops(self):
        for obj_name in OBJECTS:
            obj = OBJECTS[obj_name]
            if obj['is_fixed'] or obj['is_office']:
                continue
                
            locations_src = obj['parent'] or obj_name
            components = OBJECTS[locations_src]['components']
            record_set = getattr(self, obj_name)
            
            for record in record_set.all:
                penalty = record.score * PENALTY / 100
                
                for component in components:
                    path = (locations_src, getattr(record, obj['loc_id_field']), component)
                    location = get_deep(self.location_map, path, default=None)

                    if obj_name == 'opportunity':
                        logger.debug('Path: %s, location: %s', path, location)
                    
                    if location:
                        for service in SERVICES:
                            self.stops.append(BasicStop(
                                obj_name = obj_name,
                                record = record,
                                service = service,
                                location = location,
                                penalty = int(penalty * service['penalty']),
                            ))
    
    def _create_remote_stops(self):
        for office_obj_name in OBJECTS:
            if not OBJECTS[office_obj_name]['is_office']:
                continue
            office_record_set = getattr(self, office_obj_name)
            
            for office in office_record_set.all:
                for component in OBJECTS[office_obj_name]['components']:
                    location = get_deep(self.location_map, (office_obj_name, office.pk, component), default=None)
                    
                    if location:
                        for obj_name in OBJECTS:
                            obj = OBJECTS[obj_name]
                            if obj['is_office'] or obj['is_fixed']:
                                continue
                            record_set = getattr(self, obj_name)
                            
                            for record in record_set.all:
                                penalty = record.score * PENALTY / 100
                                
                                for service in REMOTE_SERVICES:
                                    field_names = obj[service['fields']]
                                    if any(map(partial(has_field, record), field_names)):
                                        self.stops.append(BasicStop(
                                            obj_name = obj_name,
                                            record = record,
                                            service = service,
                                            location = location,
                                            penalty = int(penalty * service['penalty']),
                                            remote = True
                                        ))
    
    def _create_existing_stops(self, date):
        tz = self.timezone = get_timezone_for(self.user)
        events = []
        
        for event in self.event.all:
            # Get location of the event
            paths = [('event', event.pk, '')]
            
            if event.who_id:
                paths += [(obj_name, event.who_id, component)
                    for obj_name in ('contact', 'lead')
                    for component in OBJECTS[obj_name]['components']
                ]
            
            if event.account_id:
                paths += [('account', event.account_id, component)
                    for component in OBJECTS['account']['components']
                ]
            
            location = find_deep(self.location_map, paths, default=None)
            
            # Get the service_time for the location
            start = event.start_date_time.astimezone(tz)
            end = event.end_date_time.astimezone(tz)

            if start.date() != date or start.time() < MORNING:
                old_start = start
                start = tz.localize(dt.datetime.combine(date, MORNING))
                logger.debug('Clip START: %r -> %r', old_start, start)

            if end.date() != date or end.time() > EVENING:
                old_end = end
                end = tz.localize(dt.datetime.combine(date, EVENING))
                logger.debug('Clip END: %r -> %r', old_end, end)

            service_time = (end - start).total_seconds()
            time_offset = tz.localize(dt.datetime.combine(date, MORNING))
            start_secs = ((start - time_offset).total_seconds())
            
            events.append(BasicStop(
                obj_name = 'event',
                record = event,
                service = { 'type': event.event_subtype, 'time': service_time },
                location = location,
                time_window = (start_secs, start_secs),
                existing = True
            ))
        
        # Check for overlapping events
        # This makes the model choke, as it is not feasible of course
        events = sorted(events, key=lambda stop: stop.time_window[0])
        current_time = 0
        
        for stop in events:
            start = stop.time_window[0]
            # Check if this event overlaps with the previous one
            if start < current_time:
                # Check if it overlaps *fully*
                # i.e. the start and end times are both within the previous event
                if start + stop.service_time <= current_time:
                    # This event overlaps fully
                    # Don't add it to stops
                    continue
                else:
                    # Only start time overlaps
                    diff = current_time - start
                    stop.time_window = (current_time, current_time)
                    stop.service_time = stop.service_time - diff
            
            self.stops.append(stop)
            current_time = stop.time_window[0] + stop.service_time
        
    
    def get_stops(self):
        return self.stops
        
    def get_driving_time(self, from_stop, to_stop):
        if OVERRIDE_DRIVING_TIME != None:
            return OVERRIDE_DRIVING_TIME
            
        start_loc = from_stop.get_location()
        end_loc = to_stop.get_location()
        driving_time = DEFAULT_DRIVING_TIME
        
        # Try to get distance from a Route object
        # Otherwise, just keep the default
        if start_loc and end_loc:
            route = get_deep(self.route_map, (start_loc.pk, end_loc.pk), default=None)
            if route:
                driving_time = route.distance
        
        # Make sure the model stays feasible,
        # even with existing events that might not be feasibly scheduled
        if from_stop.is_existing() and to_stop.is_existing():
            max_time_between = to_stop.time_window[0] - (from_stop.time_window[0] + from_stop.service_time)
            driving_time = min(driving_time, abs(max_time_between))
        
        return driving_time
    
    def get_service_time(self, stop):
        return stop.get_service_time()
    
    def get_penalty(self, stop):
        return stop.get_penalty()
    
    def get_time_window(self, stop):
        return stop.get_time_window()
    
    def is_existing(self, stop):
        return stop.is_existing()
    
    def is_remote(self, stop):
        return stop.is_remote()
    
    def get_loc_id(self, stop):
        return stop.get_record()
            

class BasicStop:
    def __init__(self, **kwargs):
        self.obj_name = kwargs.get('obj_name')
        self.record = kwargs.get('record')
        self.service_type = kwargs.get('service')['type']
        self.service_time = kwargs.get('service')['time']
        self.location = kwargs.get('location')
        self.penalty = kwargs.get('penalty', None)
        self.time_window = kwargs.get('time_window', None)
        self.existing = kwargs.get('existing', False)
        self.remote = kwargs.get('remote', False)
        
    def get_record(self):
        return self.record
        
    def get_service_type(self):
        return self.service_type
    
    def get_service_time(self):
        return self.service_time
        
    def get_penalty(self):
        return self.penalty
        
    def get_location(self):
        return self.location
    
    def is_remote(self):
        return self.remote
    
    def get_time_window(self):
        return self.time_window
    
    def is_existing(self):
        return self.existing
    
    @property
    def __dict__(self):
        return {
            **{
                key: getattr(self, key)
                for key in ['obj_name', 'service_type', 'service_time', 'penalty', 'time_window', 'existing']
            },
            'record_id': self.record.pk,
            'location_id': self.location.pk if self.location else None,
            'location_address': self.location.address if self.location else None
        }
    
    def __repr__(self):
        return str({
            key: getattr(self, key)
            for key in ['obj_name', 'record', 'service_type', 'service_time', 'penalty', 'location', 'time_window', 'existing']
        })


# Converts a naive datetime object that is supposed to be in timezone <tz> to a UTC datetime 
def to_utc(date, tz):
    return tz.localize(date).astimezone(dt.timezone.utc)

def get_morning(date, tz):
    return to_utc(dt.datetime.combine(date, MORNING), tz)
    
def get_evening(date, tz):
    return to_utc(dt.datetime.combine(date, EVENING), tz)

def get_data_set_for(userId, date=None):
    user = User.objects.get(pk=userId)
    
    if not date:
        date = get_default_date()
    
    if ENABLE_EVENTS:
        tz = get_timezone_for(user)
        start = get_evening(date, tz)
        end = get_morning(date, tz)
        events = get_records_for('event', userId,
            start_date_time__lte=start,
            end_date_time__gte=end,
            is_all_day_event=False
        )
    else:
        events = []
    
    if ENABLE_REMOTE_SERVICES:
        orgs = Organization.objects.all()
    else:
        orgs = []
    
    return DBDataSet(
        user,
        get_records_for('account', userId),
        get_records_for('contact', userId),
        get_records_for('lead', userId),
        get_records_for('opportunity', userId),
        events,
        orgs,
        date
    )

def get_data_sets_for(ctxs):
    return [get_data_set_for(*ctx) for ctx in ctxs]

def get_records_for(obj_name, userId, **filters):
    obj = OBJECTS[obj_name]
    Model = obj['model']
    query = Model.objects.filter(owner_id=userId, **filters)

    if 'related_fields' in obj and obj['related_fields']:
        query = query.select_related(*obj['related_fields'])
    
    return query

def has_field(record, name):
    for part in name.split('.'):
        if hasattr(record, part):
            record = getattr(record, part)
        
        if not record:
            return False
    
    return True
