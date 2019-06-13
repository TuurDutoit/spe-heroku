from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
application = get_wsgi_application()

LAST_EVENT_QUERY = """
SELECT WhatId, WhoId, MAX(EndDateTime)
FROM Event
WHERE WhatId IN %s OR WhoId IN %s
GROUP BY CUBE(WhatId, WhoId)
HAVING
    (GROUPING(WhatId) = 1 OR GROUPING(WhoId) = 1) AND
    (GROUPING(WhatId) = 0 OR GROUPING(WhoId) = 0) AND
    (WhatId != NULL OR WhoId != NULL) AND
    (WhatId IN %s OR WhoId IN %s)
"""

def listify(arr):
    return '(' + ','.join(map(lambda item: "'%s'" % item, arr)) + ')'

from django.db import connections

what_ids = ('0011i000007AZgwAAG', '0011i00000BnM4LAAV')
who_ids = ('0031i00000CubdRAAR', '0031i000006utCBAAY')

print(what_ids)

with connections['salesforce'].cursor() as cursor:
    cursor.execute(LAST_EVENT_QUERY % (what_ids, who_ids, what_ids, who_ids), [])
    rows = cursor.fetchall()
    m = {}
    
    for row in rows:
        recordId = row[0] or row[1]
        m[recordId] = row[2]

print('Last activity for 0011i000007AZgwAAG:', m['0011i000007AZgwAAG'])
