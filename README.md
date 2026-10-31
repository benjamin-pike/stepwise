# Neighbourhood Walkability and Cardiometabolic Morbidity in Greater London: A Fine-Grained Spatial Analysis

This repository contains the code for our study of neighbourhood walkability and recorded cardiometabolic morbidity in Greater London.

The walkability index combines five measures: amenity access, dwelling density, land-use mix, street connectivity and public transport access. The main analysis uses 15-minute network walksheds, the areas reachable on foot along the street network.

General practice disease registers are used to estimate the prevalence of eight conditions in Lower-Layer Super Output Areas (LSOAs). The analyses relate these estimates to walkability, demographic composition, and environmental conditions, and examine how the associations change after accounting for the city's spatial structure.

## Getting started

1. [Set up the environment](docs/setup.md). Both workflows share one Python environment at the repository root.
2. [Gather the source data](docs/data.md). The guide lists the required files, download links and any preparation needed.
3. [Run the workflows](docs/runbook.md). Preprocessing creates the datasets; analysis produces the figures and tables.

From the repository root, start preprocessing with `./preprocessing/run.sh`. Once it has finished, start analysis with `./analysis/run.sh`. Each command starts Dagster. Launch the corresponding job from its web interface. Individual notebooks can also be run in Jupyter.

Source datasets and generated results are excluded from Git. The repository does include the amenity classifications and prepared transport frequencies, so there is no need to run their manual preparation notebooks unless you wish to update them.

## Repository

| Location | Contents |
| --- | --- |
| [`preprocessing/`](preprocessing/) | Notebooks and Python helpers that prepare neighbourhoods, walkability scores, health estimates, and context data |
| [`analysis/`](analysis/) | Notebooks and Python helpers for the statistical analyses, validation, figures, and tables |
| `data/` | Raw source files |
| `artifacts/` | Caches, working files, and copies of executed notebooks |
| `results/` | The six final parquet datasets, three figures, and CSV tables |
| [`paths.py`](paths.py) | Input and output paths for both workflows |
| [`pyproject.toml`](pyproject.toml) | Python dependencies for the whole project. |

See the [runbook](docs/runbook.md) for instructions on running the workflows.
