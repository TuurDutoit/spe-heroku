from web.models import Account, Contact, Lead, Opportunity, Event, Organization

EXTRA_FIELDS = ['owner_id']
ADDRESS_SUBFIELDS = ['street', 'city', 'state', 'postal_code', 'country']
DEFAULT_SETTINGS = {
    'extra_fields': EXTRA_FIELDS,
    'currency_fields': [],
    'phone_fields': [],
    'email_fields': [],
    'has_locations': True,
    'is_global': False, # Global records don't have a specific owner -> routes to/from everywhere are calculated
    'is_office': False, # Whether these records can be used as offices for remote stops
    'is_fixed': False, # Whether these records are existing fixed events
    'parent': None, # The name of the parent object, if any. Locations will be taken from that object instead
    'related_fields': None, # ForeignKey fields that should be populated in a DataSet
    'loc_id_field': 'pk' # The name of the field that is referenced by Location#related_to_id
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
    'account': basic_model(
        Account,
        ['billing', 'shipping'],
        currency_fields=['annual_revenue'],
        phone_fields=['phone'],
    ),
    'contact': basic_model(
        Contact,
        ['mailing', 'other'],
        phone_fields=['assistant_phone', 'home_phone', 'mobile_phone', 'phone'],
        email_fields=['email'],
    ),
    'lead': basic_model(
        Lead,
        [''],
        currency_fields=['annual_revenue'],
        phone_fields=['mobile_phone', 'phone'],
        email_fields=['email'],
    ),
    'opportunity': basic_model(
        Opportunity,
        [],
        has_locations=False,
        currency_fields=['amount', 'expected_revenue'],
        parent='account',
        loc_id_field='account_id',
        related_fields=['account'],
        phone_fields=['account.phone'],
    ),
    'event': {
        **DEFAULT_SETTINGS,
        'model': Event,
        'components': {
            '': ['location']
        },
        'extra_fields': ['what_id', 'who_id', 'account_id'],
        'is_fixed': True,
    },
    'organization': basic_model(
        Organization,
        [''],
        is_global=True,
        is_office=True,
        extra_fields=[],
    )
}


for obj_name in OBJECTS:
    obj = OBJECTS[obj_name]
    address_fields = []

    for component in obj['components']:
        address_fields += obj['components'][component]

    extra_fields = obj.get('extra_fields', [])
    obj['relevant_fields'] = address_fields + extra_fields

    if not 'name' in obj:
        obj['name'] = obj['model']._meta.model_name
    
    if not 'label' in obj:
        obj['label'] = obj['model']._meta.verbose_name
