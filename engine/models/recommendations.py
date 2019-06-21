from django.db import transaction, models
from engine.data import get_data_set_for, remove_recommendations_for, insert_recommendations
from engine.data.util import matrix_str
from engine.data.remote.conf import OBJECTS
from engine.data.remote.util import get_timezone_for
from web.models import Recommendation, Account
from .tsp import TravellingSalesman, create_context
from app.util import env, boolean, MINUTE
import datetime as dt
import humanize
import logging

ENABLE = {
    'account': env('REC_ACCOUNT', True, boolean),
    'opportunity': env('REC_OPPORTUNITY', True, boolean),
    'lead': env('REC_LEAD', True, boolean),
    'contact': env('REC_CONTACT', True, boolean)
}
CURRENCY_SYMBOL = env('CURRENCY', '€')

logger = logging.getLogger(__name__)

def refresh_recommendations_for(ctx):
    with transaction.atomic():
        recs, solution = get_recommendations_for(ctx)
        remove_recommendations_for(ctx[0])
        insert_recommendations(recs)
    
    return recs, solution
        

def get_recommendations_for(ctx):
    data = get_data_set_for(ctx[0], ctx[1])
    context = create_context(data)
    tsp = TravellingSalesman(context)
    solution = tsp.run()
    
    tz = get_timezone_for(data.user)
    day_start = tz.localize(data.day['start']).astimezone(dt.timezone.utc)
    recs = []
    
    logger.debug(solution)
    
    if solution.solved:
        for leg in solution.legs:
            obj_name = leg.stop.obj_name
            if obj_name in ENABLE and ENABLE[obj_name] and not OBJECTS[obj_name]['is_fixed']:
                record = leg.stop.get_record()
                service_time = leg.stop.get_service_time()
                start = day_start + dt.timedelta(seconds=leg.arrival[0])
                end = start + dt.timedelta(seconds=service_time)
                reasons = get_reasons(leg, obj_name, solution.legs)
                
                rec = Recommendation(
                    score = record.score,
                    service_type = leg.stop.get_service_type(),
                    service_time = service_time,
                    start_date_time = start,
                    end_date_time = end,
                    location_id = leg.stop.get_location().pk,
                    what_type = obj_name,
                    what_id = record.pk,
                    owner_id = ctx[0],
                    **{
                        'reason' + str(i + 1): reasons[i]
                        for i in range(min(len(reasons), 3))
                    }
                )
                
                recs.append(rec)
    else:
        logger.warning('Not creating recommendations: solution not solved')
    
    return recs, solution

def get_reasons(leg, obj_name, legs):
    obj = OBJECTS[obj_name]
    rec = leg.stop.record
    reasons = []
    
    for attr in rec.best_attrs:
        field = get_field(obj['model'], attr)
        label = field.verbose_name.capitalize()
        value = getattr(rec, attr)
        formatted = format_field(value, field, obj)
            
        reasons.append('%s %s' % (label, formatted))
    
    return reasons

def format_date(date):
    if not date:
        return 'was never'
    elif isinstance(date, dt.datetime):
        date = date.date()
    
    fmt = 'was %s' if date < dt.date.today() else 'is %s'
    return fmt % (humanize.naturalday(date),)

FIELD_FORMATS = [
    (models.DateField, format_date),
    (models.DateTimeField, format_date),
]

def format_field(value, field, obj):
    if field.name in obj['currency_fields']:
        return 'is ' + CURRENCY_SYMBOL + str(value)
    
    for (field_type, formatter) in FIELD_FORMATS:
        if isinstance(field, field_type):
            return formatter(value)
    
    return 'is ' + str(value)

def get_field(Model, field_name):
    return list(filter(lambda field: field.name == field_name, Model._meta.fields))[0]
