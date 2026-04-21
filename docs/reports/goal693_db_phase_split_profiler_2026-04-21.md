# Goal693: DB Phase-Split Profiler

Date: 2026-04-21

Input:

- Goal692 DB/segment-polygon correctness and transparency:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal692_optix_db_segpoly_correctness_transparency_2026-04-21.md`

## Scope

This goal implements DB-2 from Claude's Goal691 action plan: a phase-split
profiler for the public unified database analytics app.

The profiler is intentionally diagnostic. It does not claim new OptiX speedups
or RT-core acceleration.

## Added

Script:

- `/Users/rl2025/rtdl_python_only/scripts/goal693_db_phase_profiler.py`

Examples:

```bash
PYTHONPATH=src:. python scripts/goal693_db_phase_profiler.py \
  --scenario sales_risk \
  --backend cpu \
  --iterations 3
```

```bash
PYTHONPATH=src:. python scripts/goal693_db_phase_profiler.py \
  --scenario regional_dashboard \
  --backend cpu_reference \
  --iterations 3
```

Linux/OptiX command for later backend validation:

```bash
PYTHONPATH=src:. python scripts/goal693_db_phase_profiler.py \
  --scenario all \
  --backend optix \
  --iterations 5
```

## Phase Coverage

For `regional_dashboard`, the profiler records:

- `python_input_construction`
- `backend_selection`
- `native_prepare_dataset` for prepared RT backends
- `query_conjunctive_scan_and_materialize`
- `query_grouped_count_and_materialize`
- `query_grouped_sum_and_materialize`
- `native_close_dataset`
- `cpu_reference_execute_and_postprocess` for CPU reference mode
- `total`

For `sales_risk`, the profiler records:

- `python_input_construction`
- `query_conjunctive_scan_and_materialize`
- `query_grouped_count_and_materialize`
- `query_grouped_sum_and_materialize`
- `python_postprocess`
- `total`

This split is not perfect native-internal profiling. In particular,
`query_*_and_materialize` includes native execution plus copy-back and Python
row materialization where the runtime returns Python rows. That is intentional:
the goal is to expose user-visible bottlenecks before deeper native
instrumentation.

## Boundary

`database_analytics` remains classified as `python_interface_dominated`.

The profiler can be run with `--backend optix`, but an OptiX result is not an
RT-core claim unless the run is on RTX-class NVIDIA hardware and the dominant
operation is verified to be OptiX traversal rather than Python/interface work.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal693_db_phase_profiler_test \
  tests.goal692_optix_app_correctness_transparency_test
```

Static checks:

```bash
python3 -m py_compile \
  scripts/goal693_db_phase_profiler.py \
  tests/goal693_db_phase_profiler_test.py
git diff --check
```

## Next

The next DB performance goal should use this profiler on the Linux OptiX host,
then implement the highest-impact native summary or prepared-columnar
optimization shown by the phase split.

## External Review

Claude finish review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal693_claude_finish_review_2026-04-21.md`
- Verdict: ACCEPT.

Claude confirmed that the profiler is useful, bounded, and does not overstate
OptiX RT-core acceleration.
