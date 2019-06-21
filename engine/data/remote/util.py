from django.db.models import Q
from web.models import Location, Route, Organization
from pytz import timezone

ORG_ID = None

def get_record_ids(records):
    return [record.pk for record in records if record.pk != None]

def get_locations_related_to(obj_name, records, all=False):
    return get_locations_related_to_ids(obj_name, get_record_ids(records), all)

def get_locations_related_to_ids(obj_name, ids, all=False):
    query = Q(related_to=obj_name, related_to_id__in=ids)
    
    if not all:
        query = query & Q(is_valid=True)
        
    return Location.objects.filter(query)

def get_locations_related_to_map(id_map, all=False):
    query =  Q()
    
    for obj_name in id_map:
        subquery = Q(related_to=obj_name)
        
        if id_map[obj_name] != True:
            subquery = subquery & Q(related_to_id__in=id_map[obj_name])
            
        query = query | subquery
    
    if not all:
        query = query & Q(is_valid=True)
    
    return Location.objects.filter(query)

def get_locations(all=False):
    if all:
        return Location.objects.all()
    else:
        return Location.objects.filter(is_valid=True)

def get_locations_for(userId):
    return Location.objects.filter(owner_id=userId, is_valid=True)

def get_global_locations():
    return Location.objects.filter(owner_id__isnull=True)

def get_routes_for_locations(locations):
    return get_routes_for_location_ids(get_record_ids(locations))

def get_routes_for_location_ids(ids):
    return Route.objects.filter(Q(start_id__in=ids) | Q(end_id__in=ids))

def get_timezone_for(user):
    return timezone(user.time_zone_sid_key)

def get_org_id():
    if not ORG_ID:
        ORG_ID = Organization.objects.get().pk
    
    return ORG_ID
