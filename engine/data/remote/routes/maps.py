import googlemaps
import os

maps = googlemaps.Client(key=os.environ['MAPS_API_KEY'])

def get_distances(locations):
    raise NotImplementedError