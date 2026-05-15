# Goal2088 v2.0 Release Prep After Streaming Witness

Date: 2026-05-15

Status: `release-prep-candidate`

## Purpose

Goal2073 accepted the v2.0 release-hardening packet with boundary, but it still classified `segment_polygon_anyhit_rows` as mixed because the old full Python witness-row contract was slower than v1.8 native rows.

Goals 2081, 2083, 2085, 2086, and 2087 supersede that stale part of the packet. The replacement contract is streaming exact witness columns: the native engine emits generic ray/primitive candidate witness pairs, the app/partner layer exact-filters them, and exact witness IDs remain in partner-owned device columns instead of becoming Python row dictionaries.

This file prepares the post-Goal2086 v2.0 release packet for final external review. It is not a tag, publish, or announcement action.

## Updated Evidence Packet

- all-app table after streaming witness update: `docs/reports/goal2085_v2_perf_table_after_streaming_witness_update_2026-05-15.md`
- table JSON: `docs/reports/goal2085_v2_perf_table_after_streaming_witness_update_2026-05-15.json`
- streaming witness design report: `docs/reports/goal2081_streaming_witness_page_adapter_2026-05-15.md`
- first pod evidence: `docs/reports/goal2083_streaming_witness_page_pod_evidence_2026-05-15.md`
- extended pod evidence: `docs/reports/goal2086_streaming_witness_page_extended_scale_pod_2026-05-15.md`
- Gemini review of Goal2081: `docs/reviews/goal2082_gemini_review_goal2081_streaming_witness_page_adapter_2026-05-15.md`
- Gemini review of Goal2083: `docs/reviews/goal2084_gemini_review_goal2083_streaming_witness_page_pod_evidence_2026-05-15.md`
- Gemini review of Goal2086: `docs/reviews/goal2087_gemini_review_goal2086_extended_streaming_witness_pod_2026-05-15.md`

## Current Matrix Position

The Goal2085 table has all cells filled.

OptiX/RT:

- rows: `16`
- rows with measured v2/v1.8 ratio below `1.0`: `16`
- remaining mixed rows in the current OptiX/RT table: `[]`
- slowest current OptiX/RT ratio: `robot_collision_screening`, `0.367x`

Embree:

- rows: `16`
- rows with measured v2/v1.8 ratio below `1.0`: `9`
- Embree is a CPU same-contract comparison surface, not the headline GPU partner-speedup surface.
- Embree rows near or above parity remain bounded CPU evidence, not blockers to the OptiX/RT partner claim.

## What Changed Since Goal2073

- `segment_polygon_anyhit_rows` should no longer be described as the old mixed full-row materialization row in the v2.0 release-prep packet.
- The correct current OptiX/RT row is the Goal2083/Goal2085 streaming exact witness-column row:
  - scale: `count=16384 partner=cupy streaming_exact_witness_page current RTX 3090`
  - v1.8: `1.905528s`
  - v2.0: `0.001421s`
  - v2/v1.8: `0.001x`
- Goal2086 extends the same contract to `32768` and `65536` exact witnesses with no overflow.

## Claim Boundary

Allowed for final review:

- v2.0 is a Python+partner+RTDL source-tree release-prep candidate.
- v2.0 has a current, filled Embree and OptiX/RT v1.8-vs-v2.0 evidence table.
- Current OptiX/RT evidence has measured v2 ratios below `1.0` for all 16 rows under the documented contracts.
- `segment_polygon_anyhit_rows` is solved for the streaming exact witness-column contract, not for full Python row-table materialization.
- v2.0 demonstrates reusable partner-owned device-column output patterns for counts, flags, threshold summaries, polygon candidate summaries, and exact witness pages.

Still not allowed:

- v2.0 is released, until an explicit release/tag/publish action is requested and completed.
- all possible user programs are faster.
- broad RT-core acceleration without scoped evidence.
- arbitrary PyTorch/CuPy acceleration.
- package-install support.
- old full Python witness-row materialization is fast.
- arbitrary polygon overlay is solved.
- Triton, Numba, Embree CPU partner, or v3.0 custom-extension claims as part of v2.0.

## Remaining Prep Work

Before a final v2.0 release action:

1. Get a fresh Claude review over this post-Goal2086 packet.
2. Get a fresh Gemini final-release review over this post-Goal2086 packet, or explicitly reuse Goal2087 only for the Goal2086 delta and ask Gemini to review the full packet.
3. Write a new final consensus file that supersedes Goal2073 for the post-Goal2086 packet.
4. Run the focused v2.0 release-prep test slice after all review/consensus artifacts exist.
5. Only then perform the explicit user-requested release action.

## Verdict

`release-prep-candidate`

The v2.0 packet is stronger than Goal2073 because the old mixed witness-row problem now has a measured streaming-column solution. It is ready for final external release review, but it is not yet a release authorization.

