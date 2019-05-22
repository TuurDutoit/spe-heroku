from django.contrib.auth.mixins import PermissionRequiredMixin
from engine.models.schedule import main as get_schedules
from engine.models.recommendations import refresh_recommendations_for
from engine.data.manage import handle_change
from .models import User, Account, Event, Recommendation
from .util import to_json
from .util.endpoint import Endpoint, ModelEndpoint
from .util.request import RequestData
from .util.response import error, success


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
            account_id=acct.id,
            owner_id=user.id
        )
        newRec.save()
        
        # Return a successful response
        return success({
            **to_json(newRec),
            'url': req.build_absolute_uri('/api/engine/recommedations/' + str(newRec.id))
        })

class RecalculateEndpoint(PermissionRequiredMixin, Endpoint):
    permission_required = 'web.engine_recalculate'
    http_method_names = ['post']
    
    def post(self, req, *args, **kwargs):
        data = RequestData(req)
        userId = data.get('userId', graceful=True)
        change = data.getdict('change', default=None)
        
        # Update caches
        handle_change(change)
        
        # Recalculate recommendations
        refresh_recommendations_for(userId)
        
        return success()

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
    readable_keys = ['id', 'score', 'reason1', 'reason2', 'reason3', 'account_id', 'owner_id']