from django.db import transaction
from engine.data import get_data_set_for, remove_recommendations_for, insert_recommendations
from engine.data.util import matrix_str
from engine.data.remote.util import get_timezone_for
from web.models import Recommendation, Account
from .tsp import TravellingSalesman, create_context
from app.util import env, boolean
import datetime as dt
import logging


ENABLE = {
    'account': env('REC_ACCOUNT', True, boolean),
    'opportunity': env('REC_OPPORTUNITY', True, boolean),
    'lead': env('REC_LEAD', True, boolean),
    'contact': env('REC_CONTACT', True, boolean)
}
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
    
    logger.debug('Day start: %s', day_start)
    
    logger.debug(solution)
    
    if solution.solved:
        for leg in solution.legs:
            obj_name = leg.stop.obj_name
            if obj_name in ENABLE and ENABLE[obj_name]:
                record = leg.stop.get_record()
                service_time = leg.stop.get_service_time()
                start = day_start + dt.timedelta(seconds=leg.arrival[0])
                end = start + dt.timedelta(seconds=service_time)
                
                logger.debug('Start: %s', start)
                logger.debug('End: %s', end)
                
                rec = Recommendation(
                    score = record.score,
                    reason1 = 'This %s looks promising' % obj_name,
                    service_type = leg.stop.get_service_type(),
                    service_time = service_time,
                    start_date_time = start,
                    end_date_time = end,
                    location_id = leg.stop.get_location().pk,
                    what_type = obj_name,
                    what_id = record.pk,
                    owner_id = ctx[0],
                )
                
                recs.append(rec)
    else:
        logger.warning('Not creating recommendations: solution not solved, or using a mock data set')
    
    return recs, solution
