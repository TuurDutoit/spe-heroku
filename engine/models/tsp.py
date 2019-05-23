from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from engine.data import get_data_set_for
from engine.data.util import s_to_h

D_TIME = 'time'

class TravellingSalesman:
    def __init__(self, context):
        self.context = context
        self.manager = manager = pywrapcp.RoutingIndexManager(context['num_nodes'], context['num_vehicles'], context['depot'])
        self.model = pywrapcp.RoutingModel(manager)
        self.params = get_search_params()
        
        self._setup()
    
    def _setup(self):
        # Set global cost function as cumulative time
        transit_cb = set_transit_callback(self)
        
        # Add time constraint
        #  1. Working day
        self.model.AddDimension(
            transit_cb,
            (18 - 9) * 60 * 60,  # No maximum waiting time
            (15 - 9) * 60 * 60, # Working 9am to 6pm
            True, # Travel time starts at 0, of course
            D_TIME
        )
        d_time = self.model.GetDimensionOrDie(D_TIME)
        
        # TODO
        #  2. Existing schedule (based on time windows)
        
        # Allow dropping nodes
        for i in range(1, self.context['num_nodes']):
            index = self.manager.NodeToIndex(i)
            penalty = self.context['penalties'][i - 1]
            self.model.AddDisjunction([index], penalty)
    
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
            return
        
        d_time = routing.model.GetDimensionOrDie(D_TIME)
        index = routing.model.Start(0)
        previous_departure = (0, 0)
        stops = []

        while not routing.model.IsEnd(index):
            stop = Stop()
            index, previous_index, previous_departure = stop.update(locals())
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
                'locations': list(self.locations),
                'stops': [stop.to_dict() for stop in self.stops]
            }
        else:
            return { 'solved': False }
        
    def print(self):
        if not self.solved:
            print('NO SOLUTION')
            return
            
        pad = '                  '
        print(pad + 'Depot')
        prev_dep = (0, 0)
        
        for stop in self.stops:
            print(s_to_h(prev_dep[0]) + ' ' + s_to_h(stop.arrival[1] - stop.time_driving))
            print(pad + 'Driving({}, {}, {})'.format(
                s_to_h(stop.time_driving),
                s_to_h(stop.arrival[0] - prev_dep[0] - stop.time_driving),
                s_to_h(stop.arrival[1] - prev_dep[0] - stop.time_driving))
            )
            print(s_to_h(stop.arrival[0]) + ' ' + s_to_h(stop.arrival[1]))
            print(pad + 'Service({}, {})'.format(s_to_h(stop.time_serving), stop.to_loc))
            print(s_to_h(stop.departure[0]) + ' ' + s_to_h(stop.departure[1]))
            prev_dep = stop.departure

class Stop:
    def update(self, args):
        routing = args['routing']
        locations = routing.context['locations']
        assignment = args['assignment']
        d_time = args['d_time']
        prev_dep = args['previous_departure']
        
        previous_index = args['index']
        index = assignment.Value(routing.model.NextVar(previous_index))
        from_node = routing.manager.IndexToNode(previous_index)
        to_node = routing.manager.IndexToNode(index)
        is_depot = to_node <= 0
        
        driving_time = routing.context['driving_times'][from_node][to_node]
        service_time = routing.context['service_times'][to_node]
        
        time_var = d_time.CumulVar(index)
        arrival = (assignment.Min(time_var), assignment.Max(time_var))
        departure = (arrival[0] + service_time, arrival[1] + service_time)
        
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
            self.from_loc = None if self.from_idx == 0 else locations[self.from_loc_idx]
            self.to_loc = locations[self.to_loc_idx]
            
            # 0: soonest time at which we can or are allowed to arrive
            # 1: latest time at which we are allowed to arrive
            self.arrival = arrival
            # arrival + service_time
            self.departure = departure
            # Time needed to drive to this location from the previous one
            self.time_driving = driving_time
            # Time spent at this location
            self.time_serving = service_time
            # Time you are expected to have to wait if everything goes smoothly at previous client
            # In other words: the amount of time you are expected to be early
            self.wait = arrival[0] - prev_dep[0] - driving_time
            # Maximum amount of time you can afford to lose between the previous client and this one
            # e.g. previous meeting runs out, traffic jams, etc.
            self.slack = arrival[1] - prev_dep[0] - driving_time
        
        return index, previous_index, prev_dep
    
    def to_dict(self):
        if self.is_depot:
            return { 'is_depot': True }
        else:
            return {
                attr: getattr(self, attr)
                for attr in ['from_idx', 'to_idx', 'from_loc_idx', 'to_loc_idx', 'from_loc', 'to_loc',
                    'time_driving', 'time_serving', 'time', 'arrival', 'slack']
            }
    
    def print(self):
        print('Arrive({}-{}) {} Depart({}) Slack({})'.format(
            self.arrival[0],
            self.arrival[1],
            self.to_loc_idx,
            self.departure,
            self.slack
        ))

def get_var_val(var, assignment=None):
    if not var:
        print('No var')
        return (0, 0, 0)
    if assignment:
        print('has assignment')
        return (assignment.Min(var), assignment.Value(var), assignment.Max(var))
    else:
        print('no assignment')
        return (var.Min(), var.Value() if var.Bound() else None, var.Max())

def create_context_for(userId):
    return create_context(get_data_set_for(userId))

def create_context(data_set):
    context = {
        'locations': data_set.get_locations(),
        'driving_times': data_set.get_driving_times(),
        'service_times': data_set.get_service_times(),
        'penalties': data_set.get_penalties(),
        'num_vehicles': 1,
        'depot': 0
    }
    
    context['num_locations'] = len(context['locations'])
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
