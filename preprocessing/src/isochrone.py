import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union

from paths import paths

from .constants import CRS_METRIC


def fill_holes(geom):
    if geom.geom_type == 'Polygon':
        return Polygon(geom.exterior)
    
    elif geom.geom_type == 'MultiPolygon':
        return MultiPolygon([Polygon(p.exterior) for p in geom.geoms])
    
    elif geom.geom_type == 'GeometryCollection':
        polys = [p for p in geom.geoms if p.geom_type in ('Polygon', 'MultiPolygon')]

        if not polys:
            return geom

        return fill_holes(unary_union(polys))

    return geom


def extract_zones(lsoa, mins, buffer = 0.01, crs = CRS_METRIC):
    return extract_zones_by_duration(lsoa, (mins,), buffer = buffer, crs = crs)[mins]


def extract_zones_by_duration(lsoa, durations = (20, 15, 10), buffer = 0.01, crs = CRS_METRIC):
    selected = [z for z in (5, 10, 15, 20) if z <= max(durations)]
    gdf = gpd.read_file(paths.preprocessing.shared.isochrones / f'{lsoa}.geojson')
    coverage = gdf.groupby('seed_node')['minutes'].agg(set)

    if coverage.empty or any(not set(selected).issubset(values) for values in coverage):
        raise ValueError(
            f'{lsoa} is missing isochrone rings required for {max(durations)} minutes. '
            'Run isochrone.ipynb to generate all 5, 10, 15, and 20 minute rings.'
        )

    gdf = gdf[gdf['minutes'].isin(selected)].copy()
    gdf.geometry = gdf.geometry.buffer(buffer)
    gdf = gdf.to_crs(crs)

    by_duration = {}

    for minutes in durations:
        zones = []

        for seed, group in gdf[gdf['minutes'] <= minutes].groupby('seed_node'):
            exterior = fill_holes(unary_union(group.geometry))

            if not exterior.is_empty:
                zones.append((seed, exterior))

        by_duration[minutes] = zones

    return by_duration
