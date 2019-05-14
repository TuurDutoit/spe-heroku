from django.views.generic import View
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Recommendation

def index(request):
    return render(request, "index.html")

@login_required
def test(request):
    #return HttpResponse(', '.join(Recommendation._meta.get_field('account').__dict__.keys()))
    return HttpResponse(Recommendation._meta.get_field('account').related_model().__dict__)

class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'login.html', { 'next': request.GET.get('next', '/') })
    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', '/'))
        else:
            return redirect(settings.LOGIN_URL)
