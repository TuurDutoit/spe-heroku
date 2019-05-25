from web.models import Recommendation
from .routes.manage import refresh_routes

def handle_change(change):
    if not change:
        return []
    if change['type'] == 'object':
        return refresh_routes(change['objectName'], change['records'], change['action'])
    if change['type'] == 'manual':
        return [change['userId']]

def remove_recommendations_for(userId):
    Recommendation.objects.filter(owner_id=userId).delete()

def insert_recommendations(recs):
    Recommendation.objects.bulk_create(recs)