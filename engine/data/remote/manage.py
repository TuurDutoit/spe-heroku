from django.db.models import Q
from web.models import User, Recommendation, Location, Route
from .routes.manage import refresh_routes
from dateutil.parser import parse
import datetime

def handle_change(change):
    if change['type'] == 'manual':
        userId = change['userId']
        
        if 'date' in change:
            datestr = change['date']
            date = parse(datestr)
        else:
            date = datetime.date.today()
            
        return [(userId, date)]
    elif change['type'] == 'object':
        return refresh_routes(change['objectName'], change['records'], change['action'])
    else:
        return []

def remove_recommendations_for(userId):
    Recommendation.objects.filter(owner_id=userId).delete()

def insert_recommendations(recs):
    Recommendation.objects.bulk_create(recs)