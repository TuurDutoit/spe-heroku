from django.views.generic import View
from django.http import HttpResponse, JsonResponse
import logging
import traceback
import os

logger = logging.getLogger(__name__)

class JsonApiEndpoint(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            return super(JsonApiEndpoint, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.exception('Exception: %s', str(e))
            return error(request, 'Something went wrong handling this request')


def error(req, errors, status=500):
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
            error['location'] = {'line': 0, 'col': 0}

        if not 'docs' in error or not error['docs'].startswith(req.get_host()):
            error['docs'] = get_doc_uri(req, error.get('docs', ''))

    return JsonResponse({
        'success': False,
        'status': status,
        'errors': errors
    }, status=status)

def success(data, status=200):
    return JsonResponse({
        'success': True,
        'status': status,
        'data': data
    }, status=status)


def get_doc_uri(req, suffix=''):
    return req.build_absolute_uri('/docs' + req.path + '#' + suffix)


def get_loc(string, index):
    lines = 0
    
    if type(string) == type(bytes()):
        string = string.decode('utf-8')
    
    if type(index) == type(str()):
        index = string.index(index)

    for line in string.split(os.linesep):
        if index <= len(line):
            return {'line': lines, 'col': index}
        else:
            index -= len(line) + len(os.linesep)
            lines += 1
