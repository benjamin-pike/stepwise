# Runbook

[Overview](../README.md) · [Setup](setup.md) · [Source Data](data.md) · [Runbook](runbook.md)

Complete the [environment setup](setup.md) and [gather the source data](data.md) first. Run all shell commands from the repository root.

There are two workflows: preprocessing builds the datasets, then analysis uses them to produce the study results. Both can be run through Dagster, which runs the notebooks in the required order and records their progress.

## Preprocessing

```sh
./preprocessing/run.sh
```

The script prepares the Python environment and starts Dagster. Open **http://127.0.0.1:3000**, select the `preprocessing` job and launch a run.

This builds the LSOA boundaries and walksheds, calculates the five walkability components, prepares the health and context data, and joins them into six final parquet files. Each component notebook runs once, reusing work where possible. Tasks run in series because the component notebooks already use multiple workers.

The `preparation/inputs` task checks that the supplied amenity classifications and transport frequencies are present. It does not run the annotation or timetable notebooks (those are only needed if you want to [update the supplied files](#optional)).

### Reruns

Starting another run executes the notebooks again. Existing output files do not automatically cause Dagster to skip a task (reuse depends on the cache checks inside each notebook).

The dwellings notebook reuses `dwellings_in_region.parquet` when present. The isochrone notebook checks its cached files for the required seeds and durations, rebuilding missing or invalid files. These caches avoid repeating the slowest preparation steps. Outputs written by later steps are replaced when those steps run.

Run only one preprocessing job at a time, since runs share the same caches and output paths. If you change the data or settings used to build a cache, remove the affected cache before rerunning as its presence does not guarantee it reflects those changes.

To repeat just the final join, select the **`results/analysis`** asset in Dagster and materialise it on its own. This runs `master.ipynb` and requires all of its input files to exist already.

## Analysis

Once preprocessing has finished:

```sh
./analysis/run.sh
```

Open **http://127.0.0.1:3001**, select the `study` job and launch a run.

Analysis reads the parquet files directly from `results/`. The main dataset is `enriched_15.parquet`. The walkshed sensitivity analysis uses the 10- and 20-minute walkability scores while keeping the health values and adjustment variables from the main dataset.

Keep `data/` after preprocessing. External validation still needs MEDSAT and the validation files, while the QOF sensitivity analysis needs the registration ZIPs and LSOA lookup. It also reads the prepared `artifacts/preprocessing/health/qof.csv` table, so keep that file too.

Analysis runs up to three tasks at a time. The final `results/figures`, `results/tables`, and `results/accompanying` tasks can run in parallel once their required analyses have finished.

## Progress and Failed Runs

Dagster shows the status and logs for each task. Each notebook runs in a fresh kernel using the project environment.

Copies of executed notebooks are saved under `artifacts/preprocessing/executed_notebooks/` and `artifacts/analysis/executed_notebooks/`. If a notebook fails, its saved copy includes the cells that completed before the error. Dagster's run history is stored in the corresponding `artifacts/preprocessing/dagster/` or `artifacts/analysis/dagster/` directory.

## Running Notebooks Directly

Activate the environment and start Jupyter from the repository root:

```sh
source .venv/bin/activate
jupyter lab
```

Choose **Python (stepwise)** as the notebook kernel and run cells from top to bottom. The installation makes the project imports available without changing the working directory. Notebooks use the same inputs and output paths in Jupyter and Dagster.

Run any notebooks that provide the inputs first. Most analysis notebooks can run once those datasets exist. The full dependencies are recorded in [preprocessing/src/workflow.py](../preprocessing/src/workflow.py) and [analysis/src/workflow.py](../analysis/src/workflow.py).

## Outputs

The top-level `results/` directory holds the datasets passed from preprocessing to analysis, along with the final figures and tables:

```text
results/
├── slim_10.parquet
├── enriched_10.parquet
├── slim_15.parquet
├── enriched_15.parquet
├── slim_20.parquet
├── enriched_20.parquet
├── figures/        # Three figures, each as PDF, SVG and PNG
├── tables/         # The two main manuscript tables, as CSV
└── accompanying/   # Supporting numerical results, as CSV
```

Each duration has a **slim** dataset containing the walkability and component scores, ranks, geometries, health outcomes and covariates. The **enriched** version also contains the detailed component measures. All six files include borough names (`LAD22NM`) and store `LSOA21CD` as both the index and a column.

The notebooks in [analysis/notebooks/results](../analysis/notebooks/results) generate the final outputs. Working tables, model outputs, maps, and caches are kept in `artifacts/`.

## Optional

The following intermediate files are included in Git:

```text
artifacts/preprocessing/walkability/shared/
├── amenities/osm_tags_grouped.json
└── transport/
    ├── transport_stop_frequency_bus.csv
    ├── transport_stop_frequency_rail.csv
    └── transport_stop_frequency_tfl.csv
```

These are the only generated files under `artifacts/`. They let you run preprocessing without first running `annotator.ipynb` or `timetables.ipynb`, as they are dependent on OpenAI's API and R, respectively.

To update them, use the notebooks in [preprocessing/notebooks/walkability/preparation](../preprocessing/notebooks/walkability/preparation). Both run manually, outside the DAG:

1. `annotator.ipynb` groups OSM tags into amenity categories. Supply the raw Taginfo database and set `OPENAI_API_KEY` in your terminal before starting Jupyter. The notebook replaces `osm_tags_grouped.json`.
2. `timetables.ipynb` calculates stop frequencies from the raw transport feeds. Run it three times, setting `SELECTED_MODE` to `'bus'`, `'rail'` and `'tfl'` in its configuration cell. Rail and TfL conversion use `Rscript` and [UK2GTFS](setup.md#optional). Converted GTFS files and frequency CSVs are saved under `artifacts/preprocessing/walkability/shared/transport/`.

The [data guide](data.md#optional) lists the raw files needed for these steps. Running either notebook overwrites its supplied outputs.
