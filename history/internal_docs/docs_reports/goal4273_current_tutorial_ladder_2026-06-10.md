# Goal4273 Current Tutorial Ladder

Status: local documentation update for current v2.10 learner guidance.

## Purpose

The tutorial directory already had useful current pages, but it read like a
reference pile rather than a beginner path. Goal4273 adds a short ordered
learning ladder that starts from source-tree execution and ends with a real
Python+RTDL+CuPy/Numba benchmark-app walkthrough.

The goal is learner clarity:

```text
first run -> mental model -> primitive discovery -> app split -> partner choice
-> measurement -> benchmark app
```

## Files Updated

| File | Previous learner problem | Action |
| --- | --- | --- |
| `docs/tutorials/current/README.md` | No concise current tutorial landing page existed. | Added the canonical seven-step current v2.10 tutorial track. |
| `docs/tutorials/current/01_source_tree_first_run.md` | Beginners had to infer source-tree setup from several pages. | Added a minimal first-run tutorial with Windows and Linux/macOS commands. |
| `docs/tutorials/current/02_kernel_shape_and_backends.md` | Backend choice and kernel shape were spread across reference docs. | Added the `input -> traverse -> refine -> emit` mental model and backend boundary. |
| `docs/tutorials/current/03_primitives_and_discovery.md` | Discovery was not placed early enough in the learner path. | Added search-before-create guidance and the primitive discovery command. |
| `docs/tutorials/current/04_python_app_structure.md` | App/engine boundary was implicit for new users. | Added a simple app structure that keeps app meaning in Python and engine contracts generic. |
| `docs/tutorials/current/05_partner_columns_cupy_numba.md` | Partner guidance existed but was not taught as a tutorial step. | Added explicit CuPy/Numba choice rules and starter commands. |
| `docs/tutorials/current/06_prepared_execution_measurement.md` | Measurement guidance was easy to miss. | Added setup/prepare/warmup/steady-state/validation separation. |
| `docs/tutorials/current/07_benchmark_app_python_rtdl_partner.md` | No final beginner tutorial connected RTDL to a full benchmark app with partners. | Added an RT-DBSCAN-style walkthrough from CPU oracle to RTDL rows, CuPy, Numba, and optional OptiX. |
| `docs/tutorials/README.md` | The front page listed many pages but did not give newcomers one ordered route. | Added a guided-track table first, then kept existing reference tutorials below. |
| `docs/learn/README.md` | The learning path pointed at the tutorial directory generally. | Promoted the current tutorial track to step 2. |
| `tests/goal4273_current_tutorial_ladder_test.py` | No regression guard protected the new tutorial shape. | Added checks for file presence, front-door links, local link validity, current example paths, and partner coverage. |

## Learner Boundary

The new track is deliberately current-version only. It does not teach older
version migration history, does not use `examples/v2_0`, and does not mention
Triton or PyTorch. It teaches the current v2.10 user surface:

- source-tree Python execution;
- generic RTDL primitives;
- explicit backend choice;
- explicit CuPy or Numba partner continuation;
- prepared measurement discipline;
- benchmark-app execution with CPU, RTDL, partner, and optional OptiX routes.

## Smoke Commands

These commands were run locally from the repository root:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\current\getting_started\rtdl_hello_world.py
$env:PYTHONPATH='src;.'; py -3 examples\current\getting_started\rtdl_primitive_discovery_workflow.py
$env:PYTHONPATH='src;.'; py -3 examples\current\research_benchmarks\rt_dbscan\rtdl_rt_dbscan_benchmark_app.py --mode cpu_reference --dataset tiny --include-rows
$env:PYTHONPATH='src;.'; py -3 examples\current\research_benchmarks\rt_dbscan\rtdl_rt_dbscan_benchmark_app.py --mode rtdl_cpu_rows --dataset tiny --include-rows
```

All four commands completed and produced expected learner output. The RT-DBSCAN
CPU oracle and RTDL row route both reported `matches_reference: true` on the
tiny dataset.

## Regression Test

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4273_current_tutorial_ladder_test
```

The test protects the current tutorial ladder from link drift, old example
paths, version soup, and missing CuPy/Numba benchmark-app coverage.
