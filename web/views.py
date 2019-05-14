from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Recommendation

def index(request):
    return render(request, "index.html")

@login_required
def test(request):
    #return HttpResponse(', '.join(Recommendation._meta.get_field('account').__dict__.keys()))
    return HttpResponse(Recommendation._meta.get_field('account').related_model().__dict__)