from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.db.models import When, Case, Value, F, BooleanField
from .models import Account
from .util.endpoint import Endpoint, ModelEndpoint, error, success, get_loc
import json
import os

class RecalculateEndpoint(Endpoint):
    http_method_names = ['post']

    def post(self, req, *args, **kwargs):
        try:
            data = json.loads(req.body)
        except json.JSONDecodeError:
            return error(req, 'Empty or malformed body.', 400)
        
        if not 'userId' in data:
            return error(req, {
                'message': 'Missing parameter: userId',
                'docs': 'request.body.userId'
            }, 400)
        
        if not type(data['userId']) == type(str()):
            return error(req, {
                'message': 'Parameter "userId" must be a string',
                'docs': 'request.body.userId',
                'location': get_loc(req.body, '"userId"')
            }, 400)
            
        return success(data)

class AccountsEndpoint(ModelEndpoint):
    http_method_names = ['get']
    Model = Account
    readable_keys = ['sf_id', 'AccountNumber']