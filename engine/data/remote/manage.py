from web.models import Recommendation
from .routes.manage import refresh_routes_for

def handle_change(change):
    if not change:
        return
    if change['type'] == 'object':
        refresh_routes_for(change['object'], change['records'])

def remove_recommendations_for(userId):
    Recommendation.objects.filter(owner_id=userId).delete()

def insert_recommendations(recs):
    Recommendation.objects.bulk_create(recs)