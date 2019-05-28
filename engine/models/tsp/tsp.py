from __future__ import print_function
from ortools.constraint_solver import pywrapcp
from .util import create_context, create_context_for, get_search_params, set_transit_callback, timestamp, h

D_TIME = 'time'

class TravellingSalesman:
    def __init__(self, context):
        self.context = context
        self.manager = manager = pywrapcp.RoutingIndexManager(context.num_nodes, context.num_vehicles, context.depot)
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
            self.context.max_slack,  # No maximum waiting time
            self.context.day_duration, # Working 9am to 6pm
            True, # Travel time starts at 0, of course
            D_TIME
        )
        d_time = self.model.GetDimensionOrDie(D_TIME)
        
        # TODO
        #  2. Existing schedule (based on time windows)
        
        # TODO
        # 3. Don't visit locations related to the same record
        
        # Allow dropping nodes
        for i in range(self.context.num_nodes):
            index = self.manager.NodeToIndex(i)
            penalty = self.context.penalties[i]
            
            if penalty != None:
                self.model.AddDisjunction([index], penalty)
    
    # Convert a node number into the corresponding location's index
    def node_to_loc_idx(self, node):
        return node - (self.context.num_nodes - self.context.num_locations)
    
    def run(self):
        assignment = self.model.SolveWithParameters(self.params)
        return Solution(assignment, self)
    
    @staticmethod
    def for_user(userId):
        return TravellingSalesman(create_context_for(userId))
    
    @staticmethod
    def for_data_set(data_set):
        return TravellingSalesman(create_context(data_set))


class Solution:
    def __init__(self, assignment, routing):
        if not assignment:
            self.solved = False
            return
        
        d_time = routing.model.GetDimensionOrDie(D_TIME)
        time_var = d_time.CumulVar(routing.model.End(0))
        index = routing.model.Start(0)
        self.time = assignment.Max(time_var)
        self.solved = True
        self.stops = []
        
        while not routing.model.IsEnd(index):
            # This is the index of the *previous* node, as
            stop = Stop(assignment, routing, index)
            index = stop.index
            if not stop.is_depot:
                self.stops.append(stop)
                
        self.locations = [stop.location for stop in self.stops]
    
    @property
    def __dict__(self):
        if not self.solved:
            return { 'solved': False }
        else:
            return {
                'solved': True,
                'time': self.time,
                'locations': list(self.locations),
                'stops': [stop.__dict__ for stop in self.stops]
            }
    
    def __repr__(self):
        if not self.solved:
            data = { 'solved': False }
        else:
            data = {
                'solved': True,
                'time': self.time,
                'locations': list(self.locations),
                'stops': '[' + ', '.join([stop.__repr__() for stop in self.stops]) + ']'
            }
        
        return 'Solution(' + data.__repr__() + ')'
    
    def __str__(self):
        return '\n'.join((
            '*' * 80,
            '\n'.join(map(str, self.stops)) if self.solved else 'NO SOLUTION',
            '*' * 80
        ))


class Stop:
    def __init__(self, assignment, routing, prev_index):
        index = assignment.Value(routing.model.NextVar(prev_index))
        node = routing.manager.IndexToNode(index)
        prev_node = routing.manager.IndexToNode(prev_index)
        
        self.index = index
        self.node = node
        self.is_depot = node <= 0
        
        if self.is_depot:
            return
        
        driving_time = routing.context.driving_times[prev_node][node]
        service_time = routing.context.service_times[node]
        prev_service_time = routing.context.service_times[prev_node]
        
        d_time = routing.model.GetDimensionOrDie(D_TIME)
        time_var = d_time.CumulVar(index)
        prev_time_var = d_time.CumulVar(prev_index)
        arrival = (assignment.Min(time_var), assignment.Max(time_var))
        finish = (arrival[0] + service_time, arrival[1] + service_time)
        prev_arrival = assignment.Min(prev_time_var)
        prev_finish = prev_arrival + prev_service_time
    
        # Locations in driving_times matrix are preceded by the depot
        # Correct those indexes here
        self.location_index = routing.node_to_loc_idx(node)
        # Retrieve Location object from data_set
        self.location = routing.context.locations[self.location_index]
        
        # - earliest time you can leave from previous location
        # - latest time you should leave from previous location in order to be here on time
        self.departure = (prev_finish, arrival[1] - driving_time)
        # - earliest time at which you can or are allowed to arrive
        # - latest time at which you are allowed to arrive
        self.arrival = arrival
        # arrival + service_time
        self.finish = finish
        # Time needed to drive to this location from the previous one
        self.time_driving = driving_time
        # Time spent at this location
        self.time_serving = service_time
        # Time you are expected to have to wait if everything goes smoothly at previous client
        # In other words: the amount of time you are expected to be early
        self.wait = arrival[0] - prev_finish - driving_time
        # Maximum amount of time you can afford to lose between the previous client and this one
        # e.g. previous meeting runs out, traffic jams, etc.
        self.slack = arrival[1] - prev_finish - driving_time
    
    def __repr__(self):
        if self.is_depot:
            data = { 'is_depot': True }
        else:
            data = {
                attr: getattr(self, attr)
                for attr in ['index', 'node', 'location_index', 'location', 'departure', 'arrival',
                    'finish', 'time_driving', 'time_serving', 'wait', 'slack']
            }
        
        return 'Stop(' + data.__repr__() + ')'
    
    def __str__(self):
        pad = ' ' * 18
        return '\n'.join((
            timestamp(*self.departure),
            pad + 'Driving({}, {}, {})'.format(
                h(self.time_driving),
                h(self.arrival[0] - self.departure[0] - self.time_driving),
                h(self.arrival[1] - self.departure[0] - self.time_driving)
            ),
            timestamp(*self.arrival),
            pad + 'Service({}, {})'.format(h(self.time_serving), self.location),
            timestamp(*self.finish)
        ))
