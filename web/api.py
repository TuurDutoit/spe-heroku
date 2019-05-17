from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.serializers import serialize
from engine.recommendations import main as get_schedules
from .models import User, Account, Recommendation
from .util.endpoint import Endpoint, ModelEndpoint, RequestData, GracefulError, error, success, to_json
import json
import time


class RecalculateEndpoint(PermissionRequiredMixin, Endpoint):
    permission_required = 'web.engine_recalculate'
    http_method_names = ['post']

    def post(self, req, *args, **kwargs):
        data = RequestData(req)
        
        # Get userId from request
        try:
            userId = data.get('userId')
        except KeyError:
            raise GracefulError(error(req, 'Required parameter missing: "userId"'))
        
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

class RecommendationsEndpoint(PermissionRequiredMixin, Endpoint):
    permission_required = 'web.engine_recalculate'
    http_method_names = ['get']
    
    def get(self, req, *args, **kwargs):
        return success(get_schedules(EngineArgs()))

class EngineArgs:
    commute_time = 30
    load_min = 480
    load_max = 560
    num_workers = 98

class AccountsEndpoint(PermissionRequiredMixin, ModelEndpoint):
    permission_required = 'web.view_account'
    http_method_names = ['get']
    Model = Account
    readable_keys = ['id', 'account_number', 'is_active']
    filterable_keys = ['id', 'is_active']