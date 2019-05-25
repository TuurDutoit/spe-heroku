from django.db import transaction
from engine.data import get_data_set_for, remove_recommendations_for, insert_recommendations
from engine.data.util import matrix_str
from web.models import Recommendation, Account
from .tsp import TravellingSalesman, create_context
import logging

logger = logging.getLogger(__name__)

def refresh_recommendations_for(userId):
    with transaction.atomic():
        recs, solution = get_recommendations_for(userId)
        remove_recommendations_for(userId)
        insert_recommendations(recs)
    
    return recs, solution
        

def get_recommendations_for(userId):
    data = get_data_set_for(userId)
    context = create_context(data)
    tsp = TravellingSalesman(context)
    solution = tsp.run()
    recs = []
    
    header = context['nodes']
    logger.debug('\n'+matrix_str(data.get_driving_times(), header=header))
    logger.debug(solution)
    
    if solution.solved:
        for location in solution.locations:
            record = data.get_record_for_location_id(location)
            
            if isinstance(record, Account):
                recs.append(Recommendation(
                    score = record.score,
                    reason1 = 'This account looks promising',
                    account_id = record.pk,
                    owner_id = userId
                ))
    else:
        logger.warning('Not creating recommendations: solution not solved, or using a mock data set')
    
    return recs, solution
