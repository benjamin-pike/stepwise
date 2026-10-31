RANDOM_STATE = 7
RADIAL_BREAKPOINTS_KM = (8.0, 18.0)

OUTCOMES = ['qof_AF', 'qof_CHD', 'qof_DM', 'qof_HF', 'qof_HYP', 'qof_OB', 'qof_PAD', 'qof_STIA']
OUTCOME_ORDER = ['qof_HYP', 'qof_OB', 'qof_DM', 'qof_CHD', 'qof_AF', 'qof_STIA', 'qof_HF', 'qof_PAD']
OUTCOME_LABELS = {
    'qof_HYP': 'Hypertension',
    'qof_OB': 'Obesity',
    'qof_DM': 'Diabetes',
    'qof_CHD': 'CHD',
    'qof_AF': 'AF',
    'qof_STIA': 'Stroke / TIA',
    'qof_HF': 'HF',
    'qof_PAD': 'PAD'
}
COVARIATES = [
    'z_pct_0_14',
    'z_pct_45_64',
    'z_pct_65p',
    'z_pct_male',
    'z_pct_asian',
    'z_pct_black',
    'z_pct_mixed',
    'z_imd_score'
]
COMPONENTS = ['amenity_score', 'dwelling_score', 'land_use_score', 'street_score', 'transport_score']
COMPONENT_LABELS = {
    'amenity_score': 'Amenity access',
    'dwelling_score': 'Dwelling density',
    'land_use_score': 'Land-use mix',
    'street_score': 'Street connectivity',
    'transport_score': 'Transport access'
}
PRIMARY_ADJUSTMENT = 'Primary: demographics + deprivation'
ADJUSTMENT_SETS = {
    PRIMARY_ADJUSTMENT: COVARIATES,
    '+ NOx': COVARIATES + ['z_nox'],
    '+ NDVI': COVARIATES + ['z_ndvi'],
    '+ NOx + NDVI': COVARIATES + ['z_nox', 'z_ndvi']
}
SECTOR_ORDER = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
RADIAL_BAND_ORDER = ['0 – 8 km', '8 – 18 km', '>18 km']
