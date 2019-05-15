from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.serializers import serialize
from .models import User, Account, Recommendation
from .util.endpoint import Endpoint, ModelEndpoint, RequestData, GracefulError, error, success
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
        
        # Wait for Heroku to sync changes
        # This usually takes 2-3 seconds
        time.sleep(5)
        
        # Fetch User and Account objects
        user = User.objects.get(id = userId)
        acct = Account.objects.all().filter(Owner = userId, AnnualRevenue__isnull = False).order_by('-AnnualRevenue').first()
        print(acct)
        
        # Delete old recommendations
        Recommendation.objects.all().filter(owner = userId).delete()
        
        # Create new recommendation
        newRec = Recommendation(
            score=max(min(acct.AnnualRevenue / 1000000, 100), 0),
            reason1='Annual revenue of €' + str(acct.AnnualRevenue),
            account=acct,
            owner=user
        )
        newRec.save()
        
        # Return a successful response
        return success({
            **json.loads(serialize('json', [newRec]))[0],
            'url': req.build_absolute_uri('/api/engine/recommedations/' + str(newRec.id))
        })


class AccountsEndpoint(PermissionRequiredMixin, ModelEndpoint):
    permission_required = 'web.view_account'
    http_method_names = ['get']
    Model = Account
    readable_keys = ['id', 'account_number', 'is_active']
    filterable_keys = ['id', 'is_active']