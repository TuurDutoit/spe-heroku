from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize
from django.core.exceptions import FieldDoesNotExist
import json
import re
import logging
import traceback
import os
import time

QUERYSTRING_PATTERN = r'(^|&){}'
FORMDATA_PATERN = r'--{}\s*Content-Disposition\s*:\s*form-data\s*;\s*name\s*=\s*"{}"'
JSON_PATTERN = r'"{}"\s*:'
KEY_PATTERN = r''
ERR_NO_PARAM = 'Expected parameter: "{}"'
ERR_NOT_LIST = 'Expected parameter of type "list": "{}"'
ERR_NOT_DICT = 'Expected parameter of type "dict": "{}"'
ERR_NOT_JSON = 'Failed to parse parameter as JSON: "{}"'

logger = logging.getLogger(__name__)

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
        
class RequestData:
    def __init__(self, request):
        self.request = request
        self.query = request.GET
        
        if request.content_type == 'application/json' and request.body:
            self.body = json.loads(request.body)
        else:
            self.body = request.POST or dict()
    
    def __getitem__(self, key):
        return self.get(key)
    
    def __contains__(self, key):
        return key in self.query or key in self.body
    
    def get(self, key, default=None, graceful=False):
        if key in self.query:
            return self.query[key]
        if key in self.body:
            return self.body[key]
        if default:
            return default
        
        self._error(ERR_NO_PARAM, key, graceful)
    
    def getlist(self, key, default=None, graceful=False):
        if key in self.query:
            value = self.query.getlist(key)
        elif key in self.body:
            value = self.body[key]
        elif default:
            value = default
        else:
            value = None

        if type(value) != type(list()):
            self._error(ERR_NOT_LIST, key, graceful)
        
        return value
    
    def getdict(self, key, default=None, graceful=False):
        value = self.get(key, default, graceful)
        
        if type(value) == type(str()):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                self._error(ERR_NOT_JSON, key, graceful)
        
        if type(value) != type(dict()):
            self._error(ERR_NOT_DICT, key, graceful)
        
        return value
    
    def get_loc(self, key):
        if key in self.query:
            return get_loc(self.request.META['QUERY_STRING'], QUERYSTRING_PATTERN.format(key), component='query')
        if key in self.body:
            if request.content_type == 'application/json':
                return get_loc(self.request.body, JSON_PATTERN.format(key))
            elif request.content_type == 'application/x-www-form-urlencoded':
                return get_loc(self.request.body, QUERYSTRING_PATTERN.format(key))
            elif request.content_type == 'multipart/form-data':
                boundary = request.content_params.get('boundary')
                return get_loc(self.request.body, FORMDATA_PATERN.format(boundary, key))
        
        return { 'line': 0, 'col': 0, 'component': 'request' }
    
    def keys(self):
        if type(self.body) == type(dict()):
            body = self.body
        else:
            body = self.body.dict()
            
        return list(self.query.dict().keys()) + list(self.body.keys())
    
    def _error(self, msg_pattern, key, graceful):
        if graceful:
            msg = msg_pattern.format(key) if graceful == True else graceful
            raise GracefulError(error(self.request, msg, 400))
        else:
            raise KeyError(msg_pattern.format(key))
        
class GracefulError(Exception):
    def __init__(self, response):
        self.response = response

def error(req, errors, status=500, auto_location=True):
    if type(errors) == type(str()) or type(errors) == type(dict()):
        errors = [errors]

    for i in range(len(errors)):
        error = errors[i]
        if type(error) == type(str()):
            error = {
                'message': error
            }
            errors[i] = error

        if auto_location:
            if 'location' in error:
                if type(error['location']) == type(int()) or type(error['location']) == type(str()):
                    error['location'] = get_loc(req.body, error['location'])
            else:
                error['location'] = {'component': 'body', 'line': 0, 'col': 0}

        if not 'docs' in error or not error['docs'].startswith(req.get_host()):
            error['docs'] = get_doc_uri(req, error.get('docs', ''))

    return JsonResponse({
        'success': False,
        'status': status,
        'errors': errors
    }, status=status)

def success(data=None, status=200):
    return JsonResponse({
        'success': True,
        'status': status,
        'data': data
    }, status=status)


def get_doc_uri(req, suffix=''):
    return req.build_absolute_uri('/docs' + req.path + '#' + suffix)


def get_loc(string, index, component='body'):
    lines = 0
    
    if type(string) == type(bytes()):
        string = string.decode('utf-8')
    
    if type(index) == type(str()) and type(index) == type(str()):
        match = re.search(index, string)
        
        if match:
            index = match.start()
        else:
            index = 0

    for line in string.split(os.linesep):
        if index <= len(line):
            return {'line': lines, 'col': index, 'component': component}
        else:
            index -= len(line) + len(os.linesep)
            lines += 1

def to_json(obj):
    return json.loads(serialize('json', [obj]))[0]

class Timer:
    def __init__(self):
        self.starts = {}
        self.intervals = []
        self._group = []
        
    def _name(self, name):
        return name if len(self._group) == 0 else ':'.join(self._group) + ':' + name
    
    def start(self, name):
        self.starts[self._name(name)] = time.time()
        return self
    
    def stop(self, name):
        self.intervals.append((self._name(name), time.time() - self.starts[self._name(name)]))
        return self
    
    def mark(self, oldName, newName):
        self.stop(oldName)
        self.start(newName)
        return self
    
    def gstart(self, name):
        self.start(name)
        self._group.append(name)
        return self
    
    def gstop(self, name):
        self._group.pop()
        self.stop(name)
        return self
    
    def to_dict(self):
        d = {}
        
        for (name, duration) in self.intervals:
            d[name] = duration
        
        return d
