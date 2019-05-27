# Setup Django environment with models etc.
from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
application = get_wsgi_application()


# Actual code
from engine.data.remote.routes.manage import refresh_routes
from web.models import Account, Route, Location

"""
# Delete old data
Route.objects.all().delete()
Location.objects.all().delete()

# Insert fresh data
account_ids = [a.pk for a in Account.objects.filter(owner_id='0051i000001NHLCAA4')]
refresh_routes('account', account_ids, 'insert')
"""

refresh_routes('account', ['0011i00000BnM4LAAV'], 'update')
