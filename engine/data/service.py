from django.db.models import Q
from web.models import Account, Contact, Lead, Location, Route, Event
from .util import init_matrix, map_from, select, print_matrix
import random

class RecordSet:
    def __init__(self, records, key='pk'):
        self.all = records
        self.map = map_from(records)
        self.ids = select(records)
        self.total = len(records)

class DataSet:
    def __init__(self, accounts, contacts, leads, events):
        self.accounts = RecordSet(accounts)
        self.contacts = RecordSet(contacts)
        self.leads = RecordSet(leads)
        self.all_ids = self.accounts.ids + self.contacts.ids + self.leads.ids
        self.total = len(self.all_ids)
        
        self.events = RecordSet(events)
        
        locations = Location.objects.filter(related_to_id__in=self.all_ids)
        self.locations = RecordSet(locations)
    
    @staticmethod
    def for_user(userId):
        return DataSet(
            get_records_for(Account, userId),
            get_records_for(Contact, userId),
            get_records_for(Lead, userId),
            get_records_for(Event, userId)
        )
    
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
        #routes = Route.objects.filter(Q(start__in=data_set.locations.ids) | Q(end__in=data_set.locations.ids))
        driving_times = init_matrix(self.locations.total + 1)

        for i in range(1, self.locations.total + 1):
            for j in range(1, self.locations.total + 1):
                driving_times[i][j] = 0 if i == j else random.randint(0, 3*60*60)

        # for route in routes:
        #     start_index = data_set.locations.ids.index(route.start_id)
        #     end_index = data_set.locations.ids.index(route.end_id)
        #     driving_times[start_index+1][end_index+1] = route.distance

        header = [0] + self.locations.ids
        print_matrix(driving_times, hheader=header, vheader=header)
        return driving_times

    def get_service_times(self):
        return [0] + [60*60 for _ in range(self.locations.total)]
    
    def get_penalties(self):
        return [24*60*60] * self.locations.total

    def get_locations(self):
        return self.locations.all
    

def get_records_for(Model, userId):
    return Model.objects.filter(owner_id=userId)

def get_data_set_for(userId):
    return DataSet.for_user(userId)
