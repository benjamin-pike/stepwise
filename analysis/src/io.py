import geopandas as gpd
import pandas as pd

from paths import experiment_paths as experiment_paths
from paths import paths


def load_data():
    return gpd.read_parquet(paths.results.enriched_15)


def read_table(path):
    if not path.is_file():
        raise FileNotFoundError(f'Table not found')

    return pd.read_csv(path)
