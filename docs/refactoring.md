# Repository structure refactor

Base: `develop` at `de930c6`. Review branch: `fixing-codebase-structure`.

## Scope and order

1. Capture deterministic scheduling, task-generation, and metric behavior.
2. Group simulator variants, normalize policy package names, and centralize environment code.
3. Group preprocessing, prediction, and analysis tools; relocate their assets and update producers and consumers together.
4. Remove verified duplicate/dead definitions, document commands and migration paths, and verify the resulting tree.

Scheduling, rewards, algorithm selection, numeric configuration, random draw order,
checkpoint tensor layouts, and output schemas are outside the scope of changes.
Public class/method names and algorithm labels remain intact. Python module paths
change with the directory layout; use the migration table for external scripts.
`main.py` remains the simulation entry point. Existing local untracked files are
not part of this refactor.

## Baseline observations

- 259 tracked files, including 105 Python files (20,001 lines).
- The three generated partition modules have identical definitions after imports
  are excluded. Two are byte-identical; the third uses short sibling imports.
- Both DDPG variants, all predictor/trainer variants, and all model checkpoint
  collections have distinct implementations or contents. Keep them.
- `final_model300 copy` is not a duplicate model: only its statistics file matches.
- The untracked `tests/test_itbs.py` has five passing checks and one pre-existing
  missing-file error for `data/hard_task_parameters_uunifast.json`. Named scenario
  files exist, but choosing one automatically would change the experiment.
- Original runtime paths point at a contributor's Windows checkout. Paths must
  follow the repository layout; scientific settings must stay unchanged.
- The paper review raises scientific issues. This change does not correct metrics,
  scheduler formulas, learning algorithms, or experiment settings.

## Final structure and removal decisions

- `controllers/simulators/` contains the base simulator and every algorithm variant.
- Policy packages use lowercase names; shared multi-agent helpers are in
  `controllers/zone_managers/multi_agent.py`.
- `environment/` contains noise settings, geometry, generators, and the one
  canonical `partitions.py`. Both redundant partition files were removed only
  after checking that all class and function definitions matched.
- `preprocessing/`, `prediction/`, and `analysis/` separate data generation,
  learned prediction, and result inspection. Python files were removed from
  data directories. The original Persian design document is in `docs/`.
- Caches, datasets, and retained reports are under `data/`. The root
  `HexTraffic_Prediction_data.pkl` and weather predictor's `hex_data.pkl` were
  byte-identical; their producers and consumers now use one canonical cache.
- Two identical earlier method definitions (`load_tasks` and
  `_assign_hard_task_locally`) were removed from the base simulator. Python
  already used their identical later definitions.
- Contributor-specific absolute path blocks and manual `sys.path` additions
  were replaced with package imports and repository-derived paths.
- No distinct algorithm, training variant, checkpoint set, scenario, or report
  was deleted. The empty traffic CSV placeholders were retained under
  `data/datasets/` because their names are referenced by research scripts.

The full file-level mapping is in [file_migration.tsv](file_migration.tsv).
Rename detection may pair identical empty files or identical statistics files
arbitrarily in Git's display; the migration table records the intended mapping.

## Verification performed

- Ten regression tests pass, including an eight-step synthetic simulation of
  all 13 registered policies. The fixture includes a vehicle, mobile fog, fixed
  fog, cloud, hard/soft arrivals, noise, and task completion/reward processing.
  Per-step metrics, completion/miss records, and convergence records match the
  original `develop` run exactly in the validation environment.
- Both unified EDF/ITBS and parallel-frequency scheduler traces match captured
  baseline hashes. Seeded UUniFast/WFD output and metric columns match as well.
- All original Python sources were mapped to their new locations and parsed.
  Comparison of 826 qualified function/method definitions after normalizing imports, documentation, and
  explicit cache-path substitutions found only three remaining changes: the
  generated partition import header, traffic CSV intermediate directory, and
  generated metrics image path. Each is a location change.
- Exact-case local import resolution and compilation cover every Python module
  in the reorganized source packages. `main` imports all simulator variants.
- Every original non-code dataset, report, scenario, and model asset is
  byte-identical at its mapped location, including both names consolidated into
  the shared hex prediction cache.
- All five simulator cache-loading methods successfully read the moved real
  caches: 3,301 traffic steps, 3,301 vehicle traffic steps, 3,601 weather steps,
  162,272 spatial cells, and 3,301 vehicle prediction steps.
- All ten predictor/trainer network variants produce identical forward outputs
  before and after relocation for fixed seeded synthetic inputs. Model classes
  were loaded separately from script entry points to avoid retraining or
  overwriting artifacts. All 18 saved tensor checkpoint files load on CPU.

## Limits and existing issues deliberately preserved

This is evidence of preserved behavior for the tested cases, not proof for
all possible experiments. Full-duration research experiments and learning
convergence were not rerun. The eight-step fixture does not exercise long
training updates, and prediction checks do not establish forecast accuracy.

The repository omits generated XML scenario inputs, the active unnamed hard-task
parameter JSON, and some prediction datasets. The existing untracked ITBS test
still has its original missing-file failure. It was neither modified nor added
to this branch. The tracked regression tests use controlled inputs instead.

`analysis.merge_metrics` retains the original signed sum labeled `Tardiness`.
The separate tardiness script still computes its existing clipped metric.
The paper's scientific concerns, reward formulations, model architectures,
DDPG variants, and scheduling equations were not changed.

Several standalone research scripts still execute work on import. Their
`python -m` entry points preserve the original script behavior; future API
cleanup should be reviewed separately. External callers using old module paths
need the migration table. Saved state-dict checkpoints remain compatible;
external pickles containing old Python class-module names were not supplied
and are not covered by these checks.

Existing simulation output folder names and filenames are preserved. The metric
merger's pre-existing `Results_success`/`Results_Success` capitalization mismatch
is recorded here rather than mixed into the scientific output comparison.

## Review sequence

1. Baseline regression checks and refactor scope.
2. Simulator, policy, and environment module moves and import rewiring.
3. Research tool and asset moves, path rewiring, duplicate removal, and optional
   prediction dependency list.
4. Cross-policy regression fixture, structure checks, and migration documentation.

The branch is intended for review without merging or modifying `develop`.
