from django.db.models import Q
from web.models import User, Recommendation, Location, Route, Account, Contact, Lead, Opportunity, Event
from .routes.manage import refresh_routes
from app.util import get_default_date
from dateutil.parser import parse
import datetime

def handle_change(change):
    if change['type'] == 'manual':
        userId = change['userId']
        
        if 'date' in change:
            datestr = change['date']
            date = parse(datestr)
        else:
            date = get_default_date()
            
        return [(userId, date)]
    elif change['type'] == 'object':
        return refresh_routes(change['objectName'], change['records'], change['action'])
    else:
        return []

def remove_recommendations(ctx):
    Recommendation.objects.filter(owner_id=ctx[0], start_date_time__date=ctx[1]).delete()

def insert_recommendations(recs):
    Recommendation.objects.bulk_create(recs)

def delete_everything():
    Recommendation.objects.all().delete()
    Route.objects.all().delete()
    Location.objects.all().delete()

def recalc_all(Model, **filters):
    name = Model._meta.model_name
    records = Model.objects.all()

    if filters and len(filters):
        records = records.filter(**filters)

    record_ids = [record.pk for record in records]
    return handle_change({
        'type': 'object',
        'action': 'insert',
        'objectName': name,
        'records': record_ids
    })

def recalc_everything(filters):
    today = datetime.datetime.combine(datetime.date.today(), datetime.time(0))
    all_ctxs = []

    all_ctxs += recalc_all(Account, **filters.get('all', {}), **filters.get('account', {}))
    all_ctxs += recalc_all(Contact, **filters.get('all', {}), **filters.get('contact', {}))
    all_ctxs += recalc_all(Lead, **filters.get('all', {}), **filters.get('lead', {}))
    all_ctxs += recalc_all(Opportunity, **filters.get('all', {}), **filters.get('opportunity', {}))
    all_ctxs += recalc_all(Event, start_date_time__gte=today, **filters.get('all', {}), **filters.get('event', {}))

    return all_ctxs

def reset(filters={}):
    delete_everything()
    return recalc_everything(filters)
