# Django environment setup
from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
application = get_wsgi_application()

# Delete all recommendations, locations & routes from the database
# and recalculate *everything*
from engine.data import reset
from engine.models.recommendations import refresh_recommendations_for_all
from dateutil.parser import parse as parse_date
import argparse

parser = argparse.ArgumentParser(description='Reset the Sales Planning Engine database')
parser.add_argument('-f', '--filter',
    dest='filters', action='append', nargs=2, metavar=('object.field', 'type:value'),
    help='Filter the records that will be queried. If you omit "object", the filter will be applied to all objects. Parses the string respresentation "value" into "type". The default type is "str".')
parser.add_argument('--no-recs', dest='recs', action='store_false')
args = parser.parse_args()

def parse_bool(s):
    return False if s in ('n','no','false') else True

filters = {}
TYPES = {
    'str': str,
    'string': str,
    'int': int,
    'integer': int,
    'float': float,
    'bool': parse_bool,
    'boolean': parse_bool,
    'date': lambda s: parse_date(s).date(),
    'time': lambda s: parse_date(s).time(),
    'datetime': parse_date,
}

for (key, val) in args.filters or []:
    oparts = key.split('.')
    fparts = val.split(':')

    if len(fparts) == 1:
        value = val
    else:
        parse = TYPES[fparts[0]]
        value = parse(fparts[1])

    if len(oparts) == 1:
        obj = 'all'
        field = key
    else:
        (obj, field) = oparts
    
    if not obj in filters:
        filters[obj] = {}
    
    filters[obj][field] = value

ctxs = reset(filters)
print(ctxs)

if args.recs:
    refresh_recommendations_for_all(ctxs)
