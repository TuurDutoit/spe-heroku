from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
application = get_wsgi_application()

from web.models import Account, Contact, Lead, Opportunity
from engine.models.recommendations import get_field
from engine.data.format import get_reason
from engine.data.remote.conf import OBJECTS
import json
res = {}

for Model in (Account, Contact, Lead, Opportunity):
    name = Model._meta.model_name
    obj = OBJECTS[name]
    this_res = res[name] = []
    records = Model.objects.all()

    for record in records:
        rec = {
            'score': record.score,
            'reasons': []
        }
        this_res.append(rec)

        if hasattr(record, 'best_attrs'):
            for attr in record.best_attrs:
                field = get_field(obj['model'], attr)
                value = getattr(record, attr)
                reason = get_reason(value, field, obj)
                if reason == None:
                    print(attr)
                rec['reasons'].append(reason)

print(res)

with open('test.json', 'w') as file:
    file.write(json.dumps(res))
