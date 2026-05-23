# Goal2467 - Grouped-stream baseline on Blackwell pod

Date: 2026-05-20

Status: pod baseline collected for Goal2467 planning. This is not a native
Goal2467 implementation and does not authorize a Goal2467 performance claim.

## Pod

Connection used from Mac Codex:

```text
ssh root@213.173.109.172 -p 36585 -i ~/.ssh/id_ed25519_rtdl_codex
```

Environment:

```text
GPU: NVIDIA RTX PRO 4000 Blackwell
Driver: 580.159.04
CUDA: /usr/local/cuda-12.8, nvcc 12.8
OptiX SDK: /root/vendor/optix-sdk
Source base: a9193856547bf692069955a3dbaf6c3e00c09b1b
```

The pod workspace used `origin/main` plus the Mac-local Goal2467 overlay files.

## Validation

Static/focused tests on pod:

```text
tests.goal2467_blocked_grouped_continuation_design_test
tests.goal2465_grouped_union_all_items_intersection_cull_test
tests.goal2463_grouped_union_all_items_path_test
tests.goal2461_grouped_stream_self_query_device_path_test

Ran 17 tests in 0.012s - OK
```

Tiny real OptiX grouped-stream smoke:

```text
mode = optix_rt_core_grouped_stream_cupy_components_3d
dataset = tiny
matches_reference = true
```

Replayable runner smoke on the same pod:

```text
python3 scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --output-dir /tmp/goal2467_runner_smoke \
  --point-count 96 \
  --repeat-count 2

signatures_match = true
tiny_smoke_matches_reference = true
```

## Baseline Results

Artifacts:

- `scripts/goal2467_grouped_stream_baseline_pod_runner.py`
- `docs/reports/goal2467_grouped_stream_baseline_pod/summary.json`
- `docs/reports/goal2467_grouped_stream_baseline_pod/clustered3d_32768_grouped_stream.json`
- `docs/reports/goal2467_grouped_stream_baseline_pod/clustered3d_65536_grouped_stream.json`

Five repeats per point count; tail medians exclude repeat 1.

| clustered3d points | total tail median sec | native grouped-union tail median sec | predicate mode |
| ---: | ---: | ---: | --- |
| 32,768 | 0.070247 | 0.024729 | predicated grouped union |
| 65,536 | 0.163915 | 0.069710 | all-items grouped union |

Both rows reported `signatures_match = true`.

Compared with the earlier RTX A5000 Goal2465 artifact, this Blackwell pod shows
faster native grouped-union time but slower total elapsed time for these rows.
That difference should not be read as a regression or speedup claim because the
hardware and environment changed and the total path includes host-visible label
materialization.

## Simulator Sample

The Mac-local Goal2467 simulator sample was reproduced on the pod:

```text
hit_stream_pair_count = 562
predicate_true_count = 60
segment_count = 9
max_segment_hits = 64
baseline_global_parent_atomic_attempts = 382
global_parent_atomic_attempts = 289
global_parent_atomic_successes = 56
deduplicated_union_proposals = 289
proposal_rejection_rate = 0.24345549738219896
fallback_to_unblocked_grouped_union = false
```

This is reference-only telemetry, not native performance evidence.

## Boundary

- No Goal2467 native ABI was added.
- No blocked/segmented native path was implemented.
- No Goal2467 performance claim is authorized.
- This pod run establishes the current Goal2465-compatible baseline and
  confirms the Goal2467 simulator/telemetry contract on the GPU pod.

Next implementation work should compare a native fixed-budget
blocked/segmented grouped-union prototype against this baseline on the same pod.
