from pathlib import Path
from types import SimpleNamespace


def _files(directory, **filenames):
    return SimpleNamespace(
        directory = directory,
        tables = directory / 'tables',
        figures = directory / 'figures',
        by_name = {value: directory / value for value in filenames.values()},
        **{name: directory / value for name, value in filenames.items()},
    )


def for_root(root):
    # Repository directories
    root = Path(root).resolve()
    
    data = root / 'data'
    artifacts = root / 'artifacts'
    preprocessing = root / 'preprocessing'
    analysis = root / 'analysis'
    pre_artifacts = artifacts / 'preprocessing'
    analysis_artifacts = artifacts / 'analysis'

    # Raw source data
    raw = SimpleNamespace(
        directory = data,
        shared = _files(
            data / 'shared',
            medsat = 'medsat_data.csv',
            lsoa_lookup = 'lsoa_lookup.csv',
        ),
        walkability = _files(
            data / 'walkability',
            epc = 'dwellings/epc_certificates.csv.zip',
            uprn = 'dwellings/os_uprn.gpkg',
            land_use = 'land_use/tiles.tif',
            osm_tags = 'poi/osm_tags.db',
            atoc = 'transport/atoc_rail.gz',
            transxchange = 'transport/transx_tfl.zip',
            gtfs_bus = 'transport/gtfs_bus.zip',
        ),
        health = _files(
            data / 'health',
            lsoa_lookup = 'lsoa_2011_to_2021.csv',
        ),
        context = _files(
            data / 'context',
            imd = 'imd/imd_2025.csv',
            vegetation = 'vegetation/vegetation_indices_2023.csv',
            nox = 'pollution/nox.csv',
            pm25 = 'pollution/pm25.csv',
            ozone = 'pollution/ozone.csv',
        ),
        validation = _files(
            data / 'validation',
            stockton = 'stockton.csv',
            boundaries = 'oa_2001_boundaries.gpkg',
        ),
    )
    raw.health.patients = data / 'health/patients'
    raw.health.patient_files = {
        year: raw.health.patients / f'{year}.zip' for year in range(2021, 2027)
    }
    raw.health.qof_files = {
        year: data / 'health/qof' / f'{year}.zip' for year in range(2021, 2027)
    }

    # Preprocessing - shared geometry and cached source data
    shared = _files(
        pre_artifacts / 'walkability/shared',
        lsoa = 'lsoa.parquet',
        network = 'network_greater_london.graphml',
        street_network = 'network_drive_greater_london.graphml',
        amenities = 'amenities/amenities.parquet',
        osm_tags = 'amenities/osm_tags.json',
        grouped_tags = 'amenities/osm_tags_grouped.json',
        epc = 'dwellings/dwellings_epc.parquet',
        dwellings = 'dwellings/dwellings_in_region.parquet',
    )
    shared.isochrones = shared.directory / 'isochrones'
    shared.subgraphs = shared.directory / 'subgraphs'
    shared.archives = shared.directory / 'archives'

    # Preprocessing - transport feeds and service frequencies
    transport = _files(
        shared.directory / 'transport',
        bus = 'transport_stop_frequency_bus.csv',
        rail = 'transport_stop_frequency_rail.csv',
        tfl = 'transport_stop_frequency_tfl.csv',
    )
    transport.gtfs = {
        'bus': raw.walkability.gtfs_bus,
        **{mode: transport.directory / f'gtfs_{mode}.zip' for mode in ('rail', 'tfl')},
    }

    transport.feeds = {
        mode: _files(
            transport.directory / mode,
            stops = 'stops.txt',
            stop_times = 'stop_times.txt',
            trips = 'trips.txt',
            calendar = 'calendar.txt',
            calendar_dates = 'calendar_dates.txt',
        )
        for mode in ('bus', 'rail', 'tfl')
    }

    # Preprocessing - component and index outputs for each walkshed duration
    walkability = {
        minutes: _files(
            pre_artifacts / 'walkability' / f'{minutes}min',
            amenities = 'amenities.parquet',
            dwellings = 'dwellings.parquet',
            land_use = 'land_use.parquet',
            streets = 'streets.parquet',
            transport = 'transport.parquet',
            slim = 'walkability.parquet',
            enriched = 'walkability_enriched.parquet',
            amenity_map = 'amenity.html',
            dwellings_map = 'dwellings.html',
            land_use_map = 'land_use.html',
            streets_map = 'streets.html',
            transport_map = 'transport.html',
            neighborhoods = 'neighbourhoods',
        )
        for minutes in (10, 15, 20)
    }

    # Preprocessing - health and context outputs
    health = _files(
        pre_artifacts / 'health',
        qof = 'qof.csv',
        prevalence = 'qof_prevalence.csv',
    )
    health.annual = {year: health.directory / f'qof_{year}.csv' for year in range(2021, 2027)}

    context = _files(
        pre_artifacts / 'context',
        imd = 'imd.csv',
        ndvi = 'ndvi.csv',
        pollution = 'pollution.csv',
    )

    # Preprocessing - notebook sources, execution records, and workflow
    notebook_names = (
        'master',
        'context/imd',
        'context/ndvi',
        'context/pollution',
        'health/patients',
        'health/qof',
        'walkability/geometry/lsoa',
        'walkability/geometry/isochrone',
        'walkability/preparation/annotator',
        'walkability/preparation/timetables',
        'walkability/components/amenities',
        'walkability/components/dwellings',
        'walkability/components/land_use',
        'walkability/components/streets',
        'walkability/components/transport',
        'walkability/walkability',
    )

    pre = SimpleNamespace(
        directory = preprocessing,
        shared = shared,
        transport = transport,
        walkability = walkability,
        health = health,
        context = context,
        cache = pre_artifacts / 'cache',
        notebooks = {name: preprocessing / 'notebooks' / f'{name}.ipynb' for name in notebook_names},
        executed = pre_artifacts / 'executed_notebooks',
        uk2gtfs = root / 'lib/UK2GTFS',
    )

    pre.master_execution = pre.executed / 'master.ipynb'
    pre.workflow = preprocessing / 'src' / 'workflow.py'
    pre.dagster = pre_artifacts / 'dagster'
    pre.executed_notebooks = {name: pre.executed / f'{name}.ipynb' for name in notebook_names}
    pre.timetable_executions = {
        mode: pre.executed / 'timetables' / f'{mode}.ipynb' for mode in ('bus', 'rail', 'tfl')
    }

    # Final preprocessing datasets consumed by analysis
    results = _files(
        root / 'results',
        slim_10 = 'slim_10.parquet',
        enriched_10 = 'enriched_10.parquet',
        slim_15 = 'slim_15.parquet',
        enriched_15 = 'enriched_15.parquet',
        slim_20 = 'slim_20.parquet',
        enriched_20 = 'enriched_20.parquet',
    )
    results.tables = _files(
        results.tables,
        primary = 'primary_associations.csv',
        spatial = 'spatial_dependence.csv',
    )
    results.accompanying = results.directory / 'accompanying'
    results.by_duration = {minutes: getattr(results, f'slim_{minutes}') for minutes in (10, 15, 20)}
    results.enriched_by_duration = {
        minutes: getattr(results, f'enriched_{minutes}') for minutes in (10, 15, 20)
    }

    # Analysis – outputs owned by each experiment
    experiments = {
        'associations/dose_response': _files(
            analysis_artifacts / 'associations/dose_response',
            quintile_contrasts_png = 'figures/quintile_contrasts.png',
            spline_predictions_png = 'figures/spline_predictions.png',
            quintile_contrasts_csv = 'tables/quintile_contrasts.csv',
            spline_tests_csv = 'tables/spline_tests.csv',
            spline_predictions_csv = 'tables/spline_predictions.csv',
        ),

        'associations/effect_modification': _files(
            analysis_artifacts / 'associations/effect_modification',
            interaction_models_csv = 'tables/interaction_models.csv',
            interaction_predictions_csv = 'tables/interaction_predictions.csv',
        ),

        'associations/primary': _files(
            analysis_artifacts / 'associations/primary',
            sequential_models_png = 'figures/sequential_models.png',
            residuals_parquet = 'residuals.parquet',
            sequential_models_csv = 'tables/sequential_models.csv',
            primary_csv = 'tables/primary.csv',
            unadjusted_correlations_csv = 'tables/unadjusted_correlations.csv',
        ),

        'geography/gradients_and_shortfalls': _files(
            analysis_artifacts / 'geography/gradients_and_shortfalls',
            boroughs_parquet = 'boroughs.parquet',
            spatial_parquet = 'spatial.parquet',
            summary_json = 'summary.json',
            component_piecewise_gradients_csv = 'tables/component_piecewise_gradients.csv',
            component_radial_gradients_csv = 'tables/component_radial_gradients.csv',
            component_sector_band_gradients_csv = 'tables/component_sector_band_gradients.csv',
            component_sector_band_means_csv = 'tables/component_sector_band_means.csv',
            component_sector_gradients_csv = 'tables/component_sector_gradients.csv',
            radial_curve_csv = 'tables/radial_curve.csv',
            radial_segments_csv = 'tables/radial_segments.csv',
            sector_band_csv = 'tables/sector_band.csv',
            sectoral_coefficients_csv = 'tables/sectoral_coefficients.csv',
            shortfall_summary_csv = 'tables/shortfall_summary.csv',
        ),

        'index/structure': _files(
            analysis_artifacts / 'index/structure',
            component_correlations_csv = 'tables/component_correlations.csv',
            contextual_correlations_csv = 'tables/contextual_correlations.csv',
            descriptives_csv = 'tables/descriptives.csv',
            index_structure_csv = 'tables/index_structure.csv',
            pca_variance_csv = 'tables/pca_variance.csv',
        ),

        'index/validation': _files(
            analysis_artifacts / 'index/validation',
            stockton_matched_scores_csv = 'tables/stockton_matched_scores.csv',
            stockton_correlations_csv = 'tables/stockton_correlations.csv',
            validation_csv = 'tables/validation.csv',
        ),

        'prediction/spatial_cross_validation': _files(
            analysis_artifacts / 'prediction/spatial_cross_validation',
            predictions_parquet = 'predictions.parquet',
            fold_membership_csv = 'tables/fold_membership.csv',
            spatial_cross_validation_csv = 'tables/spatial_cross_validation.csv',
            spatial_blocks_csv = 'tables/spatial_blocks.csv',
        ),

        'results/figures': _files(
            analysis_artifacts / 'results/figures',
        ),

        'results/tables': _files(
            analysis_artifacts / 'results/tables',
        ),

        'results/accompanying': _files(
            analysis_artifacts / 'results/accompanying',
        ),

        'robustness/index_definition': _files(
            analysis_artifacts / 'robustness/index_definition',
            index_scales_csv = 'tables/index_scales.csv',
            index_sensitivity_csv = 'tables/index_sensitivity.csv',
            rank_correlations_csv = 'tables/rank_correlations.csv',
        ),

        'robustness/qof_allocation': _files(
            analysis_artifacts / 'robustness/qof_allocation',
            qof_allocation_mc_distributions_png = 'figures/qof_allocation_mc_distributions.png',
            qof_allocation_coverage_csv = 'tables/qof_allocation_coverage.csv',
            qof_allocation_mc_coefficients_csv = 'tables/qof_allocation_mc_coefficients.csv',
            qof_allocation_mc_summary_csv = 'tables/qof_allocation_mc_summary.csv',
            qof_allocation_metadata_json = 'tables/qof_allocation_metadata.json',
            qof_allocation_samples_csv = 'tables/qof_allocation_samples.csv',
            qof_allocation_validation_csv = 'tables/qof_allocation_validation.csv',
        ),

        'robustness/regression_diagnostics': _files(
            analysis_artifacts / 'robustness/regression_diagnostics',
            residuals_png = 'figures/residuals.png',
            residual_distributions_png = 'figures/residual_distributions.png',
            vif_csv = 'tables/vif.csv',
            heteroskedasticity_csv = 'tables/heteroskedasticity.csv',
            hc3_models_csv = 'tables/hc3_models.csv',
            influential_observations_csv = 'tables/influential_observations.csv',
        ),

        'robustness/walkshed_duration': _files(
            analysis_artifacts / 'robustness/walkshed_duration',
            walkshed_sensitivity_png = 'figures/walkshed_sensitivity.png',
            walkshed_models_csv = 'tables/walkshed_models.csv',
            walkshed_rank_correlations_csv = 'tables/walkshed_rank_correlations.csv',
        ),

        'spatial/autocorrelation_and_error_models': _files(
            analysis_artifacts / 'spatial/autocorrelation_and_error_models',
            residual_maps_png = 'figures/residual_maps.png',
            global_moran_csv = 'tables/global_moran.csv',
            spatial_error_models_csv = 'tables/spatial_error_models.csv',
        ),

        'spatial/borough_fixed_effects': _files(
            analysis_artifacts / 'spatial/borough_fixed_effects',
            borough_models_csv = 'tables/borough_models.csv',
            borough_residual_moran_csv = 'tables/borough_residual_moran.csv',
        ),

        'spatial/centre_periphery_adjustment': _files(
            analysis_artifacts / 'spatial/centre_periphery_adjustment',
            centre_periphery_models_csv = 'tables/centre_periphery_models.csv',
        ),

        'spatial/conditional_null': _files(
            analysis_artifacts / 'spatial/conditional_null',
            conditional_null_draws_csv = 'tables/conditional_null_draws.csv',
            conditional_null_summary_csv = 'tables/conditional_null_summary.csv',
            null_calibration_csv = 'tables/null_calibration.csv',
            island_links_csv = 'tables/island_links.csv',
        ),
    }

    # Analysis – notebook locations are independent of experiment and artifact names
    notebook_locations = {
        'associations/dose_response': 'associations/nonlinearity',
        'associations/effect_modification': 'associations/interactions',
        'index/structure': 'walkability/structure',
        'index/validation': 'walkability/validation',
        'geography/gradients_and_shortfalls': 'walkability/geography',
        'spatial/autocorrelation_and_error_models': 'spatial/dependence',
        'spatial/borough_fixed_effects': 'spatial/boroughs',
        'spatial/centre_periphery_adjustment': 'spatial/radial',
        'prediction/spatial_cross_validation': 'spatial/cross_validation',
        'robustness/index_definition': 'sensitivity/index',
        'robustness/qof_allocation': 'sensitivity/qof',
        'robustness/regression_diagnostics': 'sensitivity/diagnostics',
        'robustness/walkshed_duration': 'sensitivity/walkshed',
    }

    study = SimpleNamespace(
        directory = analysis,
        artifacts = analysis_artifacts,
        experiments = experiments,
        notebooks = {
            notebook_locations.get(name, name): analysis / 'notebooks' / f'{notebook_locations.get(name, name)}.ipynb'
            for name in experiments
        },
        executed = {
            notebook_locations.get(name, name): analysis_artifacts / 'executed_notebooks' / f'{name}.ipynb'
            for name in experiments
        },
        dagster = analysis_artifacts / 'dagster',
        workflow = analysis / 'src' / 'workflow.py',
    )

    return SimpleNamespace(
        root = root,
        data = data,
        artifacts = artifacts,
        raw = raw,
        preprocessing = pre,
        analysis = study,
        results = results,
    )


paths = for_root(Path(__file__).resolve().parent)


def prepare_preprocessing():
    pre = paths.preprocessing
    
    directories = [
        pre.shared.directory,
        pre.shared.isochrones,
        pre.shared.subgraphs,
        pre.shared.archives,
        pre.transport.directory,
        pre.health.directory,
        pre.context.directory,
        pre.cache,
        pre.executed,
        paths.results.directory,
    ]
    directories.extend(
        path.parent
        for path in [
            pre.shared.amenities,
            pre.shared.osm_tags,
            pre.shared.epc,
            pre.shared.dwellings,
        ]
    )
    directories.extend(group.directory for group in pre.walkability.values())
    directories.extend(group.neighborhoods for group in pre.walkability.values())
    directories.extend(feed.directory for feed in pre.transport.feeds.values())
    
    for directory in directories:
        directory.mkdir(parents = True, exist_ok = True)


def experiment_paths(name):
    files = paths.analysis.experiments[name]
    for directory in (files.directory, files.tables, files.figures):
        directory.mkdir(parents = True, exist_ok = True)
   
    return files
