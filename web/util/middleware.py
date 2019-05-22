from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import authenticate, login
from base64 import b64decode

class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if not request.path.startswith('/api'):
            return self.get_response(request)
        
        if not 'HTTP_AUTHORIZATION' in request.META:
            return self.unauthed()
        
        authentication = request.META['HTTP_AUTHORIZATION']
        (auth_method, encoded) = authentication.split(' ', 1)
        
        if 'basic' != auth_method.lower():
            return self.unauthed()
        
        auth = b64decode(encoded.strip())
        username, password = auth.decode('utf8').split(':', 1)
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return self.get_response(request)
        else:
            return self.unauthed()
    
    def unauthed(self):
        response = HttpResponse("""<html><title>Auth required</title><body>
                                <h1>Authorization Required</h1></body></html>""", content_type="text/html", status=401)
        response['WWW-Authenticate'] = 'Basic realm="web"'
        return response
