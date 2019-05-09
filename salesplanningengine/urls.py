from django.urls import path, include
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

admin.autodiscover()

import engine.views
import engine.api

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", engine.views.index),
    path("api/engine/recalculate", csrf_exempt(engine.api.EngineApiEndpoint.as_view())),
    path("admin/", admin.site.urls),
]
