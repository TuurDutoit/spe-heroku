from web.models import Account, Location, Route
import googlemaps
import os

maps = googlemaps.Client(key=os.environ['MAPS_API_KEY'])

ADDRESS_COMPONENTS = ['street', 'city', 'state', 'postal_code', 'country']
OBJECTS = {
    'account': {
        'model': Account,
        'address_fields': ['billing', 'shipping']
    }
}


def refresh_routes_for(obj_name, ids):
    # Get relevant Django Model
    obj = OBJECTS[obj_name]
    model = obj.model

    # Fetch relevant records (only relevant fields)
    fields = get_address_fields(obj['address_fields'])
    records = model.objects.filter(pk__in=ids).only(*fields)

    # Fetch Location records
    current_locations = Location.objects.filter(
        related_to=obj_name, related_to_id__in=[rec.pk for rec in records])
    other_locations = Location.objects.exclude(
        pk__in=[rec.pk for rec in current_locations])

    print('Refresh routes for: ' + str(records))


def get_address_fields(names):
    fields = []

    for name in names:
        for component in ADDRESS_COMPONENTS:
            fields.append(name + '_' + component)

    return fields
