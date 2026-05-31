# Goal2801 Hausdorff/X-HD v2.5 Canonical Entrypoint

Date: 2026-05-31

Status: implemented locally with first OptiX/CuPy pod evidence and Claude review.

Verdict: accept-with-boundary pending clean-from-Git rerun.

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

Focused tests and clean-from-Git pod validation are still pending at the time of this revision.
