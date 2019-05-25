from ...util import init_matrix
import googlemaps
import os
import random

ADDRESS_FIELDS = ['street', 'city', 'state', 'postal_code', 'country']

maps = googlemaps.Client(key=os.environ['MAPS_API_KEY'])

def distance_matrix(addresses, num_new_locations):
    num_locations = len(addresses)
    distances = init_matrix(len(addresses))
    
    for i in range(num_locations):
        for j in range(num_locations):
            # Don't calculate distance between same start/end locations or unchanged start/end locations
            if i != j and not (i >= num_new_locations and j >= num_new_locations):
                distances[i][j] = random.randint(1*60, 1.5*60*60)
    
    return distances, [True] * num_locations

def geocode(address):
    try:
        res = maps.geocode(address)
        location = res[0]['geometry']['location']
        return (location['lat'], location['lng'])
    except:
        return None