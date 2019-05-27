from ...util import init_matrix
import googlemaps
import os
import logging

logger = logging.getLogger(__name__)
ADDRESS_FIELDS = ['street', 'city', 'state', 'postal_code', 'country']

class GoogleMapsClient(googlemaps.Client):
    def _get_body(self, response):
        if response.status_code != 200:
            raise googlemaps.exceptions.HTTPError(response.status_code)

        body = response.json()

        api_status = body["status"]
        if api_status == "OK" or api_status == "ZERO_RESULTS":
            return body

        if api_status == "OVER_QUERY_LIMIT":
            raise googlemaps.exceptions._OverQueryLimit(
                api_status, body.get("error_message"))

        raise GoogleMapsApiError(api_status, body, body.get("error_message"))

class GoogleMapsApiError(googlemaps.exceptions.ApiError):
    def __init__(self, status, body, message=None):
        super(self, googlemaps.exceptions.ApiError).__init__(self, status, message)
        self.body = body

maps = googlemaps.Client(key=os.environ['MAPS_API_KEY'])

def distance_matrix(addresses, num_new_locations):
    num_locations = len(addresses)
    distances = init_matrix(len(addresses))
    valid = [True] * num_locations
    
    for i in range(num_locations):
        for j in range(num_locations):
            # Don't calculate distance between same start/end locations or unchanged start/end locations
            if i != j and not (i >= num_new_locations and j >= num_new_locations):
                try:
                    directions = maps.directions(origin=addresses[i], destination=addresses[j])[0]
                    distances[i][j] = directions['routes'][0]['legs'][0]['duration']['value']
                except Exception as e:
                    logger.debug('Maps error: %s | %s -> %s', e, addresses[i], addresses[j])
                    distances[i][j] = None
                    
                    if isinstance(e, GoogleMapsApiError):
                        waypoints = e.body.get('geocoded_waypoints', default=None)
                        
                        if waypoints and len(waypoints) >= 2:
                            if waypoints[0]['geocoder_status'] != 'OK':
                                valid[i] = False
                            if waypoints[1]['geocoder_status'] != 'OK':
                                valid[j] = False
                    
    
    return distances, valid
