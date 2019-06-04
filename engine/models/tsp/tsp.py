from ortools.constraint_solver import pywrapcp
from .util import create_context, create_context_for, get_search_params, set_transit_callback, timestamp, h
import time

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
        
        # 1. Working day and breaks
        # Add time constraint
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
        for i in range(self.context.num_nodes):
            time_window = self.context.get_time_window(i)
            
            if time_window:
                index = self.manager.NodeToIndex(i)
                d_time.CumulVar(index).SetRange(int(time_window[0]), int(time_window[1]))
        # TODO
        # 3. Don't visit locations related to the same record
        
        # 4. Allow dropping nodes
        for i in range(self.context.num_nodes):
            penalty = self.context.get_penalty(i)
            
            if penalty != None:
                index = self.manager.NodeToIndex(i)
                self.model.AddDisjunction([index], int(penalty))
        
        # 5. Populate initial solution from existing schedule
        # If we don't do this, the model sometimes struggles to find a solution
        # with existing events (probably related to the small time windows)
        initial_route = []
        for i in range(self.context.num_nodes):
            is_existing = self.context.is_existing(i)
            
            if is_existing:
                initial_route.append(i)
        
        if len(initial_route) >= 1:
            self.initial_solution = self.model.ReadAssignmentFromRoutes([initial_route], True)
        else:
            self.initial_solution = None
    
    def run(self):
        start = time.time()
        if self.initial_solution:
            assignment = self.model.SolveFromAssignmentWithParameters(self.initial_solution, self.params)
        else:
            assignment = self.model.SolveWithParameters(self.params)
        end = time.time()
        
        return Solution(assignment, self, end - start)
    
    @staticmethod
    def for_user(userId):
        return TravellingSalesman(create_context_for(userId))
    
    @staticmethod
    def for_data_set(data_set):
        return TravellingSalesman(create_context(data_set))


class Solution:
    def __init__(self, assignment, routing, duration):
        self.running_time = duration
        
        if not assignment:
            self.solved = False
            return
        
        index = routing.model.Start(0)
        self.solved = True
        self.legs = []
        
        while not routing.model.IsEnd(index):
            # This is the index of the *previous* node, as
            leg = Leg(assignment, routing, index)
            index = leg.index
            if not leg.is_depot:
                self.legs.append(leg)
        
        self.time = self.legs[-1].finish[0]
        self.stops = [leg.stop for leg in self.legs]
    
    @property
    def __dict__(self):
        if not self.solved:
            return { 'solved': False, 'running_time': self.running_time }
        else:
            return {
                'solved': True,
                'running_time': self.running_time,
                'time': self.time,
                'stops': [stop.__dict__ for stop in self.stops],
                'legs': [leg.__dict__ for leg in self.legs]
            }
    
    def __repr__(self):
        if not self.solved:
            data = { 'solved': False, 'running_time': self.running_time }
        else:
            data = {
                'solved': True,
                'time': self.time,
                'running_time': self.running_time,
                'stops': list(self.stops),
                'legs': '[' + ', '.join([leg.__repr__() for leg in self.legs]) + ']'
            }
        
        return 'Solution(' + data.__repr__() + ')'
    
    def __str__(self):
        if not self.solved:
            return 'Solution(unsolved; ' + str(self.running_time) + ')'
        return '\n'.join((
            '*' * 30 + ' Solution(' + h(self.time) + ') ' + '*' * 30,
            '\n'.join(map(str, self.legs)) if self.solved else 'NO SOLUTION',
            '*' * 30 + str(self.running_time).rjust(19) + ' ' + '*' * 30
        ))


class Leg:
    def __init__(self, assignment, routing, prev_index):
        index = assignment.Value(routing.model.NextVar(prev_index))
        node = routing.manager.IndexToNode(index)
        prev_node = routing.manager.IndexToNode(prev_index)
        
        self.index = index
        self.node = node
        self.is_depot = node <= 0
        
        if self.is_depot:
            return
        
        driving_time = routing.context.get_driving_time(prev_node, node)
        service_time = routing.context.get_service_time(node)
        prev_service_time = routing.context.get_service_time(prev_node)
        
        d_time = routing.model.GetDimensionOrDie(D_TIME)
        time_var = d_time.CumulVar(index)
        prev_time_var = d_time.CumulVar(prev_index)
        arrival = (assignment.Min(time_var), assignment.Max(time_var))
        finish = (arrival[0] + service_time, arrival[1] + service_time)
        prev_arrival = assignment.Min(prev_time_var)
        prev_finish = prev_arrival + prev_service_time
    
        # Locations in driving_times matrix are preceded by the depot
        # Correct those indexes here
        self.stop_index = routing.context.node_to_stop_index(node)
        # Retrieve Location object from data_set
        self.stop = routing.context.get_stop_for_node(node)
        
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
    
    @property
    def __dict__(self):
        if self.is_depot:
            return { 'is_depot': True }
        else:
            return {
                **{
                    attr: getattr(self, attr)
                    for attr in ['index', 'node', 'stop_index', 'departure', 'arrival',
                        'finish', 'time_driving', 'time_serving', 'wait', 'slack']
                },
                'stop': self.stop.__dict__
            }
    
    def __repr__(self):
        return 'Stop(' + self.__dict__.__repr__() + ')'
    
    def __str__(self):
        pad = ' ' * 18
        return '\n'.join((
            timestamp(*self.departure),
            pad + 'Driving({}, {}, {})'.format(
                h(self.time_driving),
                h(self.wait),
                h(self.slack)
            ),
            timestamp(*self.arrival),
            pad + 'Service({}, {})'.format(h(self.time_serving), self.stop),
            timestamp(*self.finish)
        ))
