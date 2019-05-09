from django.views.generic import View
from django.http import HttpResponse, JsonResponse
import json
import os

class EngineApiEndpoint(View):
    http_method_names = ['post']

    def post(self, req, *args, **kwargs):
        try:
            data = json.loads(req.body)
        except json.JSONDecodeError:
            return error(req, {'message': 'Empty or malformed body.', 'docs': '#hello'}, 400)
        return success(data)


def error(req, errors, status = 500):
    if type(errors) == type(str()) or type(errors) == type(dict()):
        errors = [errors]
    
    for i in range(len(errors)):
        error = errors[i]
        if type(error) == type(str()):
            error = {
                'message': error
            }
            errors[i] = error
        
        if 'location' in error:
            if type(error['location']) == type(int()):
                error['location'] = get_loc(req.body, error['location'])
        else:
            error['location'] = { 'line': 0, 'col': 0 }
        
        if not 'docs' in error or not error['docs'].startswith(req.get_host()):
            error['docs'] = req.build_absolute_uri('/docs' + req.path + error.get('docs', ''))
        
    return JsonResponse({
        'success': False,
        'status': status,
        'errors': errors
    }, status=status)

def get_loc(string, index):
    lines = 0
    
    for line in string.split(os.linesep):
        if index <= len(line):
            return { 'line': lines, 'col': index }
        else:
            index -= len(line) + len(os.linesep)
            lines += 1

def success(data, status = 200):
    return JsonResponse({
        'success': True,
        'status': status,
        'data': data
    }, status=status)
