# ATOM

Awareness-Driven Task Offloading for Mixed-Class Real-Time Tasks in Vehicular Fog Computing.

The simulator combines vehicle, fog, and cloud execution with hard/soft task
scheduling, environmental noise, traffic prediction, and multiple offloading
policies. This repository also contains the research data-preparation and
analysis scripts used around the simulator.

## Repository layout

```text
main.py                      Simulation entry point and experiment combinations
config.py                    Simulation settings and runtime path configuration
controllers/
  loader.py                  XML input loading and policy selection
  metrics.py                 Metric collection and exports
  noise_selection.py         Communication-aware executor selection
  simulators/                Base simulator and algorithm-specific variants
  zone_managers/             Heuristics and deep_rl/ddpg/ddpg_new/maddpg/mappo/ppo/sac
models/                      Task, zone, vehicle, fog, and cloud models; EDF/ITBS
utils/                       Clock, enums, XML parsing, distance, and shared paths
environment/                 Noise, geometry, canonical partitions, weather generation
preprocessing/               Task/vehicle generation, XML splitting, traffic caches
prediction/
  with_weather/              Weather-aware predictors, trainers, benchmarks, checkpoints
  without_weather/           Earlier predictors, trainer, and checkpoints
analysis/                    Metric merging, traffic reports, plots, data inspection
data/
  caches/                    Precomputed traffic, weather, spatial, prediction caches
  datasets/                  Tracked traffic CSV datasets
  prediction_data/           Existing per-time prediction CSV files
  reports/                   Retained report and visualization artifacts
  vehicles/                  Local generated XML chunks (ignored)
  tasks/                     Local generated soft-task XML chunks (ignored)
  hard_tasks/                Local generated hard-task XML chunks (ignored)
docs/                        Design notes, refactor scope, and file migration map
tests/regression/            Self-contained behavior and structure checks
```

Python module and package filenames use lowercase `snake_case`. Existing public
class/method names, algorithm labels, XML attributes, metric columns, and
checkpoint tensor keys are preserved. Models remain under `models/` to keep their
existing import identities.

## Setup

Use Python 3.11 or newer (`typing.Unpack` is used by the policies).

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For training, prediction, and prediction-accuracy analysis, also install:

```sh
python -m pip install -r requirements-prediction.txt
```

Run commands from the repository root. Standalone tools now run as modules with
`python -m package.module`; this lets them import the shared code without adding
machine-specific directories to the Python search path.

## Simulation

```sh
python main.py
```

Select experiment combinations in `main.py` and settings in `config.py`. All 13
existing policies remain available: Random, Heuristic, Only Cloud, Only Fog,
Only Local, DeepRL, DDPG, DDPGNew, PPO, SAC, MADDPG, MAPPO, and Greedy.

A complete experiment needs the original local XML inputs: the chosen city's
`data/*.zon.xml` and `data/*.fn.xml`, plus the relevant `chunk_<n>.xml` files under
`data/vehicles`, `data/tasks`, and `data/hard_tasks`. These large generated inputs
are ignored by Git and are not supplied by a fresh clone. The default Melbourne
experiment still covers steps 2600–3599 with 100-step input chunks.

Hard-task generation expects `data/hard_task_parameters_uunifast.json`. The named
`data/hard_task_parameters_uunifast_u*c*.json` files are preserved scenario inputs;
select the intended scenario explicitly or generate the active file. The
refactor does not automatically choose a scenario or alter fallback behavior
when that file is absent.

`utils/paths.py` locates the repository and its data directories. Existing
`Config.Paths` and `Config.VehiclesTraffic` attributes remain available, with
checkout-relative defaults instead of contributor-specific Windows locations.

Simulation outputs retain their existing names and root-relative directories:
`Results`, `Results_Success`, `Results_Metrics`, `convergence`, and `Gantt`.

## Common tools

| Purpose | Command from the repository root |
| --- | --- |
| Generate hard-task parameters | `python -m preprocessing.task_parameters --help` |
| Generate vehicles and tasks | `python -m preprocessing.task_and_user_generator` |
| Split generated raw XML | `python -m preprocessing.split_xml` |
| Generate zones and fixed fogs | `python -m preprocessing.zone_manager_generator` |
| Produce traffic CSV chunks | `python -m preprocessing.traffic_csv` |
| Build the traffic cache | `python -m preprocessing.traffic_cache` |
| Build the spatial grid | `python -m preprocessing.precalculate_spatial_grid` |
| Build weather cache | `python -m preprocessing.precalculate_weather` |
| Build vehicle prediction cache | `python -m preprocessing.precalculate_vehicle_predictions` |
| Inspect dynamic traffic | `python -m preprocessing.vehicle_traffic` |
| Weather-aware prediction | `python -m prediction.with_weather.one_file_predictor` |
| Convert hex predictions to partition cache | `python -m prediction.with_weather.hex_to_partition` |
| Sequential prediction benchmark | `python -m prediction.with_weather.benchmark_sequential` |
| Merge experiment metrics | `python -m analysis.merge_metrics` |
| Plot convergence | `python -m analysis.plot_convergence` |
| Generate traffic report | `python -m analysis.traffic_report` |
| Plot traffic density | `python -m analysis.plot_traffic_density` |

These are the existing research scripts: inspect their input settings before
running them. Some scripts execute work when imported, and some require external
scenario files such as `testfile/final300.csv` or
`data/datasets/new_traffic_dataset1.csv`. These files were already absent from the
tracked repository; they are not substituted with other datasets. Trainers write
to their configured checkpoint directories, as before.

`preprocessing.vehicle_traffic` retains its original inspection entry point.
To generate its cache, call its existing `main()` explicitly:

```sh
python -c 'from preprocessing.vehicle_traffic import main; main()'
```

The hex prediction converter and vehicle prediction precomputation share
`data/caches/hex_traffic_predictions.pkl`. The two previous identical copies were
consolidated. CSV traffic intermediates now live under `data/caches/traffic_csv`.

## Verification and review

```sh
python -m unittest discover -s tests/regression -v
```

The regression suite uses explicit fixtures, without requiring the full local
simulation dataset. It covers scheduling, hard-task generation, metrics, short
runs of every policy, exact-case local imports, dynamic partition loading, and
cache locations. The simulation fixture was captured from `develop` before the
refactor; floating-point comparisons allow a small platform tolerance.

See [refactoring notes](docs/refactoring.md) for verification limits and removal
decisions, [the complete file migration map](docs/file_migration.tsv) for old/new
paths, and [the existing Persian offloading design notes](docs/offloading_design_fa.md)
for background. Scientific corrections and experiment changes are separate work.
