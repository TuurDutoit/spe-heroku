from django.db.models import Q
from web.models import Account, Contact, Lead, Location, Route, Event
from ..common import RecordSet, DataSet
from ..util import init_matrix
import random

class DBDataSet(DataSet):
    def __init__(self, accounts, contacts, leads, events):
        self.accounts = RecordSet(accounts)
        self.contacts = RecordSet(contacts)
        self.leads = RecordSet(leads)
        self.all_ids = self.accounts.ids + self.contacts.ids + self.leads.ids
        self.total = len(self.all_ids)
        
        self.events = RecordSet(events)
        
        locations = Location.objects.filter(related_to_id__in=self.all_ids)
        self.locations = RecordSet(locations)
    
    def get_record_for_location_index(self, loc_idx):
        location = self.locations.all[loc_idx]
        return self.get_record_for_location(location)
    
    def get_record_for_location_id(self, loc_id):
        location = self.locations.map[loc_id]
        return self.get_record_for_location(location)
    
    def get_record_for_location(self, location):
        rec_set_name = location.related_to.lower() + 's'
        records = getattr(self, rec_set_name)
        return records.map[location.related_to_id]

    def get_driving_times(self):
        routes = Route.objects.filter(Q(start__in=self.locations.ids) | Q(end__in=self.locations.ids))
        driving_times = init_matrix(self.locations.total + 1)

        for route in routes:
            start_index = self.locations.ids.index(route.start_id)
            end_index = self.locations.ids.index(route.end_id)
            driving_times[start_index+1][end_index+1] = route.distance

        return driving_times

    def get_service_times(self):
        return [0] + [60*60 for _ in range(self.locations.total)]
    
    def get_penalties(self):
        return [24*60*60] * self.locations.total

    def get_locations(self):
        return self.locations.ids


def get_data_set_for(userId):
    return DBDataSet(
        get_records_for(Account, userId),
        get_records_for(Contact, userId),
        get_records_for(Lead, userId),
        get_records_for(Event, userId)
    )

def get_records_for(Model, userId):
    return Model.objects.filter(owner_id=userId)
