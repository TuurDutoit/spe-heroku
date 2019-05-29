from web.models import Account, Contact, Lead, Event

BASE_FIELDS = ['owner_id']
ADDRESS_SUBFIELDS = ['street', 'city', 'state', 'postal_code', 'country']

def get_address_fields(name):
    fields = []
    prefix = name + '_' if name else ''

    for subfield in ADDRESS_SUBFIELDS:
        fields.append(prefix + subfield)

    return fields

def get_address_map(components):
    m = {}

    for component in components:
        m[component] = get_address_fields(component)

    return m

def basic_model(Model, address_fields):
    return {
        'model': Model,
        'components': get_address_map(address_fields),
    }

OBJECTS = {
    'account': basic_model(Account, ['billing', 'shipping']),
    'contact': basic_model(Contact, ['mailing', 'other']),
    'lead': basic_model(Lead, ['']),
    'event': {
        'model': Event,
        'components': {
            '': ['location']
        },
        'extra_fields': ['what_id', 'who_id', 'account_id'],
    }
}


for obj_name in OBJECTS:
    obj = OBJECTS[obj_name]
    address_fields = []

    for component in obj['components']:
        address_fields += obj['components'][component]

    extra_fields = obj.get('base_fields', [])
    obj['relevant_fields'] = BASE_FIELDS + extra_fields + address_fields
