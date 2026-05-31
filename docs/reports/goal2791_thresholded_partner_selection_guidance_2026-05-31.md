# Goal2791 - Thresholded Partner-Selection Guidance

Date: 2026-05-31

## Purpose

Goal2790 changed the Hausdorff/X-HD partner story from purely negative to
thresholded:

- the tiled Triton dense point-nearest route is slower than Torch at 2K, 4K,
  and 8K dense shapes;
- the same route is faster than Torch at the measured 16K dense shape;
- a corrected 32K tiled-only pod probe completes in bounded memory, while the
  dense Torch baseline from the first probe OOMed.

Goal2791 turns that into explicit planner metadata instead of hidden dispatcher
behavior. The point is not to auto-select Triton. The point is to make the
evidence readable by code, reports, and future benchmark harnesses.

## What Changed

Updated:

- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`
- `tests/goal2791_thresholded_partner_selection_guidance_test.py`
- `docs/research/future_version_to_do_list.md`

The partner-selection registry now has five rows. The new row is:

| Operation | Workload shape | Evidence | Status | Selection rule |
| --- | --- | --- | --- | --- |
| `grouped_argmin_f64` | `dense_exact_hausdorff_tiled_nearest_then_global_max` | Goal2790 | `measured_mixed_preview_guidance` | do not auto-select; may be explicitly selected only as thresholded same-contract evidence |

The row records:

- ratio kind: measured Triton wall time divided by comparison Torch wall time;
- ratio interpretation: ratio below 1.0 means Triton is faster;
- measured ratio range from Goal2790: 0.745 to 19.61;
- faster measured shape count: 1;
- slower measured shape count: 3;
- all public, RT-core, whole-app, true-zero-copy, and release claims blocked.

The Hausdorff/X-HD app migration row now carries:

- two negative guidance rows from Goal2787 and Goal2788;
- one mixed thresholded guidance row from Goal2790;
- `auto_select_preview_partner_allowed: False`.

## Pod Probe

Artifact:

`docs/reports/goal2791_pod_artifacts/goal2791_hausdorff_32k_tiled_probe_pod_69_30_85_171_2026-05-31.json`

Host:

- `69.30.85.171:22167`
- GPU: NVIDIA RTX A5000

The first 32K probe attempted the dense Torch branch and recorded CUDA OOM. A
corrected probe then measured only the bounded tiled Triton path and checked
cross-block consistency.

| Source x target | Candidate block | Median seconds | Distance | Witness | Cross-block result |
| ---: | ---: | ---: | ---: | --- | --- |
| 32768 x 32768 | 512 | 0.060236 | 0.0101895 | 26659 -> 124236 | reference |
| 32768 x 32768 | 1024 | 0.047396 | 0.0101895 | 26659 -> 124236 | exact match |
| 32768 x 32768 | 2048 | 0.044876 | 0.0101895 | 26659 -> 124236 | exact match |
| 32768 x 32768 | 4096 | 0.044568 | 0.0101895 | 26659 -> 124236 | exact match |

This is useful bounded-memory evidence. It is not a same-contract Torch speedup
row at 32K because the Torch comparison did not complete.

## Boundary

Goal2791 authorizes:

- mixed/thresholded guidance metadata;
- explicit app/user partner choice for the tiled strategy;
- bounded-memory pod evidence for the 32K tiled route;
- no hidden planner dispatch.

Goal2791 does not authorize:

- public speedup claims;
- RT-core speedup claims;
- whole-app speedup claims;
- true zero-copy claims;
- v2.5 release readiness;
- automatic Triton selection.

The planner remains advisory. If a future auto-selector is added, it must record
the selected backend, partner, shape threshold, dtype, memory condition,
fallback reason, and claim boundary.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test

Ran 12 tests in 0.006s
OK

py_compile with PYTHONPYCACHEPREFIX=scratch\pycache_goal2791_local

OK
```

Full Goal2791 validation after report/review wiring:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2791_thresholded_partner_selection_guidance_test \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test

Ran 17 tests in 0.009s
OK
```

Pod clean-check validation after push:

```text
Host: 69.30.85.171
Port: 22167
Commit: f7202796

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2791_thresholded_partner_selection_guidance_test \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test

Ran 17 tests in 0.002s
OK
```

## Decision

`accept-with-boundary`

Consensus:

`docs/reports/goal2791_thresholded_partner_selection_guidance_consensus_2026-05-31.md`
