# Goal2801 Hausdorff/X-HD v2.5 Canonical Entrypoint

Date: 2026-05-31

Status: implemented, reviewed, and clean-from-Git pod validated.

Verdict: accept-with-boundary.

## Purpose

Goal2801 consolidates the Hausdorff/X-HD benchmark row behind one canonical exact entrypoint.

The entrypoint compares:

- exact `cupy_grouped_grid_rawkernel` as the same-contract CUDA-core opponent;
- exact `rtdl_rt_grouped_adaptive_nearest_witness` as the RTDL/OptiX witness path.

This is not a speedup claim. The first artifact shows the RTDL/OptiX path is correct and uses RT cores, but it is much slower than the CuPy grid baseline on the 4K fixture.

## Files

| File | Purpose |
| --- | --- |
| `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py` | Canonical v2.5 exact Hausdorff/X-HD entrypoint. |
| `tests/goal2801_hausdorff_xhd_v25_canonical_entrypoint_test.py` | Focused regression test for the entrypoint, manifest row, pod artifact, and boundary wording. |
| `src/rtdsl/v2_5_triton_app_migration.py` | Marks `hausdorff_xhd` as ready with Goal2801 while keeping Triton witness auto-selection blocked. |
| `docs/reports/goal2801_pod_artifacts/hausdorff_xhd_v25_canonical_entrypoint_4096.json` | First pod evidence artifact. |
| `docs/reports/goal2801_pod_artifacts/hausdorff_xhd_v25_canonical_entrypoint_4096.stdout` | Captured stdout from the first pod run. |
| `docs/reports/goal2801_pod_artifacts/hausdorff_xhd_v25_canonical_entrypoint_4096_clean_from_git.json` | Clean-from-Git pod evidence artifact after the Goal2801 commit was pushed. |
| `docs/reports/goal2801_pod_artifacts/hausdorff_xhd_v25_canonical_entrypoint_4096_clean_from_git.stdout` | Captured stdout from the clean-from-Git pod run. |
| `docs/reviews/goal2801_claude_review_hausdorff_xhd_canonical_entrypoint_2026-05-31.md` | Independent Claude review, verdict `accept-with-boundary`. |
| `docs/reports/goal2801_hausdorff_xhd_v2_5_canonical_entrypoint_consensus_2026-05-31.md` | Codex+Claude consensus for the current boundary. |

## Pod Evidence

Pod:

```text
ssh root@69.30.85.171 -p 22167 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
NVIDIA RTX A5000, driver 570.211.01
```

Command:

```bash
timeout 900s python3 scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py \
  --points-a 4096 \
  --points-b 4096 \
  --output docs/reports/goal2801_pod_artifacts/hausdorff_xhd_v25_canonical_entrypoint_4096.json
```

Results:

| Metric | Value |
| --- | ---: |
| Status | pass |
| Distance error vs CuPy grid | 0.0 |
| CuPy grid elapsed | 0.004478 s |
| RTDL/OptiX adaptive witness elapsed | 0.649487 s |
| RTDL/CuPy elapsed ratio | 145.03x slower |
| RTDL method uses RT cores | true |

The clean-from-Git rerun was executed after the Goal2801 commit was pushed, on a pod checkout reset to `origin/main` at:

```text
7a764ad8b742fb621c0fcc0154335f5b19c251f1
```

Clean-from-Git results:

| Metric | Value |
| --- | ---: |
| Status | pass |
| Distance error vs CuPy grid | 0.0 |
| CuPy grid elapsed | 0.004488 s |
| RTDL/OptiX adaptive witness elapsed | 0.646395 s |
| RTDL/CuPy elapsed ratio | 144.04x slower |
| RTDL method uses RT cores | true |

## Boundary

Not claimed:

- not a public speedup claim;
- not a whole-app speedup claim;
- not a claim that RTDL beats X-HD;
- not a claim that RTDL beats the CuPy grid opponent;
- not a broad RT-core speedup claim;
- not a Triton speedup claim;
- not a full X-HD paper reproduction;
- not a native app-specific engine path.

## Manifest Update

`hausdorff_xhd` now records:

- `canonical_harness_status`: `ready_with_goal2801_canonical_exact_entrypoint`
- `pod_evidence_status`: `Goal2801 current OptiX exact witness and CuPy grid same-contract canonical entrypoint evidence recorded`
- `next_action`: keep the canonical entrypoint current and keep Triton witness auto-selection blocked until it beats the same-contract CuPy grid opponent.

## Validation

Local validation before pod run:

```text
py_compile: pass
validate_v2_5_tiered_benchmark_manifest: accept
```

External review and Codex+Claude consensus are now recorded.

```text
Claude: accept-with-boundary
Review: docs/reviews/goal2801_claude_review_hausdorff_xhd_canonical_entrypoint_2026-05-31.md
Consensus: docs/reports/goal2801_hausdorff_xhd_v2_5_canonical_entrypoint_consensus_2026-05-31.md
```

Focused local test slice after report/review/consensus:

```text
tests.goal2801_hausdorff_xhd_v25_canonical_entrypoint_test
tests.goal2800_rtnn_v25_live_ranked_summary_harness_test
tests.goal2795_v2_5_tier_label_reconciliation_test
tests.goal2790_hausdorff_tiled_dense_point_nearest_test
tests.goal2788_hausdorff_dense_point_nearest_triton_strategy_test

20 tests run, 17 passed, 3 skipped.
```

Clean-from-Git pod validation:

```text
commit: 7a764ad8b742fb621c0fcc0154335f5b19c251f1
GPU: NVIDIA RTX A5000, driver 570.211.01
OptiX build: pass
Goal2801 harness: pass
Focused pod test slice: 20 tests run, 20 passed
```

## Goal2804 Metadata Refresh

Goal2804 refreshed the clean artifact to include source commit, source dirty
state, and GPU identity. The refreshed artifact remains `pass` and records:

```text
commit: 6ae202919c2af07ae8d8a9c662edd656ae77aa87
source_dirty: []
gpu: NVIDIA RTX A5000, 570.211.01
```
