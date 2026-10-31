import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Geod

from .constants import COMPONENTS, RADIAL_BREAKPOINTS_KM, SECTOR_ORDER


def complete_case_mask(frame, outcome, covariates):
    columns = ['walkability_score', *COMPONENTS, outcome, *covariates]

    return frame[columns].notna().all(axis = 1)


def geographic_features(frame, breakpoints = RADIAL_BREAKPOINTS_KM):
    projected = frame.to_crs('EPSG:27700')
    centroids = projected.geometry.centroid
    centre = centroids.union_all().centroid

    locations = gpd.GeoSeries(centroids, crs = projected.crs).to_crs('EPSG:4326')
    origin = gpd.GeoSeries([centre], crs = projected.crs).to_crs('EPSG:4326').iloc[0]

    azimuth, _, distance = Geod(ellps = 'WGS84').inv(
        np.full(len(frame), origin.x), np.full(len(frame), origin.y), locations.x.to_numpy(), locations.y.to_numpy()
    )

    result = projected.copy()
    result['centroid_x'] = centroids.x
    result['centroid_y'] = centroids.y
    result['dist_km'] = distance / 1000
    result['azimuth'] = azimuth % 360

    sectors = np.asarray(SECTOR_ORDER)[((result.azimuth + 22.5) // 45).astype(int) % 8]
    result['sector'] = pd.Categorical(sectors, categories = SECTOR_ORDER)

    for column, values in zip(['seg1', 'seg2', 'seg3'], radial_features(result.dist_km, breakpoints).T):
        result[column] = values

    return result, {'longitude': origin.x, 'latitude': origin.y, 'x': centre.x, 'y': centre.y}


def radial_features(distance, breakpoints = RADIAL_BREAKPOINTS_KM):
    first, second = breakpoints
    distance = np.asarray(distance)

    return np.column_stack(
        [
            np.clip(distance, 0, first),
            np.clip(distance - first, 0, second - first),
            np.maximum(distance - second, 0)
        ]
    )
