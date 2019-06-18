from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
application = get_wsgi_application()

from web.models import Account, Contact, Lead, Opportunity
#a = Account.objects.get(pk='0011i000007AZgwAAG')
a = Opportunity.objects.get(pk='0061i000004eXDTAA2')
print('%s' % (a.last_activity_date,))
print('%s' % (a.last_viewed_date,))
print('%s' % (a.last_referenced_date,))
print(a.score)
