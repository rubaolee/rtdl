# Goal2802 RT-DBSCAN v2.5 Live Grouped-Stream Harness

Date: 2026-05-31

Status: implemented, reviewed, and clean-from-Git pod validated.

Verdict: accept-with-boundary.

## Purpose

Goal2802 replaces the `rt_dbscan` manifest row's old-artifact dependency with a current live harness.

The harness compares the current paths that matter for the RT-DBSCAN benchmark-app row:

- prepared CuPy grid components as the same-contract CUDA-core opponent;
- prepared RTDL/OptiX count-threshold plus CuPy grid continuation;
- RTDL/OptiX grouped-stream continuation that avoids neighbor-row materialization and avoids a full directed adjacency stream.

This is not a paper-reproduction claim and not a broad DBSCAN speedup claim. The accepted target is narrower: current RTDL can express the RT-DBSCAN-style continuation with generic fixed-radius/core-flag/grouped-stream contracts while keeping DBSCAN semantics outside the native engine.

## Files

| File | Purpose |
| --- | --- |
| `scripts/goal2802_rt_dbscan_v25_live_grouped_stream_harness.py` | Canonical v2.5 RT-DBSCAN live grouped-stream harness. |
| `tests/goal2802_rt_dbscan_v25_live_grouped_stream_harness_test.py` | Focused regression test for the harness, manifest row, pod artifact, and boundary wording. |
| `src/rtdsl/v2_5_triton_app_migration.py` | Marks `rt_dbscan` as ready with Goal2802 while keeping pure Triton component auto-selection blocked. |
| `docs/reports/goal2802_pod_artifacts/rt_dbscan_v25_live_grouped_stream_32768_65536_131072.json` | First pod evidence artifact. |
| `docs/reports/goal2802_pod_artifacts/rt_dbscan_v25_live_grouped_stream_32768_65536_131072.stdout` | Captured stdout from the first pod run. |
| `docs/reports/goal2802_pod_artifacts/rt_dbscan_v25_live_grouped_stream_32768_65536_131072_clean_from_git.json` | Clean-from-Git pod evidence artifact after the Goal2802 commit was pushed. |
| `docs/reports/goal2802_pod_artifacts/rt_dbscan_v25_live_grouped_stream_32768_65536_131072_clean_from_git.stdout` | Captured stdout from the clean-from-Git pod run. |
| `docs/reviews/goal2802_claude_review_rt_dbscan_live_grouped_stream_harness_2026-05-31.md` | Independent Claude review, verdict `accept-with-boundary`. |
| `docs/reviews/goal2802_gemini_review_rt_dbscan_live_grouped_stream_harness_2026-05-31.md` | Independent Gemini review, verdict `accept-with-boundary`. |
| `docs/reports/goal2802_rt_dbscan_v2_5_live_grouped_stream_harness_consensus_2026-05-31.md` | Codex+Claude+Gemini consensus for the current boundary. |

## Pod Evidence

Pod:

```text
ssh root@69.30.85.171 -p 22167 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
NVIDIA RTX A5000, driver 570.211.01
```

First evidence checkout:

```text
afcea27599c4738cdee62b111e22c3111598efe8
```

The Goal2802 script was copied into that checkout for the first artifact run.

Command:

```bash
timeout 1800s python3 scripts/goal2802_rt_dbscan_v25_live_grouped_stream_harness.py \
  --point-count 32768 \
  --point-count 65536 \
  --point-count 131072 \
  --repeat-count 3 \
  --output docs/reports/goal2802_pod_artifacts/rt_dbscan_v25_live_grouped_stream_32768_65536_131072.json
```

Results:

| Points | Prepared CuPy Grid Tail Median (s) | RT Count + Prepared Grid Tail Median (s) | RT Count Speedup | Grouped Stream Tail Median (s) | Grouped Native Tail Median (s) | Grouped Speedup | Planned Continuation | Status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 32,768 | 0.153620 | 0.142830 | 1.076x | 0.038223 | 0.024992 | 4.019x | full adjacency fits | pass |
| 65,536 | 0.445178 | 0.350078 | 1.272x | 0.091161 | 0.064954 | 4.883x | grouped stream | pass |
| 131,072 | 1.488015 | 0.977764 | 1.522x | 0.317657 | 0.250708 | 4.684x | grouped stream | pass |

Artifact checks:

- `status`: `pass`
- signatures match across prepared CuPy grid, RT count bridge, and grouped stream
- grouped stream uses RT cores
- grouped stream does not materialize neighbor rows
- grouped stream does not materialize a full directed adjacency stream
- minimum grouped-stream speedup vs prepared CuPy grid: 4.019x

The clean-from-Git rerun was executed after the Goal2802 commit was pushed, on a pod checkout reset to `origin/main` at:

```text
676844e4dc9d0883984827a2b6241781167020ef
```

Clean-from-Git results:

| Points | Prepared CuPy Grid Tail Median (s) | RT Count + Prepared Grid Tail Median (s) | RT Count Speedup | Grouped Stream Tail Median (s) | Grouped Native Tail Median (s) | Grouped Speedup | Status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 32,768 | 0.152686 | 0.137320 | 1.112x | 0.035597 | 0.021800 | 4.289x | pass |
| 65,536 | 0.439252 | 0.342244 | 1.283x | 0.090953 | 0.065749 | 4.829x | pass |
| 131,072 | 1.477062 | 0.962397 | 1.535x | 0.300814 | 0.251246 | 4.910x | pass |

Clean artifact checks:

- `status`: `pass`
- signatures match across prepared CuPy grid, RT count bridge, and grouped stream
- grouped stream uses RT cores
- grouped stream does not materialize neighbor rows
- grouped stream does not materialize a full directed adjacency stream
- minimum grouped-stream speedup vs prepared CuPy grid: 4.289x

## Boundary

Not claimed:

- not a public speedup claim;
- not a whole-app speedup claim;
- not a paper-reproduction claim;
- not a paper-level speedup claim;
- not a broad DBSCAN speedup claim;
- not a pure Triton components claim;
- not a native app-specific engine path.

## Manifest Update

`rt_dbscan` now records:

- `canonical_harness_status`: `ready_with_goal2802_live_grouped_stream_harness`
- `pod_evidence_status`: `Goal2802 current OptiX grouped-stream and CuPy prepared-grid same-contract evidence recorded`
- `next_action`: keep the live harness current and keep pure Triton components auto-selection blocked until a generic component continuation beats the same-contract CuPy/grid/grouped-stream opponent.

## Validation

External reviews and Codex+Claude+Gemini consensus are now recorded.

```text
Claude: accept-with-boundary
Review: docs/reviews/goal2802_claude_review_rt_dbscan_live_grouped_stream_harness_2026-05-31.md

Gemini: accept-with-boundary
Review: docs/reviews/goal2802_gemini_review_rt_dbscan_live_grouped_stream_harness_2026-05-31.md

Consensus: docs/reports/goal2802_rt_dbscan_v2_5_live_grouped_stream_harness_consensus_2026-05-31.md
```

Focused local test slice after report/review/consensus:

```text
tests.goal2802_rt_dbscan_v25_live_grouped_stream_harness_test
tests.goal2478_rt_dbscan_project_completion_test
tests.goal2795_v2_5_tier_label_reconciliation_test
tests.goal2801_hausdorff_xhd_v25_canonical_entrypoint_test

16 tests run, 16 passed.
```

Clean-from-Git pod validation:

```text
commit: 676844e4dc9d0883984827a2b6241781167020ef
GPU: NVIDIA RTX A5000, driver 570.211.01
OptiX build: pass
Goal2802 harness: pass, 3 rows
Focused pod test slice: 16 tests run, 16 passed
```
