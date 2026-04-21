# Goal699 RTX Profile Report Generator

Date: 2026-04-21

Verdict: ACCEPT as a post-processing/reporting tool for Goal697/Goal698 raw
RTX profile JSON.

## Scope

Goal699 adds:

- `/Users/rl2025/rtdl_python_only/scripts/goal699_rtx_profile_report.py`
- `/Users/rl2025/rtdl_python_only/tests/goal699_rtx_profile_report_test.py`

The script reads Goal697 profiler JSON and writes a bounded Markdown report.
It is intended for the future cloud RTX validation artifacts created by:

- `/Users/rl2025/rtdl_python_only/scripts/goal698_rtx_cloud_validation_commands.sh`

## What It Computes

For each fixed-radius app pair, the report compares:

- default emitted row path total median time;
- summary path total median time;
- row/summary total-time ratio;
- default emitted row path backend/materialization median time;
- summary path backend/materialization median time;
- row/summary backend-time ratio.

Current app pairs:

- `outlier_detection`: `rows` versus `rt_count_threshold`
- `dbscan_clustering`: `rows` versus `rt_core_flags`

## Claim Gate

The script deliberately does not say that RTDL is faster just because a ratio
is greater than one.

It marks data as `eligible_for_rtx_claim_review: true` only when:

- `mode=optix`;
- `backend=optix`;
- all cases preserve oracle parity;
- the input profiler did not request a classification change.

Even then, this is only review eligibility. A human/AI release review must still
check the environment file and confirm RTX-class hardware before public speedup
claims are made.

Dry-run data and GTX 1070 data remain correctness/instrumentation evidence, not
RT-core performance evidence.

## Native Boundary

The report repeats the Goal697 native boundary: the current fixed-radius OptiX
ABI returns whole-call timing only. Packing, BVH build, OptiX launch, and
copy-back are not separately attributed.

## Example

```bash
PYTHONPATH=src:. python3 scripts/goal699_rtx_profile_report.py \
  --profile-json docs/reports/goal698_rtx_cloud_fixed_radius_phase_profile_YYYY-MM-DD.json \
  --environment docs/reports/goal698_rtx_cloud_environment_YYYY-MM-DD.txt \
  --output docs/reports/goal699_rtx_fixed_radius_interpretation_YYYY-MM-DD.md
```

## Local Verification

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal699_rtx_profile_report_test \
  tests.goal698_rtx_cloud_validation_runbook_test \
  tests.goal697_optix_fixed_radius_phase_profiler_test

PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal699_rtx_profile_report.py \
  tests/goal699_rtx_profile_report_test.py

git diff --check
```
