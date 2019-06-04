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
        self.data_set = data_set
        self.stops = data_set.get_stops()
        self.nodes = [0] + self.stops
        
        # Defaults
        self.num_vehicles = 1
        self.depot = 0
        self.day_duration = (18 - 9) * HOUR
        self.max_slack = 2 * HOUR
    
    @property
    def num_stops(self):
        return len(self.stops)
    
    @property
    def num_nodes(self):
        return len(self.nodes)
    
    # The number of nodes in the model that aren't stops, e.g. the depot
    @property
    def num_extra_nodes(self):
        return self.num_nodes - self.num_stops
    
    def is_stop(self, node_index):
        return node_index >= self.num_extra_nodes
    
    def node_to_stop_index(self, node_index):
        return node_index - self.num_extra_nodes
    
    def stop_to_node_index(self, stop_index):
        return stop_index + self.num_extra_nodes
    
    def get_stop(self, index):
        return self.stops[index]
    
    def get_stop_for_node(self, node_index):
        return self.get_stop(self.node_to_stop_index(node_index))
    
    def get_penalty(self, node_index):
        if not self.is_stop(node_index):
            return None
            
        return self.data_set.get_penalty(self.get_stop_for_node(node_index))
    
    def get_time_window(self, node_index):
        if not self.is_stop(node_index):
            return None
        
        return self.data_set.get_time_window(self.get_stop_for_node(node_index))
    
    def get_driving_time(self, from_node_index, to_node_index):
        if from_node_index == 0 or to_node_index == 0:
            return 0
        else:
            from_stop = self.get_stop_for_node(from_node_index)
            to_stop = self.get_stop_for_node(to_node_index)
            return self.data_set.get_driving_time(from_stop, to_stop)
    
    def get_service_time(self, node_index):
        if not self.is_stop(node_index):
            return 0
        
        stop = self.get_stop_for_node(node_index)
        return self.data_set.get_service_time(stop)
    
    def get_transit_time(self, from_node, to_node):
        return self.get_service_time(from_node) + self.get_driving_time(from_node, to_node)


def create_context_for(userId):
    return create_context(get_data_set_for(userId))

def create_context(data_set):
    return TSPContext(data_set)


def create_transit_callback(routing):
    def transit_callback(from_index, to_index):
        from_node = routing.manager.IndexToNode(from_index)
        to_node = routing.manager.IndexToNode(to_index)
        return routing.context.get_transit_time(from_node, to_node)

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
    params.time_limit.seconds = 10
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
