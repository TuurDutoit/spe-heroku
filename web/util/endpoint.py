from django.views.generic import View
from django.core.exceptions import FieldDoesNotExist
from .request import RequestData
from .response import error
import json
import logging

logger = logging.Logger(__name__)

class Endpoint(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            return super(Endpoint, self).dispatch(request, *args, **kwargs)
        except GracefulError as e:
            return e.response
        except json.JSONDecodeError as e:
            return error(request, 'Empty or malformed body.', 400)
        except Exception as e:
            logger.exception('Exception: %s', str(e))
            return error(request, 'Something went wrong handling this request')

class ModelEndpoint(Endpoint):
    readable_keys = []
    writeable_keys = None
    filterable_keys = None
    orderable_keys = None
    Model = None
    
    def __init__(self):
        if self.writeable_keys == None:
            self.writeable_keys = self.readable_keys
        if self.filterable_keys == None:
            self.filterable_keys = self.readable_keys
        if self.orderable_keys == None:
            self.orderable_keys = self.readable_keys
    
    def get(self, request, *args, **kwargs):
        data = RequestData(request)
        query = self.Model.objects.all()
        fields = self.readable_keys
        
        if 'select' in data:
            fields = list(set(fields).intersection(data.getlist('select')))
        
        if 'where' in data:
            invalid_field = self.check_filter(request, data.getdict('where'))
            self.check_invalid_field(request, data, 'where', invalid_field)
            query = query.filter(**data.getdict('where'))
        
        if 'exclude' in data:
            invalid_field = self.check_filter(request, data.getdict('exclude'))
            self.check_invalid_field(request, data, 'exclude', invalid_field)
            query = query.exclude(**data.getdict('exclude'))
        
        if 'order' in data:
            invalid_field = self.check_order(request, data.getlist('order'))
            self.check_invalid_field(request, data, 'order', invalid_field)
            query = query.order_by(*data.getlist('order'))
        
        if not fields:
            return error(request, 'No fields specified', status=400)
            
        return success(list(query.values(*fields)))
    
    def get_field_name_without_lookup(self, name):
        parts = name.split('__')
        field = self.Model._meta.get_field(parts[0])
        
        if len(parts) == 1:
            return name
        
        for part in parts[1:-1]:
            field = field.related_model()._meta.get_field(part)
        
        if parts[-1] in field.get_lookups():
            return '__'.join(parts[:-1])
        else:
            return '__'.join(parts)
        
    def check_invalid_field(self, request, data, param, invalid_key):
        if invalid_key:
            raise GracefulError(error(request, {
                'message': 'Invalid field in "' + param + '" parameter: "' + invalid_key + '"',
                'location': data.get_loc(param),
                'docs': 'request.parameters.' + param
            }, status=400))
        
    def check_filter(self, request, where):
        for key in where:
            try:
                key = self.get_field_name_without_lookup(key)
            except FieldDoesNotExist:
                return key
            
            if key not in self.filterable_keys:
                return key
        
        return None
    
    def check_order(self, request, order):
        for key in order:
            if key.startswith('-'):
                key = key[1:]
            if key not in self.orderable_keys:
                return key

        return None
        
    
class GracefulError(Exception):
    def __init__(self, response):
        self.response = response
