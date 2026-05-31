# Goal2796 - RayDB Scalar Reduction Selection Guidance

Date: 2026-05-31

## Purpose

Goal2796 uses the running RTX A5000 pod to refresh a current-commit RayDB v2.5
Triton public-front-door probe and make the result actionable in the partner
selection guidance.

The result is clear: the generic Triton scalar-reduction front door is correct,
but it is not the performance path for RayDB-style scalar grouped reductions on
the measured shapes. This should be machine-readable so planners and benchmark
apps do not auto-select Triton just because the preview kernel exists.

## Pod Artifact

Artifact:

- `docs/reports/goal2796_pod_artifacts/raydb_triton_frontdoor_current.json`

Pod:

- Host: `root@69.30.85.171`, port `22167`, key:
  `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`.
- GPU: NVIDIA RTX A5000, driver `570.211.01`, memory `24564 MiB`.
- Commit: `d0cd5a022408236c5274e2e21510451bb96df2c7`.
- Torch/Triton: Torch `2.8.0+cu128`, Triton `3.4.0`.

Command:

```text
PYTHONPATH=src:. python3 scripts/goal2683_raydb_triton_front_door_pod_runner.py \
  --row-counts 1024,65536,1048576 \
  --group-count 4096 \
  --repeats 5 \
  --output docs/reports/goal2796_pod_artifacts/raydb_triton_frontdoor_current.json
```

## Result Summary

All rows are correct versus Torch CUDA. Triton is slower than Torch CUDA for the
same post-RT scalar grouped reductions.

| Operation | Row Counts | Triton Slower Range |
| --- | --- | ---: |
| `segmented_count_i64` | 1K, 64K, 1M | 22.78x-38.04x |
| `segmented_sum_f64` | 1K, 64K, 1M | 38.29x-84.10x |
| `segmented_min_f64` | 1K, 64K, 1M | 44.84x-192.49x |
| `segmented_max_f64` | 1K, 64K, 1M | 36.00x-142.23x |

The composite `avg_as_sum_count` mode is also correct but slower
(`25.76x-39.88x`), and is covered by the count/sum guidance rows rather than a
separate primitive.

## Code Changes

Updated:

- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`

Added:

- `tests/goal2796_raydb_scalar_reduction_selection_guidance_test.py`
- pod artifacts under `docs/reports/goal2796_pod_artifacts/`

The RayDB app migration plan now carries four measured negative guidance rows
for `segmented_count_i64`, `segmented_sum_f64`, `segmented_min_f64`, and
`segmented_max_f64` with workload shape
`raydb_scalar_grouped_reduction_frontdoor`.

## Decision

`accept-with-boundary`

The correct v2.5 behavior is:

- keep the generic Triton scalar reductions as correct preview operations;
- keep RayDB scalar grouped reductions on the primitive-first/prepared fused
  RTDL path, or another explicitly selected same-contract partner;
- do not auto-select Triton for this shape until a future scalar-reduction
  design beats the same-contract comparison path.

## Claim Boundary

Still blocked:

- public speedup claims;
- whole-app speedup claims;
- release readiness;
- broad Triton-performance claims;
- treating the RayDB Triton front door as the default performance path.

This is negative selection guidance, not a release or performance promotion.

## Validation

Local validation:

- `py -3 -m py_compile src\rtdsl\v2_5_partner_selection_guidance.py src\rtdsl\v2_5_triton_app_migration.py tests\goal2782_v2_5_partner_selection_guidance_test.py tests\goal2783_v2_5_app_migration_selection_guidance_test.py tests\goal2796_raydb_scalar_reduction_selection_guidance_test.py` passed.
- `py -3 -m unittest tests.goal2796_raydb_scalar_reduction_selection_guidance_test tests.goal2782_v2_5_partner_selection_guidance_test tests.goal2783_v2_5_app_migration_selection_guidance_test tests.goal2792_partner_selection_explain_plan_test tests.goal2791_thresholded_partner_selection_guidance_test` passed:
  29 tests.

Pod execution evidence:

- The `goal2683_raydb_triton_front_door_pod_runner.py` command above completed
  on the RTX A5000 pod and wrote the Goal2796 artifact.

Pod clean-check validation from Git:

- Pod: `root@69.30.85.171`, port `22167`, key
  `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`.
- Commit: `faadc6edcd91fa6e1bcc11de142633cc034037cb`.
- Python: `3.12.3`.
- Command:

```text
git fetch origin main
git reset --hard origin/main
git clean -fd
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2796_raydb_scalar_reduction_selection_guidance_test \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test \
  tests.goal2792_partner_selection_explain_plan_test \
  tests.goal2791_thresholded_partner_selection_guidance_test
```

- Result: 29 tests passed.
