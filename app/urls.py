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
    path("test", web.views.test),
    path("accounts/login/", web.views.LoginView.as_view()),
    path("api/engine/tsp", csrf_exempt(web.api.TSPEndpoint.as_view())),
    path("api/engine/recommendations", csrf_exempt(web.api.RecommendationsEndpoint.as_view())),
    path("api/engine/recalculate", csrf_exempt(web.api.RecalculateEndpoint.as_view())),
    path("api/engine/accounts", web.api.AccountsEndpoint.as_view()),
    path("api/engine/events", web.api.EventsEndpoint.as_view()),
    path("admin/", admin.site.urls),
]
