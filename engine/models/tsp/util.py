from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from engine.data import get_data_set_for
import math

class DataError(Exception):
    pass

class TSPContext:
    def __init__(self, data_set):
        self.locations = data_set.get_locations()
        self.driving_times = data_set.get_driving_times()
        self.service_times = data_set.get_service_times()
        self.penalties = data_set.get_penalties()
        self.num_vehicles = 1
        self.depot = 0
        self.day_start = 9
        self.day_end = 18
        self.day_time = self.day_end - self.day_start
        

def create_context_for(userId):
    return create_context(get_data_set_for(userId))

def create_context(data_set):
    context = {
        'locations': data_set.get_locations(),
        'driving_times': data_set.get_driving_times(),
        'service_times': data_set.get_service_times(),
        'penalties': data_set.get_penalties(),
        'num_vehicles': 1,
        'depot': 0,
        'day_start': 9,
        'day_end': 18,
    }

    context['nodes'] = [0] + context['locations']
    context['day_time'] = (context['day_end'] - context['day_start']) * 60 * 60
    context['max_slack'] = context['day_time']
    num_locations = context['num_locations'] = len(context['locations'])
    num_nodes = context['num_nodes'] = len(context['driving_times'])

    if len(context['service_times']) != num_nodes:
        num_times = len(context['service_times'])
        raise DataError('service_times : expected ' + str(num_nodes) + ' elements, got: ' + str(num_times))
    
    if len(context['penalties']) != num_locations:
        num_penalties = len(context['penalties'])
        raise DataError('penalties: expected ' + str(num_locations) + ' elements, got: ' + str(num_penalties))

    if context['depot'] < 0 or context['depot'] >= num_nodes:
        max_index = num_nodes - 1
        depot = context['depot']
        raise DataError('depot: must be a valid node index - [0, ' + str(max_index) + '], got: ' + str(depot))

    if context['num_vehicles'] < 1:
        num_vehicles = context['num_vehicles']
        raise DataError('num_vehicles: at least 1 vehicle is required, got: ' + str(num_vehicles))

    return context


def create_transit_callback(routing):
    def transit_callback(from_index, to_index):
        from_node = routing.manager.IndexToNode(from_index)
        to_node = routing.manager.IndexToNode(to_index)
        driving_time = routing.context['driving_times'][from_node][to_node]
        service_time = routing.context['service_times'][from_node]
        return driving_time + service_time

    return transit_callback


def register_transit_callback(routing, transit_callback=None):
    if transit_callback is None:
        transit_callback = create_transit_callback(routing)

    return routing.model.RegisterTransitCallback(transit_callback)


def set_transit_callback(routing, transit_callback_index=None):
    if transit_callback_index is None:
        transit_callback_index = register_transit_callback(routing)
    elif callable(transit_callback_index):
        transit_callback_index = register_transit_callback(
            routing, transit_callback_index)

    routing.model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    return transit_callback_index


def get_search_params():
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    #params.number_of_solutions_to_collect = 3

    return params

# Converts a number of seconds to hh:mm:ss format
def h(secs):
    seconds = secs % 60
    secs = math.floor(secs / 60)
    minutes = secs % 60
    secs = math.floor(secs / 60)
    hours = secs % 60
    return str(hours).rjust(2, '0') + ':' + str(minutes).rjust(2, '0') + ':' + str(seconds).rjust(2, '0')

def timestamp(a, b):
    return '{} {}'.format(h(a), h(b))