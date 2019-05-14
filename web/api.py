from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.db.models import When, Case, Value, F, BooleanField
from django.core.serializers import serialize
from django.contrib.auth.mixins import PermissionRequiredMixin
from .models import User, Account, Recommendation
from .util.endpoint import Endpoint, ModelEndpoint, RequestData, GracefulError, error, success, get_loc
import json
import os

class RecalculateEndpoint(PermissionRequiredMixin, Endpoint):
    permission_required = 'web.engine_recalculate'
    http_method_names = ['post']

    def post(self, req, *args, **kwargs):
        data = RequestData(req)
        
        try:
            userId = data.get('userId')
        except KeyError:
            raise GracefulError(error(req, 'Required parameter missing: "userId"'))
        
        user = User.objects.get(sf_id = userId)
        acct = Account.objects.all().filter(Owner = userId, AnnualRevenue__isnull = False).order_by('-AnnualRevenue').first()
        Recommendation.objects.all().filter(owner = userId).delete()
        newRec = Recommendation(
            score=max(min(acct.AnnualRevenue / 1000000, 100), 0),
            reason1='Annual revenue of €' + str(acct.AnnualRevenue),
            account=acct,
            owner=user
        )
        newRec.save()
        print(newRec)
        
        return success({
            **json.loads(serialize('json', [newRec]))[0],
            'url': req.build_absolute_uri('/api/engine/recommedations/' + str(newRec.id))
        })

class AccountsEndpoint(PermissionRequiredMixin, ModelEndpoint):
    permission_required = 'web.view_account'
    http_method_names = ['get']
    Model = Account
    readable_keys = ['sf_id', 'AccountNumber']
    filterable_keys = ['sf_id']
