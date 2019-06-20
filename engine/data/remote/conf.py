from web.models import Account, Contact, Lead, Event, Organization

EXTRA_FIELDS = ['owner_id']
ADDRESS_SUBFIELDS = ['street', 'city', 'state', 'postal_code', 'country']
DEFAULT_SETTINGS = {
    'extra_fields': EXTRA_FIELDS,
    'is_global': False,
    'is_office': False,
}

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

def basic_model(Model, address_fields, **kwargs):
    return {
        'model': Model,
        'components': get_address_map(address_fields),
        **DEFAULT_SETTINGS,
        **kwargs,
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
    },
    'organization': basic_model(Organization, [''], is_global=True, is_office=True, extra_fields=[])
}


for obj_name in OBJECTS:
    obj = OBJECTS[obj_name]
    address_fields = []

    for component in obj['components']:
        address_fields += obj['components'][component]

    extra_fields = obj.get('extra_fields', [])
    obj['relevant_fields'] = address_fields + extra_fields
