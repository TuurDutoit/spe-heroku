from django.http import JsonResponse
from .util import get_loc, get_doc_uri

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
