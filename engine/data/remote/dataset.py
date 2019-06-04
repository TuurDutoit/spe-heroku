from django.db.models import Q
from web.models import User, Account, Contact, Lead, Opportunity, Location, Route, Event
from .conf import OBJECTS
from .util import get_locations_related_to_map, get_routes_for_location_ids, get_timezone_for
from ..util import init_matrix, map_by, get_deep, find_deep
from ..common import RecordSet, DataSet
from pytz import timezone
import random
import datetime as dt
import logging

logger = logging.getLogger(__name__)

SERVICES = [
    { 'type': 'meeting', 'time': 1 * 60 * 60 }
]
BASIC_OBJECTS = ['account', 'contact', 'lead', 'opportunity']
PENALTY = 24*60*60
MORNING = dt.time(9, 0, 0, 0)
EVENING = dt.time(18, 0, 0, 0)
DEFAULT_DRIVING_TIME = 30 * 60

class DBDataSet(DataSet):
    def __init__(self, user, accounts, contacts, leads, opportunities, events, date):
        self.user = user
        self.account = RecordSet(accounts)
        self.contact = RecordSet(contacts)
        self.lead = RecordSet(leads)
        self.opportunity = RecordSet(opportunities)
        self.event = RecordSet(events)
        self.stops = []
        
        self._fetch_locations()
        self._fetch_routes()
        self._create_basic_stops()
        self._create_existing_stops(date)
        
        logger.debug('All stops: %s' % [
            '%s: %s/%s/%d' % (
                stop.obj_name,
                stop.record.pk,
                stop.location.related_to_component if stop.location else '<empty>',
                stop.record.score if hasattr(stop.record, 'score') else -1
            )
            for stop in self.stops
        ])
    
    def _fetch_locations(self):
        # IDs of the records we have to fetch locations for
        id_map = {
            'account': set(self.account.ids),
            'contact': set(self.contact.ids),
            'lead': set(self.lead.ids),
            'event': set(self.event.ids)
        }
        
        # Opportunities get their locations from related Accounts
        for opp in self.opportunity.all:
            if opp.account_id:
                id_map['account'].add(opp.account_id)
        
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
        for obj_name in BASIC_OBJECTS:
            components_src = 'account' if obj_name == 'opportunity' else obj_name
            components = OBJECTS[components_src]['components']
            record_set = getattr(self, obj_name)
            
            for record in record_set.all:
                for component in components:
                    if obj_name == 'opportunity':
                        path = ('account', record.account_id, component)
                    else:
                        path = (obj_name, record.pk, component)
                    
                    location = get_deep(self.location_map, path, default=None)
                    
                    for service in SERVICES:
                        self.stops.append(BasicStop(
                            obj_name = obj_name,
                            record = record,
                            service = service,
                            location = location,
                            penalty = record.score * PENALTY / 100,
                        ))
    
    def _create_existing_stops(self, date):
        tz = self.timezone = get_timezone_for(self.user)
        
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
                start = dt.datetime.combine(date, MORNING)

            if end.date() != date or end.time() > EVENING:
                end = dt.datetime.combine(date, EVENING)

            service_time = (end - start).total_seconds()
            time_offset = tz.localize(dt.datetime.combine(dt.date.today(), MORNING))
            start_secs = ((start - time_offset).total_seconds())
            time_window = (start_secs, start_secs)
            
            self.stops.append(BasicStop(
                obj_name = 'event',
                record = event,
                service = { 'type': event.event_subtype, 'time': service_time },
                location = location,
                penalty = None,
                time_window = time_window,
                is_existing = True
            ))
    
    def get_stops(self):
        return self.stops
        
    def get_driving_time(self, from_stop, to_stop):
        start_loc = from_stop.get_location()
        end_loc = to_stop.get_location()
        driving_time = DEFAULT_DRIVING_TIME
        
        if start_loc and end_loc:
            route = get_deep(self.route_map, (start_loc.pk, end_loc.pk), default=None)
            if route:
                driving_time = route.distance
        
        return driving_time
    
    def get_service_time(self, stop):
        return stop.get_service_time()
    
    def get_penalty(self, stop):
        return stop.get_penalty()
    
    def get_time_window(self, stop):
        return stop.get_time_window()
            

class BasicStop:
    def __init__(self, **kwargs):
        self.obj_name = kwargs.get('obj_name')
        self.record = kwargs.get('record')
        self.service_type = kwargs.get('service')['type']
        self.service_time = kwargs.get('service')['time']
        self.location = kwargs.get('location')
        self.penalty = kwargs.get('penalty', None)
        self.time_window = kwargs.get('time_window', None)
        self.is_existing = kwargs.get('is_existing', False)
        
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
    
    @property
    def __dict__(self):
        return {
            **{
                key: getattr(self, key)
                for key in ['obj_name', 'service_type', 'service_time', 'penalty', 'time_window', 'is_existing']
            },
            'record_id': self.record.pk,
            'location_id': self.location.pk if self.location else None,
            'location_address': self.location.address if self.location else None
        }
    
    def __repr__(self):
        return str({
            key: getattr(self, key)
            for key in ['obj_name', 'record', 'service_type', 'service_time', 'penalty', 'location', 'time_window', 'is_existing']
        })

# Converts a naive datetime object that is supposed to be in timezone <tz> to a UTC datetime 
def to_utc(date, tz):
    return tz.localize(date).astimezone(dt.timezone.utc)

def get_morning(date):
    return dt.datetime.combine(date, MORNING)
    
def get_evening(date):
    return dt.datetime.combine(date, EVENING)

def get_data_set_for(userId, date=dt.date.today()):
    user = User.objects.get(pk=userId)
    tz = get_timezone_for(user)
    start = to_utc(get_evening(date), tz)
    end = to_utc(get_morning(date), tz)
    
    return DBDataSet(
        user,
        get_records_for(Account, userId),
        get_records_for(Contact, userId),
        get_records_for(Lead, userId),
        get_records_for(Opportunity, userId),
        get_records_for(Event, userId,
            start_date_time__lte=start,
            end_date_time__gte=end,
            is_all_day_event=False
        ),
        date
    )

def get_records_for(Model, userId, **filters):
    return Model.objects.filter(owner_id=userId, **filters)
