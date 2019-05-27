from django.db.models import Q
from web.models import Recommendation, Location, Route
from .routes.manage import refresh_routes

def handle_change(change):
    if change['type'] == 'manual':
        return [change['userId']]
    elif change['type'] == 'object':
        return refresh_routes(change['objectName'], change['records'], change['action'])
    else:
        return []

def remove_recommendations_for(userId):
    Recommendation.objects.filter(owner_id=userId).delete()

def insert_recommendations(recs):
    Recommendation.objects.bulk_create(recs)