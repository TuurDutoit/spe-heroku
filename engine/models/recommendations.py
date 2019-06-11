from django.db import transaction
from engine.data import get_data_set_for, remove_recommendations_for, insert_recommendations
from engine.data.util import matrix_str
from web.models import Recommendation, Account
from .tsp import TravellingSalesman, create_context
import logging

logger = logging.getLogger(__name__)

def refresh_recommendations_for(ctx):
    with transaction.atomic():
        recs, solution = get_recommendations_for(ctx)
        remove_recommendations_for(ctx[0])
        insert_recommendations(recs)
    
    return recs, solution
        

def get_recommendations_for(ctx):
    data = get_data_set_for(ctx[0], ctx[1])
    logger.debug(data.event.total)
    context = create_context(data)
    tsp = TravellingSalesman(context)
    solution = tsp.run()
    recs = []
    
    logger.debug(solution)
    
    if solution.solved:
        for leg in solution.legs:
            if leg.stop.obj_name == 'account':
                record = leg.stop.record
                rec = Recommendation(
                    score = record.score,
                    reason1 = 'This account looks promising',
                    what_type = 'account',
                    what_id = record.pk,
                    owner_id = record.owner_id
                )
                
                recs.append(rec)
    else:
        logger.warning('Not creating recommendations: solution not solved, or using a mock data set')
    
    return recs, solution
