# V4 Goal4638 Catalog Regression GPU Gate After AABB

Status: `goal4638_catalog_regression_gpu_after_aabb_passed_not_release`

Decision: `accept_catalog_regression_gpu_gate_after_aabb_not_release`

Correction: this catalog GPU gate is valid release-hardening evidence, but it
is not the owner-approved Goal4638 exit gate. The controlling Goal4638 artifact
is `future/v4/v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md`.

## What Ran

Command on the RTX A5000 POD:

```bash
PYTHONPATH=src:. python3 scripts/v4_catalog_regression_gate.py \
  --mode gpu \
  --copies 8192 \
  --ray-count 8192 \
  --json-out future/v4/evidence/v4_goal4638_catalog_regression_gpu_after_aabb_2026-06-25.json \
  --md-out future/v4/evidence/v4_goal4638_catalog_regression_gpu_after_aabb_2026-06-25.md
```

Evidence:

- `future/v4/evidence/v4_goal4638_catalog_regression_gpu_after_aabb_2026-06-25.json`
- `future/v4/evidence/v4_goal4638_catalog_regression_gpu_after_aabb_2026-06-25.md`

## Result

- status: `passed`
- mode: `gpu`
- example count: `11`
- failed examples: `0`
- quickstart measured surfaces: `8`
- quickstart candidate surfaces: `0`
- quickstart measured partners: `numba`, `rtdl_native`, `torch`
- AABB example status: `measured`
- AABB backend: `optix`
- AABB correctness: `true`
- weighted-sum example status: `measured`
- release authorized: `false`

## Interpretation

This gate confirms that the post-AABB V4 front door, examples, planner, and
catalog remain runnable in GPU mode on the POD. It is release-hardening
evidence, not release authorization and not an all-application benchmark.

## Non-Authorization

This decision does not authorize V4 release, release-candidate wording, broad
V4 speedup claims, whole-app speedup claims, all-benchmark speedup claims,
public true-zero-copy claims, Tier-3 callback support, raw OptiX callback
support, CuPy performance claims, C ABI, embedding, non-Python host claims, or
app-specific native kernels.
