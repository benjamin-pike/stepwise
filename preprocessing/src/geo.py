import time

import osmnx as ox
from osmnx._errors import ResponseStatusCodeError
from requests.exceptions import RequestException

from paths import paths

from .constants import CRS_GEO, CRS_METRIC, REGION

ox.settings.cache_folder = paths.preprocessing.cache


def get_buffered_region(region, buffer, crs = CRS_METRIC):
    buffered = ox.geocode_to_gdf(region).to_crs(CRS_METRIC).buffer(buffer)

    if crs != CRS_METRIC:
        buffered = buffered.to_crs(crs)

    return buffered.union_all()


def get_street_network():
    output = paths.preprocessing.shared.street_network

    if output.is_file():
        return ox.load_graphml(output)

    region = get_buffered_region(REGION, buffer = 5000, crs = CRS_GEO)

    for attempt in range(3):
        try:
            graph = ox.graph_from_polygon(region, network_type = 'drive', retain_all = True, simplify = True)
            break
        
        except (ResponseStatusCodeError, RequestException) as error:
            if attempt == 2:
                raise
            
            delay = 5 * 2 ** attempt
            print(f'Street network download failed (retrying in {delay}s: {error})')
            time.sleep(delay)

    graph = ox.project_graph(graph, to_crs = CRS_METRIC)
    
    ox.save_graphml(graph, output)
    
    return graph


def intersecting_features(frame, zone, candidates = None):
    if candidates is None:
        return frame.iloc[frame.sindex.query(zone, predicate = 'intersects', sort = True)]

    return candidates[candidates.intersects(zone)]
