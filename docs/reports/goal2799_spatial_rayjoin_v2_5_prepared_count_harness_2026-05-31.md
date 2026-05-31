# Goal2799 Spatial RayJoin v2.5 Prepared Count Harness

Date: 2026-05-31

Status: implemented locally with first OptiX pod evidence and external review.

Verdict: accept-with-boundary pending clean-from-Git rerun.

## Purpose

Goal2799 closes the current v2.5 manifest gap for Spatial RayJoin's Tier A count/parity track.

The v2.5 rule is primitive-first:

- keep RayJoin-style count/parity workloads on prepared generic RTDL/OptiX primitives;
- do not route a fused RT primitive through Triton just to use a partner;
- keep row materialization, overlay continuation, and grouped downstream processing as deferred Tier B device-resident continuation work.

This goal adds a canonical harness around the existing Spatial RayJoin prepared OptiX count route and records current pod evidence for:

- `pip`: point/closed-shape membership count;
- `lsi`: segment-pair intersection count;
- `overlay_seed`: shape-pair relation flag count.

## Files

| File | Purpose |
| --- | --- |
| `scripts/goal2799_spatial_rayjoin_v25_prepared_count_harness.py` | Canonical v2.5 harness for the three Spatial RayJoin prepared OptiX count workloads. |
| `tests/goal2799_spatial_rayjoin_v25_prepared_count_harness_test.py` | Focused regression test for the harness, manifest row, pod artifact, and claim boundary. |
| `src/rtdsl/v2_5_triton_app_migration.py` | Marks `spatial_rayjoin` as ready with the Goal2799 prepared count harness while keeping row/overlay work deferred to Tier B. |
| `docs/reports/goal2799_pod_artifacts/spatial_rayjoin_v25_prepared_count_optix_fixture.json` | First pod evidence artifact. |
| `docs/reports/goal2799_pod_artifacts/spatial_rayjoin_v25_prepared_count_optix_fixture.stdout` | Captured stdout from the first pod run. |

## Pod Environment

Pod SSH used:

```text
ssh root@69.30.85.171 -p 22167 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

Hardware and driver:

```text
NVIDIA RTX A5000, 570.211.01
```

OptiX setup:

```text
OPTIX_PREFIX=/root/vendor/optix-sdk make build-optix
RTDL_OPTIX_LIB=/root/rtdl_goal2785_work/build/librtdl_optix.so
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2785_work/build/librtdl_optix.so
PYTHONPATH=src:.
```

The first evidence run was executed on a pod checkout reset to `origin/main` at:

```text
72f6d8de15cd915c2e58323b95d7a029631b1367
```

The new Goal2799 script was copied into that checkout for the initial artifact run. A clean-from-Git rerun must follow after the goal commit is pushed.

## Evidence Command

```bash
timeout 600s python3 scripts/goal2799_spatial_rayjoin_v25_prepared_count_harness.py \
  --warmup 2 \
  --repeat 7 \
  --output docs/reports/goal2799_pod_artifacts/spatial_rayjoin_v25_prepared_count_optix_fixture.json \
  --fail-fast
```

## Results

All three workloads matched the CPU reference count.

| Workload | Generic Primitive | CPU Reference Count | Prepared OptiX Count | Prepared Query Median (ms) | Status |
| --- | --- | ---: | ---: | ---: | --- |
| `pip` | `POINT_CLOSED_SHAPE_MEMBERSHIP_2D` | 6 | 6 | 0.129229 | pass |
| `lsi` | `SEGMENT_PAIR_INTERSECTION_2D` | 1 | 1 | 0.143813 | pass |
| `overlay_seed` | `SHAPE_PAIR_RELATION_FLAGS_2D` | 0 | 0 | 0.008794 | pass |

Phase medians from the artifact:

| Workload | Query Pack (ms) | Static Shape Pack (ms) | Prepare Static Scene (ms) | Prepared Query (ms) |
| --- | ---: | ---: | ---: | ---: |
| `pip` | 0.007050 | 0.018688 | 0.166797 | 0.129229 |
| `lsi` | 0.023294 | n/a | 0.166541 | 0.143813 |
| `overlay_seed` | 0.027198 | 0.004607 | 0.009355 | 0.008794 |

## Boundary

This is Tier A count/parity evidence only.

Not claimed:

- not a public speedup claim;
- not a whole-app RayJoin reproduction;
- not a claim that RTDL beats the RayJoin paper implementation;
- not a Triton speedup claim;
- not a true zero-copy claim;
- not a row/overlay continuation closure.

The row/overlay continuation remains deferred Tier B work because the larger design question is still device-resident row-stream continuation and grouped downstream processing, not the prepared count/parity primitive itself.

## Current Manifest Update

`spatial_rayjoin` now records:

- `canonical_harness_status`: `ready_with_goal2799_prepared_count_harness`
- `pod_evidence_status`: `Goal2799 current OptiX prepared count evidence recorded for PIP, LSI, and overlay-seed count/parity rows`
- `next_action`: keep count/parity primitive-first and keep row/overlay output deferred to Tier B continuation work.

## Validation

Local validation completed before the pod run:

```text
py_compile: pass
validate_v2_5_tiered_benchmark_manifest: accept
```

External review:

```text
Claude: accept-with-boundary
Review: docs/reviews/goal2799_claude_review_spatial_rayjoin_prepared_count_harness_2026-05-31.md
Consensus: docs/reports/goal2799_spatial_rayjoin_v2_5_prepared_count_harness_consensus_2026-05-31.md
```

Focused tests were run after the report/review/consensus files were added.

Focused local test slice after report/review/consensus:

```text
tests.goal2790_hausdorff_tiled_dense_point_nearest_test
tests.goal2791_thresholded_partner_selection_guidance_test
tests.goal2792_partner_selection_explain_plan_test
tests.goal2793_v2_5_partner_role_reconciliation_test
tests.goal2794_v2_5_determinism_policy_test
tests.goal2795_v2_5_tier_label_reconciliation_test
tests.goal2796_raydb_scalar_reduction_selection_guidance_test
tests.goal2797_triangle_counting_v25_canonical_harness_test
tests.goal2798_librts_v25_warm_median_harness_test
tests.goal2799_spatial_rayjoin_v25_prepared_count_harness_test

47 tests run, 46 passed, 1 skipped.
```

Clean-from-Git pod validation remains pending.
