# Goal 23 Iteration 2 Implementation Report

## Scope

This iteration implements the bounded local executable slice defined in the Goal 23 setup.

It does not claim full RayJoin-paper dataset coverage. It executes only the currently runnable local slice while preserving the frozen Goal 21/22 provenance boundaries.

## Implemented Changes

### 1. Goal 23 runner and report path

Added [goal23_reproduction.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal23_reproduction.py).

This module now:

- executes the bounded local Figure 13 `lsi` analogue,
- executes the bounded local Figure 14 `pip` analogue,
- executes partial Table 3 bounded rows for the currently runnable County-family local analogues,
- executes bounded Table 4 overlay-seed analogue rows,
- derives the bounded Figure 15 overlay speedup analogue,
- and generates the final Goal 23 markdown/PDF report.

### 2. Goal 23 script and tests

Added:

- [goal23_generate_bounded_reproduction.py](/Users/rl2025/rtdl_python_only/scripts/goal23_generate_bounded_reproduction.py)
- [goal23_reproduction_test.py](/Users/rl2025/rtdl_python_only/tests/goal23_reproduction_test.py)

The tests validate a small-config path so the generation pipeline is verifiable without running the full bounded package.

### 3. Public API and Makefile

Updated:

- [__init__.py](/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py)
- [Makefile](/Users/rl2025/rtdl_python_only/Makefile)

The new public entry points are:

- `run_goal23_reproduction(...)`
- `generate_goal23_artifacts(...)`

## Executed Result

The full bounded package was executed successfully and generated:

- `/Users/rl2025/rtdl_python_only/build/goal23_reproduction/goal23_reproduction.json`
- `/Users/rl2025/rtdl_python_only/build/goal23_reproduction/table3_bounded_results.md`
- `/Users/rl2025/rtdl_python_only/build/goal23_reproduction/table4_overlay_results.md`
- `/Users/rl2025/rtdl_python_only/build/goal23_reproduction/figures/figure13_lsi_bounded.svg`
- `/Users/rl2025/rtdl_python_only/build/goal23_reproduction/figures/figure14_pip_bounded.svg`
- `/Users/rl2025/rtdl_python_only/build/goal23_reproduction/figures/figure15_overlay_speedup_bounded.svg`
- `/Users/rl2025/rtdl_python_only/build/goal23_reproduction/goal23_embree_reproduction_report.md`
- `/Users/rl2025/rtdl_python_only/build/goal23_reproduction/goal23_embree_reproduction_report.pdf`

Published snapshots were also written to:

- [goal23_embree_reproduction_report_2026-04-01.md](/Users/rl2025/rtdl_python_only/docs/reports/goal23_embree_reproduction_report_2026-04-01.md)
- [goal23_embree_reproduction_report_2026-04-01.pdf](/Users/rl2025/rtdl_python_only/docs/reports/goal23_embree_reproduction_report_2026-04-01.pdf)

## Measured Outcome

- total package wall time: `286.25 s`
- Table 3 executed rows: `4`
- Table 3 missing rows: `14`
- Table 4 executed rows: `2`
- Figure 13 records: `10`
- Figure 14 records: `10`

Important boundary:

- `County ⊲⊳ Zipcode` rows remain local analogues based on currently available county-side fixture/derived data, not acquired exact-input zipcode data.
- `Block ⊲⊳ Water` and all six continent Lakes/Parks families remain unexecuted and are explicitly marked missing.
- Table 4 / Figure 15 remain overlay-seed analogues, not full overlay materialization results.

## Verification

Executed:

- `cd /Users/rl2025/rtdl_python_only && PYTHONPATH=src:. python3 -m unittest tests.goal23_reproduction_test`
- `cd /Users/rl2025/rtdl_python_only && python3 -m py_compile src/rtdsl/goal23_reproduction.py scripts/goal23_generate_bounded_reproduction.py src/rtdsl/__init__.py`
- `cd /Users/rl2025/rtdl_python_only && PYTHONPATH=src:. python3 scripts/goal23_generate_bounded_reproduction.py`

## Current Position

This slice should close only if Claude and Gemini agree that:

1. the executed subset is labeled honestly,
2. the missing rows are explicit enough,
3. the final report preserves the Goal 21/22 provenance boundaries,
4. and the bounded runtime budget remains acceptable for the current Mac.
