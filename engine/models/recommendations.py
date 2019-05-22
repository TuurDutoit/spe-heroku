from django.db import transaction
from engine.data import get_data_set_for
from engine.data.manage import remove_recommendations_for, insert_recommendations
from web.models import Recommendation, Account
from .tsp import TravellingSalesman, create_context

def refresh_recommendations_for(userId):
    with transaction.atomic():
        recs = get_recommendations_for(userId)
        remove_recommendations_for(userId)
        insert_recommendations(recs)
    
    return recs
        

def get_recommendations_for(userId):
    data = get_data_set_for(userId)
    tsp = TravellingSalesman.for_data_set(data)
    solution = tsp.run()
    recs = []
    
    if solution.solved:
        for location in solution.locations:
            record = data.get_record_for_location(location)
            
            if isinstance(record, Account):
                recs.append(Recommendation(
                    score = record.score,
                    reason1 = 'This account looks promising',
                    account_id = record.pk,
                    owner_id = userId
                ))
    
    return recs
