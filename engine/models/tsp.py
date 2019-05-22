from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from engine.data import get_data_set_for, get_driving_times, get_meeting_times

class TravellingSalesman:
    def __init__(self, context):
        self.context = context
        self.manager = manager = pywrapcp.RoutingIndexManager(context['num_nodes'], context['num_vehicles'], context['depot'])
        self.model = pywrapcp.RoutingModel(manager)
        self.params = get_search_params()
        
        set_distance_callback(self)
    
    def run(self):
        assignment = self.model.SolveWithParameters(self.params)
        return Solution(assignment, self)
    
    @staticmethod
    def for_user(userId):
        return TravellingSalesman(create_context_for(userId))
    
    @staticmethod
    def for_data_set(data_set):
        return TravellingSalesman(create_context(data_set))

class DataError(Exception):
    pass

class Solution:
    def __init__(self, assignment, routing):
        if not assignment:
            self.solved = False
            return self
        
        index = routing.model.Start(0)
        total_distance = 0
        stops = []

        while not routing.model.IsEnd(index):
            stop = Stop()
            previous_index, index, total_distance = stop.update(locals())
            if not stop.is_depot:
                stops.append(stop)
        
        self.solved = True
        self.stops = stops
        self.locations = [stop.to_loc for stop in stops]
        self.time = total_distance
    
    def to_dict(self):
        return {
            'time': self.time,
            'locations': self.locations,
            'stops': [stop.to_dict() for stop in self.stops]
        }

class Stop:
    def update(self, args):
        routing = args['routing']
        data_set = routing.context['data_set']
        previous_index = args['index']
        index = args['assignment'].Value(routing.model.NextVar(previous_index))
        arc_distance = routing.model.GetArcCostForVehicle(previous_index, index, 0)
        from_node = routing.manager.IndexToNode(previous_index)
        to_node = routing.manager.IndexToNode(index)
        meeting_time = routing.context['meeting_times'][to_node]
        
        self.is_depot = to_node <= 0
        
        if not self.is_depot:
            # Indexes in driving_times matrix
            self.from_idx = from_node
            self.to_idx = to_node
            # First row/column in driving_times is depot, followed by all locations
            # Correct the indexes here
            self.from_loc_idx = from_node - 1
            self.to_loc_idx = to_node - 1
            # Retrieve Location objects from data_set
            self.from_loc = None if self.from_idx == 0 else data_set.locations.all[self.from_loc_idx]
            self.to_loc = data_set.locations.all[self.to_loc_idx]
            
            self.time_driving = arc_distance - meeting_time
            self.time_meeting = meeting_time
            self.time = arc_distance
        
        return previous_index, index, args['total_distance'] + arc_distance
    
    def to_dict(self):
        return {
            'from': {
                'index': self.from_idx,
                'location_index': self.from_loc_idx,
                'location': self.from_loc
            },
            'to': {
                'index': self.to_idx,
                'location_index': self.to_loc_idx,
                'location': self.to_loc
            },
            'time': {
                'driving': self.time_driving,
                'meeting': self.time_meeting,
                'total': self.time
            }
        }

def create_context_for(userId):
    return create_context(get_data_set_for(userId))

def create_context(data_set):
    context = {
        'data_set': data_set,
        'driving_times': get_driving_times(data_set),
        'meeting_times': get_meeting_times(data_set),
        'num_vehicles': 1,
        'depot': 0
    }
    
    num_nodes = context['num_nodes'] = len(context['driving_times'])
    
    if len(context['meeting_times']) != num_nodes:
        num_times = len(context['meeting_times'])
        raise DataError('meeting_times : expected ' + str(num_nodes) + ' elements, got: ' + str(num_times))
    
    if context['depot'] < 0 or context['depot'] >= num_nodes:
        max_index = num_nodes - 1
        depot = context['depot']
        raise DataError('depot: must be a valid node index - [0, ' + str(max_index) + '], got: ' + str(depot))
    
    if context['num_vehicles'] < 1:
        num_vehicles = context['num_vehicles']
        raise DataError('num_vehicles: at least 1 vehicle is required, got: ' + str(num_vehicles))
    
    return context

def create_distance_callback(routing):
    def distance_callback(from_index, to_index):
        from_node = routing.manager.IndexToNode(from_index)
        to_node = routing.manager.IndexToNode(to_index)
        driving_time = routing.context['driving_times'][from_node][to_node]
        meeting_time = routing.context['meeting_times'][to_node]
        return driving_time + meeting_time
    
    return distance_callback

def register_distance_callback(routing, distance_callback=None):
    if distance_callback is None:
        distance_callback = create_distance_callback(routing)
    
    return routing.model.RegisterTransitCallback(distance_callback)

def set_distance_callback(routing, distance_callback_index=None):
    if distance_callback_index is None:
        distance_callback_index = register_distance_callback(routing)
    elif callable(distance_callback_index):
        distance_callback_index = register_distance_callback(routing, distance_callback_index)
    
    routing.model.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)
    
def get_search_params():
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    
    return params