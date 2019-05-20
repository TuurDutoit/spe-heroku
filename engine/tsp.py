from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import time

class TravellingSalesman:
    def __init__(self, userId):
        self.data = data = create_data_model()
        self.manager = manager = pywrapcp.RoutingIndexManager(data['num_nodes'], data['num_vehicles'], data['depot'])
        self.model = pywrapcp.RoutingModel(manager)
        self.params = get_search_params()
        
        set_distance_callback(self)
    
    def run(self):
        start = time.time()
        assignment = self.model.SolveWithParameters(self.params)
        end = time.time()
        return solution_to_dict(assignment, self, end - start)

class DataError(Exception):
    pass

def create_data_model():
    data = {
        'driving_times': [
            [0, 30, 30],
            [30, 0, 30],
            [30, 30, 0]
        ],
        'meeting_times': [0, 60, 60],
        'num_vehicles': 1,
        'depot': 0
    }
    
    num_nodes = data['num_nodes'] = len(data['driving_times'])
    
    if len(data['meeting_times']) != num_nodes:
        num_times = len(data['meeting_times'])
        raise DataError('meeting_times : expected ' + str(num_nodes) + ' elements, got: ' + str(num_times))
    
    if data['depot'] < 0 or data['depot'] >= num_nodes:
        max_index = num_nodes - 1
        depot = data['depot']
        raise DataError('depot: must be a valid node index - [0, ' + str(max_index) + '], got: ' + str(depot))
    
    if data['num_vehicles'] < 1:
        num_vehicles = data['num_vehicles']
        raise DataError('num_vehicles: at least 1 vehicle is required, got: ' + str(num_vehicles))
    
    return data

def create_distance_callback(routing):
    def distance_callback(from_index, to_index):
        from_node = routing.manager.IndexToNode(from_index)
        to_node = routing.manager.IndexToNode(to_index)
        driving_time = routing.data['driving_times'][from_node][to_node]
        meeting_time = routing.data['meeting_times'][to_node]
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

def solution_to_dict(assignment, routing, exec_time):
    if not assignment:
        return None
    
    vehicles = []
    
    for vehicle in range(routing.data['num_vehicles']):
        index = routing.model.Start(vehicle)
        total_distance = 0
        stops = []
        
        while not routing.model.IsEnd(index):
            previous_index = index
            index = assignment.Value(routing.model.NextVar(index))
            arc_distance = routing.model.GetArcCostForVehicle(
                previous_index, index, vehicle)
            total_distance += arc_distance
            
            stops.append({
                'from': routing.manager.IndexToNode(previous_index),
                'to': routing.manager.IndexToNode(index),
                'distance': arc_distance
            })
        
        vehicles.append({
            'number': vehicle,
            'total_distance': total_distance,
            'stops': stops
        })
    
    return {
        '_time': exec_time,
        'total_time': assignment.ObjectiveValue(),
        'vehicles': vehicles
    }
