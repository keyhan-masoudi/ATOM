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

- 259 tracked files, including 99 Python files (20,001 lines).
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
