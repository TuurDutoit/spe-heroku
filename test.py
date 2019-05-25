# Setup Django environment with models etc.
from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
application = get_wsgi_application()


# Actual code
from engine.data.remote.routes.manage import refresh_routes
refresh_routes('account', ['0011i00000BnM4LAAV', '0011i00000BnM09AAF','0011i00000BnM3hAAF', '0011i00000Bmx6XAAR', '0011i000007AZgwAAG'], 'insert')
