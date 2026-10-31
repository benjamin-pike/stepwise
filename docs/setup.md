# Setup

[Overview](../README.md) · [Setup](setup.md) · [Source Data](data.md) · [Runbook](runbook.md)

Run the shell commands below from the repository root in a macOS or Linux terminal.

## Python

Install **Python 3.12** before creating the environment. Check that it is available in your terminal:

```sh
python3.12 --version
```

## Virtual Environment

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m ipykernel install --user --name stepwise --display-name "Python (stepwise)"
```

This installs the project and its dependencies from `pyproject.toml`, and registers **Python (stepwise)** as a Jupyter kernel.

For later sessions, activate the environment with:

```sh
source .venv/bin/activate
```

Both `run.sh` scripts create or reuse `.venv` and install the project before starting Dagster. They do not register the Jupyter kernel, so complete the setup above to run notebooks in Jupyter.

Next, follow the [source data guide](data.md), then [run the workflows](runbook.md).

## Optional

The repository includes prepared bus, rail, and TfL stop frequencies. R is only needed if you want to regenerate the rail or TfL files.

For that step, install [R](https://cran.r-project.org/) and check that `Rscript` is available in the terminal used to start Jupyter:

```sh
Rscript --version
```

Then install [UK2GTFS](https://github.com/ITSLeeds/UK2GTFS), which converts the source timetables to GTFS. Run these commands in R:

```r
install.packages("remotes", repos = "https://cloud.r-project.org")
remotes::install_github("ITSLeeds/UK2GTFS")
```

UK2GTFS uses the R package `sf`. If it needs to be compiled on your system, install GDAL, GEOS, and PROJ, and the build tools described in the [sf installation instructions](https://r-spatial.github.io/sf/#installing).

The [workflow guide](runbook.md#optional) explains how to run the timetable notebook.
