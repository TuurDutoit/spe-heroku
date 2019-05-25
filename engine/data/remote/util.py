from django.db.models import Q
from web.models import Location, Route

def get_record_ids(records):
    return [record.pk for record in records if record.pk != None]

def get_locations_related_to(obj_name, records):
    return get_locations_related_to_ids(obj_name, get_record_ids(records))

def get_locations_related_to_ids(obj_name, ids):
    return Location.objects.filter(
        related_to=obj_name,
        related_to_id__in=ids,
        is_valid=True
    )

def get_locations_related_to_map(id_map):
    query =  Q()
    for obj_name in id_map:
        query = query | Q(related_to=obj_name, related_to_id__in=id_map[obj_name])
    
    return Location.objects.filter(query)

def get_locations_for(userId):
    return Location.objects.filter(owner_id=userId, is_valid=True)

def get_routes_for_locations(locations):
    return get_routes_for_location_ids(get_record_ids(locations))

def get_routes_for_location_ids(ids):
    return Route.objects.filter(Q(start_id__in=ids) | Q(end_id__in=ids))