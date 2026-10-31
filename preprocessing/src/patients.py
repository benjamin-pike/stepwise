import zipfile
from functools import lru_cache

import pandas as pd

from paths import paths


@lru_cache(maxsize = 1)
def london_weights():
    lookup = pd.read_csv(paths.raw.health.lsoa_lookup)
    london = lookup.loc[lookup.LAD22CD.str.startswith('E09'), ['LSOA11CD', 'LSOA21CD']].drop_duplicates()
    
    population = pd.read_csv(
        paths.raw.shared.medsat, usecols = ['geography code', 'c_total population']
    ).set_index('geography code')['c_total population']

    london['population'] = london.LSOA21CD.map(population)
    london['weight'] = london.population / london.groupby('LSOA11CD').population.transform('sum')

    return london[['LSOA11CD', 'LSOA21CD', 'weight']]


def load_patients(year):
    with zipfile.ZipFile(paths.raw.health.patient_files[year]) as archive:
        member = next(name for name in archive.namelist() if name.endswith('gp-reg-pat-prac-lsoa-all.csv'))
        with archive.open(member) as stream:
            patients = pd.read_csv(stream, dtype = {'PRACTICE_CODE': str, 'LSOA_CODE': str})

    patients = patients.rename(columns = {'Number of Patients': 'NUMBER_OF_PATIENTS'})
    patients = patients[['PRACTICE_CODE', 'LSOA_CODE', 'NUMBER_OF_PATIENTS']].copy()
    patients['NUMBER_OF_PATIENTS'] = patients.NUMBER_OF_PATIENTS.astype(float)

    weights = london_weights()
    in_london = patients.LSOA_CODE.isin(weights.LSOA11CD)
    
    mapped = patients.loc[in_london].merge(weights, left_on = 'LSOA_CODE', right_on = 'LSOA11CD')
    mapped['LSOA_CODE'] = mapped.LSOA21CD
    mapped['NUMBER_OF_PATIENTS'] *= mapped.weight

    combined = pd.concat([patients.loc[~in_london], mapped[patients.columns]], ignore_index = True)

    return combined.groupby(
        ['PRACTICE_CODE', 'LSOA_CODE'], as_index = False, sort = False, dropna = False
    ).NUMBER_OF_PATIENTS.sum()
