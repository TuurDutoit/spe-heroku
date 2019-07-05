from django.contrib.auth.mixins import PermissionRequiredMixin
from engine.models.schedule import main as get_schedules
from engine.models.recommendations import refresh_recommendations_for
from engine.data import handle_change, reset
from .models import User, Account, Event, Recommendation
from .util import to_json
from .util.endpoint import Endpoint, ModelEndpoint
from .util.request import RequestData
from .util.response import error, success
import logging

logger = logging.getLogger(__name__)


class OldRecalculateEndpoint(PermissionRequiredMixin, Endpoint):
    permission_required = 'web.engine_recalculate'
    http_method_names = ['post']

    def post(self, req, *args, **kwargs):
        data = RequestData(req)
        
        # Get userId from request
        userId = data.get('userId', graceful=True)
        
        # Fetch User and Account objects
        user = User.objects.get(id = userId)
        acct = Account.objects.all().filter(owner = userId, annual_revenue__isnull = False).order_by('-annual_revenue').first()
        
        # Delete old recommendations
        Recommendation.objects.all().filter(owner_id = userId).delete()
        
        # Create new recommendation
        newRec = Recommendation(
            score=max(min(acct.annual_revenue / 1000000, 100), 0),
            reason1='Annual revenue of €' + str(acct.annual_revenue),
            what_type='account',
            what_id=acct.id,
            owner_id=user.id
        )
        newRec.save()
        
        # Return a successful response
        return success({
            **to_json(newRec),
            'url': req.build_absolute_uri('/api/engine/recommedations/' + str(newRec.id))
        })

class ChangeEndpoint(PermissionRequiredMixin, Endpoint):
    permission_required = 'web.engine_recalculate'
    http_method_names = ['post']
    
    def post(self, req, *args, **kwargs):
        data = RequestData(req)
        change = data.getdict('change', default=None)
        user_ids = handle_change(change)
        success(user_ids)

class RecalculateEndpoint(PermissionRequiredMixin, Endpoint):
    permission_required = 'web.engine_recalculate'
    http_method_names = ['post']
    
    def post(self, req, *args, **kwargs):
        data = RequestData(req)
        change = data.getdict('change', default=None)
        
        # Update locations, routes, etc.
        ctxs = handle_change(change)
        logger.debug(ctxs)
        
        # Recalculate recommendations
        results = []
        
        for ctx in set(ctxs):
            recs, solution = refresh_recommendations_for(ctx)
            results.append({
                'userId': ctx[0],
                'date': ctx[1],
                'recommendations': [to_json(rec) for rec in recs],
                'solution': solution.__dict__,
                'schedule': str(solution)
            })
        
        return success(results)

class AccountsEndpoint(PermissionRequiredMixin, ModelEndpoint):
    permission_required = 'web.view_account'
    http_method_names = ['get']
    Model = Account
    readable_keys = ['id', 'account_number', 'is_active']
    filterable_keys = ['id', 'is_active']


class EventsEndpoint(PermissionRequiredMixin, ModelEndpoint):
    permission_required = 'web.view_event'
    http_method_names = ['get']
    Model = Event
    readable_keys = ['id', 'start_date_time', 'end_date_time', 'subject', 'location', 'who', 'what']

class RecommendationsEndpoint(PermissionRequiredMixin, ModelEndpoint):
    permission_required = 'web.view_recommendation'
    http_method_names = ['get']
    Model = Recommendation
    readable_keys = ['id', 'score', 'reason1', 'reason2', 'reason3', 'what_type', 'what_id', 'owner_id']
