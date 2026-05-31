# Goal2800 RTNN v2.5 Live Ranked-Summary Harness

Date: 2026-05-31

Status: implemented, reviewed, and clean-from-Git pod validated.

Verdict: accept-with-boundary.

## Purpose

Goal2800 replaces the RTNN manifest row's historical-artifact dependency with a current live harness.

The target is narrow:

- generate deterministic 3-D RTNN-shaped point clouds;
- run RTDL/OptiX exact fixed-radius ranked-summary rows;
- run the stronger same-contract CuPy grid CUDA-core opponent;
- compare candidate counts with an explicit float32 boundary tolerance;
- record that this is not a speedup claim, not a full RTNN reproduction, and not a native app customization.

This is Tier B benchmark-app evidence. It is meant to keep RTNN honest in v2.5, not to claim RTDL beats the RTNN paper or the optimized CuPy grid baseline.

## Files

| File | Purpose |
| --- | --- |
| `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py` | Live RTNN v2.5 harness over current RTDL/OptiX and optional CuPy grid same-contract opponent. |
| `tests/goal2800_rtnn_v25_live_ranked_summary_harness_test.py` | Focused regression test for the harness, manifest row, pod artifact, and boundary wording. |
| `src/rtdsl/v2_5_triton_app_migration.py` | Marks `rtnn` as ready with the Goal2800 live harness and keeps dense top-k Triton auto-selection blocked. |
| `docs/reports/goal2800_pod_artifacts/rtnn_v25_live_ranked_summary_65536.json` | First pod evidence artifact. |
| `docs/reports/goal2800_pod_artifacts/rtnn_v25_live_ranked_summary_65536.stdout` | Captured stdout from the first pod run. |
| `docs/reports/goal2800_pod_artifacts/rtnn_v25_live_ranked_summary_65536_clean_from_git.json` | Clean-from-Git pod evidence artifact after the Goal2800 commit was pushed. |
| `docs/reports/goal2800_pod_artifacts/rtnn_v25_live_ranked_summary_65536_clean_from_git.stdout` | Captured stdout from the clean-from-Git pod run. |

## Pod Environment

Pod SSH used:

```text
ssh root@69.30.85.171 -p 22167 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

Hardware and driver:

```text
NVIDIA RTX A5000, 570.211.01
```

Runtime:

```text
CuPy 14.1.0
RTDL_OPTIX_LIB=/root/rtdl_goal2785_work/build/librtdl_optix.so
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2785_work/build/librtdl_optix.so
PYTHONPATH=src:.
```

The first evidence run was executed on a pod checkout at:

```text
6da008bc
```

The new Goal2800 script was copied into that checkout for the first artifact run. That boundary was closed by the clean-from-Git rerun below.

The clean-from-Git rerun was executed after the Goal2800 commit was pushed, on a pod checkout reset to `origin/main` at:

```text
a22d388f1826c9e892f8b8a26196c8f0963c90e4
```

## Evidence Command

```bash
timeout 1200s python3 scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py \
  --point-count 65536 \
  --repeat 3 \
  --work-dir /tmp/goal2800_live \
  --output docs/reports/goal2800_pod_artifacts/rtnn_v25_live_ranked_summary_65536.json \
  --fail-fast
```

## Results

All three distributions passed the live harness. The RTDL and CuPy grid paths agree exactly for uniform input and agree within the explicit boundary tolerance for clustered and shell input.

| Distribution | RTDL/OptiX Last Run (s) | CuPy Grid Last Run (s) | CuPy/RTDL Ratio | RTDL Candidates | CuPy Candidates | Delta | Tolerance | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `uniform` | 0.001880 | 0.000140 | 0.0746x | 206446 | 206446 | 0 | 2 | pass |
| `clustered` | 0.096477 | 0.046966 | 0.4868x | 2914108 | 2914109 | 1 | 2 | pass |
| `shell` | 0.005670 | 0.002724 | 0.4804x | 1158440 | 1158438 | 2 | 2 | pass |

Clean-from-Git rerun:

| Distribution | RTDL/OptiX Last Run (s) | CuPy Grid Last Run (s) | CuPy/RTDL Ratio | Delta | Tolerance | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `uniform` | 0.002396 | 0.000143 | 0.0597x | 0 | 2 | pass |
| `clustered` | 0.096271 | 0.046990 | 0.4881x | 1 | 2 | pass |
| `shell` | 0.005706 | 0.002730 | 0.4785x | 2 | 2 | pass |

Interpretation:

- RTDL/OptiX produces exact ranked-summary rows without materializing full neighbor rows.
- The CuPy grid CUDA-core opponent is faster on these 65K fixtures.
- Clustered and shell counts differ by 1-2 boundary candidates because the CuPy grid baseline is float32 while the RTDL path follows the native prepared RTDL precision path.
- The harness records the delta instead of hiding it.

## Boundary

This is a live v2.5 RTNN harness and same-contract opponent check.

Not claimed:

- not a public speedup claim;
- not a whole-app speedup claim;
- not a claim that RTDL beats RTNN;
- not a claim that RTDL beats the CuPy grid opponent;
- not a broad RT-core speedup claim;
- not a Triton speedup claim;
- not a full RTNN paper reproduction;
- not a native app-specific engine path.

## Current Manifest Update

`rtnn` now records:

- `canonical_harness_status`: `ready_with_goal2800_live_ranked_summary_harness`
- `pod_evidence_status`: `Goal2800 current OptiX ranked-summary and CuPy grid same-contract live harness evidence recorded`
- `next_action`: keep the live harness current and keep dense exact top-k Triton auto-selection blocked until a tiled top-k route beats the same-contract CuPy grid opponent.

## Validation

Local validation completed before the pod run:

```text
py_compile: pass
validate_v2_5_tiered_benchmark_manifest: accept
```

External review:

```text
Claude: accept-with-boundary
Review: docs/reviews/goal2800_claude_review_rtnn_live_ranked_summary_harness_2026-05-31.md
Consensus: docs/reports/goal2800_rtnn_v2_5_live_ranked_summary_harness_consensus_2026-05-31.md
```

Focused local test slice after report/review/consensus:

```text
tests.goal2800_rtnn_v25_live_ranked_summary_harness_test
tests.goal2799_spatial_rayjoin_v25_prepared_count_harness_test
tests.goal2795_v2_5_tier_label_reconciliation_test
tests.goal2784_dense_point_topk_triton_adapter_kernel_test
tests.goal2780_topk_adapter_triton_grouped_topk_test

18 tests run, 16 passed, 2 skipped.
```

Clean-from-Git pod validation:

```text
commit: a22d388f1826c9e892f8b8a26196c8f0963c90e4
GPU: NVIDIA RTX A5000, driver 570.211.01
OptiX build: pass
Goal2800 harness: pass, 3 rows
Focused pod test slice: 18 tests run, 18 passed
```

## Goal2804 Metadata Refresh

Goal2804 refreshed the clean artifact to include source commit, source dirty
state, and GPU identity. The refreshed artifact remains `pass` and records:

```text
commit: 6ae202919c2af07ae8d8a9c662edd656ae77aa87
source_dirty: []
gpu: NVIDIA RTX A5000, 570.211.01
```
