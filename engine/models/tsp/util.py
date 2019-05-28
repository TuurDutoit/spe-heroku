from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from engine.data import get_data_set_for
import math

MIN = 60
HOUR = 60 * MIN
DAY = 24 * HOUR

class DataError(Exception):
    pass

class TSPContext:
    def __init__(self, data_set):
        # Extract relevant data from data set
        self.locations = data_set.get_locations()
        self.driving_times = data_set.get_driving_times()
        self.service_times = data_set.get_service_times()
        self.penalties = data_set.get_penalties()
        self.nodes = [0] + self.locations
        
        # Defaults
        self.num_vehicles = 1
        self.depot = 0
        self.day_duration = (18 - 9) * HOUR
        self.max_slack = 2 * HOUR
        
        self._check()
    
    def _check(self):
        if len(self.driving_times) != self.num_nodes:
            raise DataError('driving_times: expected %d elements, got: %d' % (self.num_nodes, len(self.service_times)))
        
        for row in self.driving_times:
            if len(row) != self.num_nodes:
                raise DataError('driving_time, row %d: expected %d elements, got: %d' % (
                    self.driving_times.index(row), self.num_nodes, len(row)
                ))
        
        if len(self.service_times) != self.num_nodes:
            raise DataError('service_times: expected %d elements, got: %d' % (self.num_nodes, len(self.service_times)))
        
        if len(self.penalties) != self.num_nodes:
            raise DataError('penalties: expected %d elements, got: %d' % (self.num_nodes, len(self.penalties)))
    
    @property
    def num_locations(self):
        return len(self.locations)
    
    @property
    def num_nodes(self):
        return len(self.nodes)


def create_context_for(userId):
    return create_context(get_data_set_for(userId))

def create_context(data_set):
    return TSPContext(data_set)


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
