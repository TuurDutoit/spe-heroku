from django.urls import path, include
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

admin.autodiscover()

import web.views
import web.api

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", web.views.index),
    path("api/engine/recalculate", csrf_exempt(web.api.EngineApiEndpoint.as_view())),
    path("admin/", admin.site.urls),
]
