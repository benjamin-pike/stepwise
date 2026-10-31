# Source Data

[Overview](../README.md) · [Setup](setup.md) · [Source Data](data.md) · [Runbook](runbook.md)

Place source files in `data/` using the filenames below. All paths in this guide are relative to that directory. If you need to use a different location, change the corresponding entry in [`paths.py`](../paths.py).

Given their size and licensing terms, datasets are excluded from Git. Create any missing folders before adding files. Retain the original column names, since the notebooks use them to select fields.

## Required Data

For a full run, gather the required files listed below. Most can be downloaded directly from their linked providers. The EPC archive and Stockton scores need the preparation described below.

The health notebooks download the GP registration and QOF ZIPs themselves and reuse files already present. Street networks and amenity features are also downloaded during preprocessing. The raw Taginfo database and timetable feeds are [optional](#optional) and prepared versions of their outputs are included in the repository.

 Updated releases and new OpenStreetMap queries can produce different results from earlier runs.

## Shared Geography and Demographics

| File | Details|
| --- | --- |
| `shared/medsat_data.csv` | Use `point_data/2020_spatial_raw_master.csv` from the [MEDSAT dataset](https://doi.org/10.14459/2023mp1714817), linked from the [authors' repository](https://github.com/sanja7s/MedSat). Rename it `medsat_data.csv` and keep the published columns. |
| `shared/lsoa_lookup.csv` | Download the [ONS LSOA 2021 to ward and local authority 2022 lookup](https://www.data.gov.uk/dataset/19a01ab0-2111-4c29-8a89-a6dd14ba845c/lsoa-2021-to-electoral-ward-2022-to-lad-2022-best-fit-lookup-in-ew-v31) as CSV. Keep `LSOA21CD` and `LAD22NM`. |


## Walkability Index

| File | Details|
| --- | --- |
| `walkability/dwellings/epc_certificates.csv.zip` | Download domestic EPC records from the [UK Government bulk-data service](https://get-energy-performance-data.communities.gov.uk/), which requires sign-in. Combine and ZIP the records as described below. |
| `walkability/dwellings/os_uprn.gpkg` | Download **OS Open UPRN in GeoPackage format** from the [OS Data Hub](https://osdatahub.os.uk/downloads/open/OpenUPRN). Extract the GeoPackage. It must include the `UPRN` identifier and point geometry. |
| `walkability/land_use/tiles.tif` | Download the United Kingdom categorical GeoTIFF from the [OSMlanduse research dataset](https://doi.org/10.11588/DATA/IUTCDN). Use the 10-metre raster in `EPSG:3035`. Its class codes must match `CODE_TO_GENERAL_USE` in [land_use.ipynb](../preprocessing/notebooks/walkability/components/land_use.ipynb). |

To prepare the EPC archive:

1. Combine the domestic certificate CSVs into one file named `epc_certificates.csv`.
2. Keep the original headers, including `UPRN` and `BUILT_FORM`.
3. Put the CSV at the root of a ZIP named `epc_certificates.csv.zip`.


## Health

| File | Details |
| --- | --- |
| `health/qof/2021.zip` through `health/qof/2026.zip` | [qof.ipynb](../preprocessing/notebooks/health/qof.ipynb) downloads the six annual Quality and Outcomes Framework (QOF) releases. |
| `health/patients/2021.zip` through `health/patients/2026.zip` | [patients.ipynb](../preprocessing/notebooks/health/patients.ipynb) downloads the April registration snapshots from [NHS England](https://digital.nhs.uk/data-and-information/publications/statistical/patients-registered-at-a-gp-practice). |
| `health/lsoa_2011_to_2021.csv` | Download the [ONS 2011-to-2021 LSOA exact-fit lookup (V3)](https://www.arcgis.com/home/item.html?id=cbfe64cc03d74af982c1afec639bafd1) as CSV and save it at this path. Retain `LSOA11CD`, `LSOA21CD`, `CHGIND` and `LAD22CD`. |

## Deprivation, Vegetation, and Pollution

| File | Details |
| --- | --- |
| `context/imd/imd_2025.csv` | Download **File 7: All ranks, scores, deciles and population denominators** from the [English indices of deprivation 2025 release](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2025). |
| `context/vegetation/vegetation_indices_2023.csv` | Download [Small Area UK Vegetation Indices, summer 2023](https://data.geods.ac.uk/dataset/small-area-uk-vegetation-indices/resource/7213a70a-2a1e-4442-8adb-29d3f8dff060). |
| `context/pollution/nox.csv` | Download Defra's [2023 annual-mean NOx grid](https://uk-air.defra.gov.uk/datastore/pcm/mapnox2023.csv) (`mapnox2023.csv`). |
| `context/pollution/pm25.csv` | Download Defra's [2023 annual-mean PM2.5 grid](https://uk-air.defra.gov.uk/datastore/pcm/mappm252023g.csv) (`mappm252023g.csv`). |
| `context/pollution/ozone.csv` | Download Defra's [2023 ozone DGT120 grid](https://uk-air.defra.gov.uk/datastore/pcm/mapdgt12023.csv) (`mapdgt12023.csv`). |

## External validation

These files are required by the analysis validation notebook. They are not used during preprocessing.

| File | Detail |
| --- | --- |
| `validation/stockton.csv` | Download Stockton's [Walkability index scores for administrative areas in London](https://discovery.ucl.ac.uk/id/eprint/1537546/) from UCL Discovery. Export the output-area scores from the `.xls` workbook as CSV, retaining `oa_00_2001` and `OA_M1_raw`. |
| `validation/oa_2001_boundaries.gpkg` | Download the GeoPackage of [ONS Output Areas (December 2001) Boundaries EW BFE](https://www.data.gov.uk/dataset/48d55ccb-dd6b-4e72-a5c8-63f7ed1e350c/output-areas-december-2001-boundaries-ew-bfe1). |

## Optional

These files are only needed for the amenity classifications and transport frequencies, which are aleady supplied. The [workflow guide](runbook.md#optional) explains how to run the two manual preparation notebooks.

| File| Details |
| --- | --- |
| `walkability/poi/osm_tags.db` | Download `taginfo-master.db.bz2` from [OpenStreetMap Taginfo](https://taginfo.openstreetmap.org/download), decompress it and rename the SQLite database `osm_tags.db`. |
| `walkability/transport/gtfs_bus.zip` | Download the national static GTFS timetable ZIP from the [Department for Transport's Bus Open Data Service](https://findtransportdata.dft.gov.uk/dataset/bus-open-data---download-all-timetable-data--18335fb19c4) |
| `walkability/transport/atoc_rail.gz` | Register for [Network Rail's open data feeds](https://www.networkrail.co.uk/who-we-are/transparency-and-ethics/transparency/open-data-feeds/) and download a full CIF schedule, compressed with gzip. |
| `walkability/transport/transx_tfl.zip` | Get the Journey Planner timetable feed in TransXChange format from [TfL's open-data downloads](https://tfl.gov.uk/info-for/open-data-users/api-documentation). Save the XML ZIP as `transx_tfl.zip`. |

[qof-2021]: https://digital.nhs.uk/data-and-information/publications/statistical/quality-and-outcomes-framework-achievement-prevalence-and-exceptions-data/2020-21
[qof-2022]: https://digital.nhs.uk/data-and-information/publications/statistical/quality-and-outcomes-framework-achievement-prevalence-and-exceptions-data/2021-22
[qof-2023]: https://digital.nhs.uk/data-and-information/publications/statistical/quality-and-outcomes-framework-achievement-prevalence-and-exceptions-data/2022-23
[qof-2024]: https://digital.nhs.uk/data-and-information/publications/statistical/quality-and-outcomes-framework-achievement-prevalence-and-exceptions-data/2023-24
[qof-2025]: https://digital.nhs.uk/data-and-information/publications/statistical/quality-and-outcomes-framework-achievement-prevalence-and-exceptions-data/2024-25
[qof-2026]: https://digital.nhs.uk/data-and-information/publications/statistical/quality-and-outcomes-framework-achievement-prevalence-and-exceptions-data/2025-26
