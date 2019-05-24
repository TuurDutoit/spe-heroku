# Setup Django environment with models etc.
from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
application = get_wsgi_application()


# Actual TSP model
from engine.data import get_data_set_for
from engine.data.util import matrix_str
from engine.models.tsp import TravellingSalesman, create_context

data_set = get_data_set_for('0051i000001NHLCAA4')
context = create_context(data_set)
tsp = TravellingSalesman(context)
solution = tsp.run()


print(matrix_str(context['driving_times'], header=context['nodes']))
print(solution)
