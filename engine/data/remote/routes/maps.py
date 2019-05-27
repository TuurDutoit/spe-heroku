from ...util import init_matrix
import googlemaps
import os
import logging

logger = logging.getLogger(__name__)

ADDRESS_FIELDS = ['street', 'city', 'state', 'postal_code', 'country']

maps = googlemaps.Client(key=os.environ['MAPS_API_KEY'])

def distance_matrix(addresses, num_new_locations):
    num_locations = len(addresses)
    distances = init_matrix(len(addresses))
    valid = [True] * num_locations
    
    for i in range(num_locations):
        for j in range(num_locations):
            # Don't calculate distance between same start/end locations or unchanged start/end locations
            if i != j and not (i >= num_new_locations and j >= num_new_locations):
                directions = maps.directions(origin=addresses[i], destination=addresses[j])
                
                if directions and directions['status'] == 'OK':
                    distances[i][j] = directions['routes'][0]['legs'][0]['duration']['value']
                else:
                    logger.debug('Maps error: %s | %s -> %s', directions['status'], addresses[i], addresses[j])
                    distances[i][j] = None
                    waypoints = directions.get('geocoded_waypoints', default=None)
                    
                    if not waypoints or len(waypoints) < 2:
                        valid[i] = False
                        valid[j] = False
                    else:
                        if waypoints[0]['geocoder_status'] != 'OK':
                            valid[i] = False
                        if waypoints[1]['geocoder_status'] != 'OK':
                            valid[j] = False
                    
    
    return distances, valid

def geocode(address):
    try:
        res = maps.geocode(address)
        location = res[0]['geometry']['location']
        return (location['lat'], location['lng'])
    except:
        return None
