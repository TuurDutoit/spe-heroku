from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.db.models import When, Case, Value, F, BooleanField
from django.forms.models import model_to_dict
from .models import User, Account, Recommendation
from .util.endpoint import Endpoint, ModelEndpoint, RequestData, GracefulError, error, success, get_loc
import json
import os

class RecalculateEndpoint(Endpoint):
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
        newRec = Recommendation(score=acct.AnnualRevenue, reason1='Annual revenue of €' + str(acct.AnnualRevenue), account=acct, owner=user)
        newRec.save()
        print(newRec)
        
        return success({
            'record': model_to_dict(newRec),
            'recordId': newRec.id,
            'url': req.build_absolute_uri('/api/engine/recommedations/' + str(newRec.id))
        })

class AccountsEndpoint(ModelEndpoint):
    http_method_names = ['get']
    Model = Account
    readable_keys = ['sf_id', 'AccountNumber']
    filterable_keys = ['sf_id']
