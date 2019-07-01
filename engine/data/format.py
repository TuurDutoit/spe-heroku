from django.db import models
from app.util import env, DAY
from functools import partial
import datetime as dt
import humanize

CURRENCY_SYMBOL = env('CURRENCY', '€')
NO_MSG = '{field} is not set'
ACTIVITY_MSGS = {
    'never': "Has never been {verb}",
    'past': "Hasn't been {verb} {in}",
    'today': "Was {verb} today",
    'future': "Is set to be {verb} {in}",
}
SLA_MSGS = {
    'past': "SLA expired {ago}",
    'future': "SLA expires {in}",
}
EMAIL_MSGS = {
    'never': "No bounced emails",
    'past': "Last bounced email was {ago}",
    'today': "Last bounced email was today",
    'future': "Last bounced email {in}",
}
OPP_CLOSE_MSGS = {
    'past': "Closed {ago}",
    'future': "Closes {in}"
}
UPSELL_MSGS = {
    'Yes': 'Has the opportunity to upsell',
    'Maybe': 'Maybe has the opportunity to upsell',
    'No': 'Has no opportunity to upsell',
}
ACCOUNT_TYPES = {
    'Prospect': 'Is a prospect',
    'Customer - Direct': 'Is a direct customer',
    'Customer - Channel': 'Is a channel customer',
}
LEAD_PRIM = {
    'Yes': 'This is a primary lead',
    'No': 'This is not a primary lead',
}
OPP_TYPE = {
    'Existing Customer - Downgrade': 'For a downgrade',
    'Existing Customer - Upgrade': 'For a upgrade',
    'Existing Customer - Replacement': 'For a replacement',
    'New Customer': 'For a new customer'
}


def day_diff(date):
    if not date:
        return None
        
    if isinstance(date, dt.datetime):
        date = date.date()

    return (dt.date.today() - date).days

def get_args(value, field, obj):
    return {
        'value': value,
        'field': field.verbose_name.title(),
        'object': obj['label'].lower(),
    }

def _format(fmt, value, field, obj, **kwargs):
    return fmt.format(value, **get_args(value, field, obj), **kwargs)

def default_formatter(value, field, obj, fmt='{field} {verb} {value}', verb='is', **kwargs):
    return _format(fmt, value, field, obj, verb=verb, **kwargs)

def with_no(formatter, no_msg=NO_MSG):
    def with_no_formatter(value, field, obj):
        if value == None:
            return _format(no_msg, value, field, obj)

        return formatter(value, field, obj)

    return with_no_formatter

default_formatter_safe = with_no(default_formatter)

def safe(creator, *no_args):
    def with_no_creator(*args):
        return with_no(creator(*args), *no_args)
    
    return with_no_creator

def combine(*formatters):
    def combine_formatters(value, field, obj):
        for formatter in formatters:
            value = formatter(value, field, obj)
        
        return value

    return combine_formatters

combine_safe = safe(combine)

def format_str(fmt, **kwargs):
    def formatter(value, field, obj):
        return _format(fmt, value, field, obj, **kwargs)
    
    return formatter

format_str_safe = safe(format_str)

def format_default(*args, **kwargs):
    def formatter(value, field, obj):
        return default_formatter(value, field, obj, *args, **kwargs)
    
    return formatter

format_default_safe = safe(format_default)

def currency_formatter(value, field, obj):
    return CURRENCY_SYMBOL + humanize.intword(value)

currency_formatter_safe = with_no(currency_formatter)
currency_formatter_default = combine(currency_formatter, default_formatter)
currency_formatter_default_safe = with_no(currency_formatter_default)

def date_formatter(date, field, obj):
    if isinstance(date, dt.datetime):
        date = date.date()

    return humanize.naturalday(date)

date_formatter_safe = safe(date_formatter)

def date_formatter_default(date, field, obj):
    date_str = date_formatter(date, field, obj)
    verb = 'is' if date >= dt.date.today() else 'was'
    return format_default(date_str, field, obj, verb=verb)

date_formatter_default_safe = safe(date_formatter_default)

def format_date_cond(msgs, extra_args = {}, **kwargs):
    def formatter(date, field, obj):
        args = {}

        if date:
            diff = day_diff(date)
            args = {
                'diff': diff,
                'diff_abs': abs(diff),
                'days': str(abs(diff)) + ' days' if abs(diff) <= 30 else 'over a month',
            }
            args['ago'] = 'today' if diff == 0 else args['days'] + ' ago'
            args['in'] = 'today' if diff == 0 else 'in ' + args['days']

            if diff > 30:
                msg = msgs['past']
            elif diff > 0:
                msg = msgs['past']
            elif diff == 0:
                msg = msgs.get('today', None) or msgs['past']
            elif diff < 30:
                msg = msgs['future']
            else:
                msg = msgs['future']
        else:
            msg = msgs.get('never', 'No {field}')
        
        return _format(msg, date, field, obj, **args, **extra_args, **kwargs)
    
    return formatter

def format_last_activity(verb):
    return format_date_cond(ACTIVITY_MSGS, verb=verb)

def format_choice(choices):
    def formatter(value, field, obj):
        return choices[value]
    
    return formatter

format_choice_safe = safe(format_choice)

def format_bool(fmt):
    def formatter(value, field, obj):
        return fmt.format(no=('no' if not value else '__NO__')).replace(' __NO__', '')
    
    return formatter

format_bool_safe = safe(format_bool)

SPECIAL_FORMATS = {
    'last_activity_date': format_last_activity('contacted'),
    'last_viewed_date': format_last_activity('viewed'),
    'last_modified_date': format_last_activity('updated'),
    'last_referenced_date': format_last_activity('referenced'),
    'slaexpiration_date': format_date_cond(SLA_MSGS),
    'annual_revenue': combine_safe(currency_formatter, format_default(verb='of')),
    'industry': format_str_safe('Operates in the {} industry'),
    'number_of_employees': format_str_safe('Has {} employees'),
    'numberof_locations': format_str_safe('Has {} locations'),
    'upsell_opportunity': format_choice_safe(UPSELL_MSGS),
    'email_bounced_date': format_date_cond(EMAIL_MSGS),
    'has_open_activity': format_bool_safe('Has {no} open activities'),
    'has_overdue_task': format_bool_safe('Has {no} overdue tasks'),
    'account.type': format_choice_safe(ACCOUNT_TYPES),
    'lead.primary': format_choice_safe(LEAD_PRIM),
    'opportunity.amount': combine_safe(currency_formatter, format_str('Is worth {}')),
    'opportunity.close_date': format_date_cond(OPP_CLOSE_MSGS),
    'opportunity.type': format_choice_safe(OPP_TYPE),
    'opportunity.probability': format_str_safe('Probability is {value}%')
}

TYPE_FORMATS = [
    (models.DateField, date_formatter_default_safe),
    (models.DateTimeField, date_formatter_default_safe),
]

def get_formatter(field, obj):
    fullname = obj['name'] + '.' + field.name

    if fullname in SPECIAL_FORMATS:
        return SPECIAL_FORMATS[fullname]
    
    if field.name in obj['currency_fields']:
        return currency_formatter_default_safe
    
    if field.name in SPECIAL_FORMATS:
        return SPECIAL_FORMATS[field.name]
    
    for (field_type, formatter) in TYPE_FORMATS:
        if isinstance(field, field_type):
            return formatter
    
    return default_formatter_safe
    


def get_reason(value, field, obj):
    formatter = get_formatter(field, obj)
    return formatter(value, field, obj)
