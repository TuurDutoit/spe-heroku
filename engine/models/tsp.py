from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from engine.data import get_data_set_for, get_driving_times, get_service_times

D_TIME = 'time'

class TravellingSalesman:
    def __init__(self, context):
        self.context = context
        self.manager = manager = pywrapcp.RoutingIndexManager(context['num_nodes'], context['num_vehicles'], context['depot'])
        self.model = pywrapcp.RoutingModel(manager)
        self.params = get_search_params()
        
        self._setup()
    
    def _setup(self):
        transit_cb = set_transit_callback(self)
        self.model.AddDimension(
            transit_cb,
            60 * 60, # max. 1 hour waiting time
            (18 - 9) * 60 * 60, # Working 9am to 6pm
            True, # Travel time starts at 0, of course
            D_TIME
        )
        d_time = self.model.GetDimensionOrDie(D_TIME)
        
    
    def run(self):
        assignment = self.model.SolveWithParameters(self.params)
        solution = Solution(assignment, self)
        solution.print()
        return solution
    
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
            return
        
        d_time = routing.model.GetDimensionOrDie(D_TIME)
        index = routing.model.Start(0)
        stops = []

        while not routing.model.IsEnd(index):
            stop = Stop()
            previous_index, index = stop.update(locals())
            if not stop.is_depot:
                stops.append(stop)
        
        self.solved = True
        self.stops = stops
        self.locations = [stop.to_loc for stop in stops]
        self.time = assignment.Max(d_time.CumulVar(routing.model.End(0)))
    
    def to_dict(self):
        if self.solved:
            return {
                'time': self.time,
                'locations': [loc.pk for loc in self.locations],
                'stops': [stop.to_dict() for stop in self.stops]
            }
        else:
            return { 'solved': False }
        
    def print(self):
        for stop in self.stops:
            stop.print()
        
        print('-' * 80)
        print('Total time: {}'.format(self.time))

class Stop:
    def update(self, args):
        routing = args['routing']
        data_set = routing.context['data_set']
        assignment = args['assignment']
        previous_index = args['index']
        index = assignment.Value(routing.model.NextVar(previous_index))
        from_node = routing.manager.IndexToNode(previous_index)
        to_node = routing.manager.IndexToNode(index)
        driving_time = routing.context['driving_times'][from_node][to_node]
        service_time = routing.context['service_times'][to_node]
        time_var = args['d_time'].CumulVar(index)
        
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
            
            self.time_driving = driving_time
            self.time_serving = service_time
            self.time = driving_time + service_time
            self.arrival = (assignment.Min(time_var), assignment.Max(time_var))
            self.departure = self.arrival[1] + service_time
            self.slack = self.arrival[1] - self.arrival[0]
        
        return previous_index, index
    
    def to_dict(self):
        return {
            'from': {
                'index': self.from_idx,
                'location_index': self.from_loc_idx,
                'location': None if not self.from_loc else self.from_loc.pk
            },
            'to': {
                'index': self.to_idx,
                'location_index': self.to_loc_idx,
                'location': self.to_loc.pk
            },
            'time': {
                'driving': self.time_driving,
                'serving': self.time_serving,
                'total': self.time,
                'arrival': {
                    'min': self.arrival[0],
                    'max': self.arrival[1]
                },
                'departure': self.departure,
                'slack': self.slack
            }
        }
    
    def print(self):
        print('Arrive({}-{}) {} Depart({}) Slack({})'.format(
            self.arrival[0],
            self.arrival[1],
            self.to_loc_idx,
            self.departure,
            self.slack
        ))

def create_context_for(userId):
    return create_context(get_data_set_for(userId))

def create_context(data_set):
    context = {
        'data_set': data_set,
        'driving_times': get_driving_times(data_set),
        'service_times': get_service_times(data_set),
        'num_vehicles': 1,
        'depot': 0
    }
    
    num_nodes = context['num_nodes'] = len(context['driving_times'])
    
    if len(context['service_times']) != num_nodes:
        num_times = len(context['service_times'])
        raise DataError('service_times : expected ' + str(num_nodes) + ' elements, got: ' + str(num_times))
    
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
        transit_callback_index = register_transit_callback(routing, transit_callback_index)
    
    routing.model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    return transit_callback_index
    
def get_search_params():
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    #params.number_of_solutions_to_collect = 3
    
    return params
