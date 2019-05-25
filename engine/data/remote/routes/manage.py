from django.db.models import Q
from web.models import Account, Location, Route
from .maps import geocode, distance_matrix
from ..util import get_locations_for, get_locations_related_to_ids, get_routes_for_locations, get_record_ids
import logging

logger = logging.getLogger(__name__)

ADDRESS_SUBFIELDS = ['street', 'city', 'state', 'postal_code', 'country']
OBJECTS = {
    'account': {
        'model': Account,
        'components': ['billing', 'shipping'],
        'base_fields': ['owner_id']
    }
}


def refresh_routes(obj_name, ids, action):
    if action == 'delete':
        return action_delete(obj_name, ids)
    elif action == 'insert' or action == 'update':
        return action_upsert(obj_name, ids)
    else:
        logger.warning('Unknown action: ' + action)
        return []


def action_delete(obj_name, ids):
    locations = get_locations_related_to_ids(obj_name, ids).only('owner_id')
    user_ids = [loc.owner_id for loc in locations]
    
    # Routes are deleted automatically because of the CASCADE policy
    locations.delete()

    return user_ids


def upsert_location(record, component, address, existing_locations, obj_name):
    if (component, record.pk) in existing_locations:
        location = existing_locations[(component, record.pk)]
        
        # If the address was changed, update the location and return it, so its related Routes can be updated
        # If it wasn't changed, return None. This way, related Routes won't be updated
        #   (except for routes related to this location and one that was updated, of course)
        if location.address != address:
            location.address = address
            return location, False
    else:
        return Location(
            address=address,
            related_to=obj_name,
            related_to_component=component,
            related_to_id=record.pk,
            owner_id=record.owner_id,
            is_valid=True  # Set to True for now, we'll correct this after a sanity check and geocoding
        ), True

def action_upsert(obj_name, ids):
    existing_locations = create_location_map(get_locations_related_to_ids(obj_name, ids))
    locations, user_ids = init_locations(obj_name, ids, upsert_location, existing_locations, obj_name)
    
    invalid_locations = locations['invalid']
    valid_locations = []
    routes_to_create = []
    
    for userId in user_ids:
        maybe_valid_locations = locations['maybe_valid_by_owner'][userId]
        other_locations = get_other_locations(userId, maybe_valid_locations)
        all_locations = maybe_valid_locations + list(other_locations)
        route_map = get_route_map(all_locations)
        
        update_routes(maybe_valid_locations, other_locations, route_map,
                      routes_to_create, valid_locations, invalid_locations)
    
    # Mark all (in)valid locations
    # We can only do this after the loop above, because it can add locations to invalid_locations
    # depending on the results of the geocoding
    # We don't save them here, because they might have to be created,
    # which is more efficient with a single bulk_create call
    for loc in invalid_locations:
        loc.is_valid = False
    
    for loc in valid_locations:
        is_valid = True
    
    # Save all Locations that have changed
    for loc in locations['to_update']:
        loc.save()
    
    # Create new Locations
    # This requires the new PKs to be populated, which is only supported in PostgreSQL!
    Location.objects.bulk_create(locations['to_create'])
    
    # Even though PKs are populated on the Location object above,
    # the start/end locations were added earlier, when the PKs for the new Locations weren't available yet
    # Let's fix that here
    for route in routes_to_create:
        route.start_id = route.start.pk
        route.end_id = route.end.pk
    
    # Create new routes, and delete ones related to invalid locations
    # The ones that need updating have been save()d in update_routes
    Route.objects.bulk_create(routes_to_create)
    delete_routes_for(locations['invalid'])


# Given a number of new or updated locations (maybe_valid_locations)
# and some existing unchanged ones (other_locations),
# fetch a distance matrix and update or create routes accordingly
#
# Routes that are found in existing_routes will be updated,
# otherwise a new Route will be added to routes_to_create
#
# Locations will be added to either valid_locations or invalid_locations, depending on the geocoding results
# This essentially splits maybe_valid_locations into 2: valid or invalid
# 
# Notes:
#  - Invalid locations are added to invalid_locations, but are not updated and stay in the maybe_valid_locations list
#     No routes will be created for them, however
#  - Updates to routes are done immediately, but routes that need to be created are added to routes_to_create
#     This allows the use of bulk_create
def update_routes(maybe_valid_locations, other_locations, existing_routes,
                  routes_to_create, valid_locations, invalid_locations):
    all_locations = maybe_valid_locations + list(other_locations)
    all_addresses = [loc.address for loc in all_locations]
    num_updated_locations = len(maybe_valid_locations)
    num_locations = len(all_locations)

    # Get distance matrix for all locations, both the ones we just created or updated
    # and existing unchanged ones
    distances, valid = distance_matrix(all_addresses, num_updated_locations)

    # Split maybe_valid_locations into valid_locations and invalid_locations
    for i in range(num_updated_locations):
        loc = maybe_valid_locations[i]
        if valid[i]:
            valid_locations.append(loc)
        else:
            invalid_locations.append(loc)

    # Create or update a route for each element in the distance matrix, if required
    for i in range(num_locations):
        for j in range(num_locations):
            d = distances[i][j]
            # Don't create/update routes:
            # - with the same start and end location
            # - with an invalid start or end location
            # - between two locations that weren't updated or created
            if i != j and d != None and (i < num_updated_locations or j < num_updated_locations):
                start = all_locations[i]
                end = all_locations[j]
                
                # Don't enable this check yet, as the TSP model doesn't support it yet
                """
                # Also don't create routes from/to the same record (but different component)
                if start.related_to_id == end.related_to_id:
                    continue
                """

                # If a route already exists, update it (if needed)
                if (start.pk, end.pk) in existing_routes:
                    route = existing_routes[(start.pk, end.pk)]
                    if route.distance != d:
                        route.distance = d
                        route.save()
                # Otherwise, create one
                # but don't save it yet: this allows us to use bulk_create when we're finished
                else:
                    routes_to_create.append(Route(
                        start=start,
                        end=end,
                        distance=d
                    ))


# Creates or updates Locations for the affected records
# These are sorted two times (so every location is included in 2 lists):
#  - Based on validity:
#     - invalid_locations: locations with an empty address, not worth passing to distance_matrix
#     - maybe_valid_locations: locations with an address, to be passed to distance_matrix
#        These can still turn out to be invalid though!
#  - Based on update/create:
#     - locations_to_create: locations that don't exist yet in the database
#     - locations_to_update: locations that do exist already
# It also extracts the userId's of the affected users
# The actual creation of new Locations or retrieval of existing ones is done in a callback
def init_locations(obj_name, ids, create_or_update_location, *cb_extras):
    obj = OBJECTS[obj_name]
    records = get_records(obj, ids)
    maybe_valid_locations_by_owner = {}
    invalid_locations = []
    locations_to_update = []
    locations_to_create = []
    user_ids = set()
    
    # For each Address compound field of each record...
    for record in records:
        userId = record.owner_id

        if not userId in user_ids:
            user_ids.add(userId)
            maybe_valid_locations_by_owner[userId] = []

        maybe_valid_locations = maybe_valid_locations_by_owner[userId]

        for component in obj['components']:
            # Format the address and get a Location object from the callback
            address = get_address(record, component)
            res = create_or_update_location(record, component, address, *cb_extras)
            
            # Location == None means that it wasn't changed,
            # so we don't include it in the locations to update/create routes for
            if res:
                (location, create) = res
                if location.address and location.address.strip():
                    # The address is not empty, so let's try to process it
                    maybe_valid_locations.append(location)
                else:
                    # The address is empty, don't even try to create routes
                    invalid_locations.append(location)
                
                if create:
                    # This location needs to be created (e.g. with bulk_create())
                    locations_to_create.append(location)
                else:
                    # This location needs to be updated (e.g. with save())
                    locations_to_update.append(location)
    
    locations = {
        'maybe_valid_by_owner': maybe_valid_locations_by_owner,
        'invalid': invalid_locations,
        'to_create': locations_to_create,
        'to_update': locations_to_update
    }
    return locations, user_ids



def get_other_locations(userId, locations):
    return get_locations_for(userId).exclude(
            pk__in=get_record_ids(locations)
        )

def create_location_map(locations):
    m = dict()
    
    for loc in locations:
        m[(loc.related_to_component, loc.related_to_id)] = loc
    
    return m
    
def get_records(obj, ids):
    return obj['model'].objects.filter(pk__in=ids).only(*obj['relevant_fields'])

def get_route_map(locations):
    routes = get_routes_for_locations(locations)
    m = dict()
    
    for route in routes:
        m[(route.start_id, route.end_id)] = route
    
    return m

def delete_routes_for(locations):
    get_routes_for_locations(locations).delete()

def get_address(record, component):
    parts = []

    for field in ADDRESS_SUBFIELDS:
        part = getattr(record, component + '_' + field)
        if part and part.strip():
            parts.append(part)

    return ', '.join(parts)

def get_address_fields(components):
    fields = []

    for name in components:
        for subfield in ADDRESS_SUBFIELDS:
            fields.append(name + '_' + subfield)

    return fields


for obj_name in OBJECTS:
    obj = OBJECTS[obj_name]
    obj['address_fields'] = get_address_fields(obj['components'])
    obj['relevant_fields'] = obj['base_fields'] + obj['address_fields']
