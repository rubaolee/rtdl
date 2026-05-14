# Goal2024 v2.0 Readiness Audit After Goal2022

Date: 2026-05-14

Status: release-positioning audit, not release authorization

## Purpose

This audit positions the current Python + partner + RTDL work after the latest
v2.0 performance fixes:

- Goal2020 kept the polygon AABB extent payload on the CuPy device path.
- Goal2022 added the compressed repeated metric-table pattern for the graph
  control row.

Those two goals matter because they close the last obvious weak-spot group in
the current 16-row all-app matrix. Before Goal2020 and Goal2022, the v2.0 story
still had visible "yes, but" performance holes in polygon overlap/Jaccard and
graph analytics. After them, every row in the current matrix has positive or
bounded-positive evidence against the v1.8 Python + RTDL baseline.

## Current Position

The project is now in a v2.0 release-candidate preparation lane, not in an
open-ended performance rescue lane.

That does not mean v2.0 is released. It means the remaining work has shifted
from "find a credible v2 design" to "freeze the claims, refresh the release
packet, and obtain final consensus."

Current release posture:

| Area | Position |
| --- | --- |
| Native engine boundary | Accepted: the v2 work keeps app/domain semantics outside the native engine. |
| Partner direction | Accepted: Python orchestrates RTDL primitive outputs into CuPy/Torch continuation code. |
| Current matrix usefulness | Accepted with boundaries: all 16 rows have positive or bounded-positive evidence. |
| Broad whole-app speedup claim | Blocked: only row-scoped claims are authorized. |
| Broad RT-core acceleration claim | Blocked: many rows measure partner continuation speed, not RT-core-only acceleration. |
| Package-install claim | Blocked: current public usage remains source-tree execution. |
| Final v2.0 release | Blocked pending final release packet, final 3-AI consensus, and explicit user release action. |

## Evidence Snapshot

The current machine-readable matrix is:

`docs/reports/goal2015_current_all_app_v18_v2_perf_analysis_after_goal2009_2026-05-14.json`

It contains 16 rows:

- 7 `positive`
- 3 `positive-bounded`
- 5 `positive-bounded-exact`
- 1 `positive-subsecond`

The most important recent evidence updates are:

| Goal | Effect | External review |
| --- | --- | --- |
| Goal2020 | Polygon pair overlap and Jaccard keep the CuPy extent payload device-resident, improving the 8192-copy ratios to `0.214x` and `0.201x`. | Goal2021: `accept` |
| Goal2022 | Graph analytics uses a generic compressed repeated metric-table pattern, improving the 1000-copy ratio to `0.000007x` with a 100000-copy v2-only scale probe. | Goal2023: `accept-with-boundary` |

The Goal2023 boundary is important and correct: the graph result is a generic
compressed metric-table continuation for the authored graph control row. It is
not evidence for arbitrary graph traversal acceleration, BFS acceleration, or
RT-core graph acceleration.

## What v2.0 Can Say Now

Allowed current wording:

- RTDL v2.0 candidate code demonstrates Python + RTDL + partner tensor
  continuation across the current app matrix.
- The native RTDL engine remains app-agnostic; app semantics live in Python and
  partner code.
- The current 16-row evidence matrix has no remaining negative row in its
  measured or bounded contract.
- CuPy and Torch are useful continuation partners for reducing, filtering,
  ranking, grouping, and summarizing generic RTDL outputs.
- Some rows show large speedups because v2 avoids Python object materialization
  and keeps the continuation in partner-owned arrays.

Forbidden current wording:

- Do not say v2.0 is released.
- Do not say every app has a final whole-app speedup claim.
- Do not say RT cores broadly accelerate every workload in the matrix.
- Do not say arbitrary PyTorch/CuPy user code is automatically accelerated.
- Do not claim true package installation support.
- Do not turn bounded rows into broad domain claims.

## Remaining Boundaries

The strongest remaining engineering boundaries are claim boundaries, not design
unknowns:

- `segment_polygon_anyhit_rows` is positive but still marked
  `implemented-rerun-needed` in the current matrix.
- Several rows are intentionally bounded:
  - graph analytics: compressed metric-table control row, not arbitrary graph
    traversal;
  - polygon overlap/Jaccard: authored axis-aligned extent control contract, not
    arbitrary polygon overlay;
  - DBSCAN: exact but host-bucket-index bounded;
  - Hausdorff, ANN, facility KNN, and Barnes-Hut: exact partner-reference rows,
    not full industrial solver claims.
- Some pod artifacts use local source labels rather than a clean Git checkout
  label, so the final release packet should prefer a fresh source-tree run from
  a recorded commit.
- The matrix file name still says "after Goal2009" even though its content has
  been updated through Goal2020 and Goal2022. This is acceptable as historical
  continuity but should be replaced by a final release matrix before tagging.
- Goal1911 and Goal1950 already keep final release blocked until final v2.0
  release consensus and explicit release action exist.

## Recommended Path To v2.0

1. Track the Goal2023 external review alongside the Goal2022 implementation.
2. Produce a final v2.0 release packet that supersedes the older Goal2011 and
   Goal2015 naming:
   - final all-app matrix after Goal2022;
   - final claim-boundary table;
   - final front-page/tutorial/examples wording for Python + RTDL + partner
     tensors;
   - final source-tree usage instructions.
3. Run a final pre-release gate:
   - current v2 performance-row tests;
   - app-agnostic native purity tests;
   - partner architecture tests;
   - release wording and package-claim scan.
4. Request final 3-AI release consensus after the final release packet exists.
   For this release decision, Codex plus only one external review is not enough.
5. Publish v2.0 only after the user gives the explicit release action.

## Audit Verdict

`accept-with-boundary`

The v2.0 work is now credible enough to enter final release preparation. The
project should stop adding new performance lanes unless a final gate exposes a
specific regression. The next correct work is release hardening: final matrix,
final docs, final tests, and final 3-AI consensus.

v2.0 is close, but not released.
