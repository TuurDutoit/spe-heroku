from web.models import Account, Contact, Lead, Location, Route
from django.db.models import Q

class LocationSet:
    def __init__(self, accounts, contacts, leads):
        self.accounts = accounts
        self.account_ids = [record.pk for record in accounts]
        self.num_accounts = len(self.account_ids)
        self.contacts = contacts
        self.contact_ids = [record.pk for record in contacts]
        self.num_contacts = len(self.contact_ids)
        self.leads = leads
        self.lead_ids = [record.pk for record in leads]
        self.num_leads = len(self.lead_ids)
        self.all_ids = self.account_ids + self.contact_ids + self.lead_ids
        self.num_records = self.num_accounts + self.num_contacts + self.num_leads
        
        self.locations = Location.objects.filter(related_to_id__in=self.all_ids)
        self.location_ids = [record.pk for record in self.locations]
        self.num_locations = len(self.location_ids)
    
    @staticmethod
    def for_user(userId):
        return LocationSet(
            get_records_for(Account, userId),
            get_records_for(Contact, userId),
            get_records_for(Lead, userId)
        )

def get_records_for(Model, userId):
    return Model.objects.filter(owner_id=userId)

def get_locations_for(userId):
    return LocationSet.for_user(userId)

def get_driving_times(location_set):
    routes = Route.objects.filter(Q(start__in=location_set.location_ids) | Q(end__in=location_set.location_ids))
    driving_times = init_matrix(location_set.num_locations + 1)
    
    for route in routes:
        start_index = location_set.location_ids.index(route.start_id)
        end_index = location_set.location_ids.index(route.end_id)
        driving_times[start_index+1][end_index+1] = route.distance
    
    return driving_times

def get_meeting_times(location_set):
    return [0] + [60*60 for _ in range(location_set.num_locations)]

def init_matrix(size):
    return [[0] * size for _ in range(size)]
