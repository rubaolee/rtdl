# Goal 136 External Review

Date: 2026-04-06
Reviewer: Claude
Status: accepted

## Verdict

Accepted. The Goal 136 evaluation package is technically honest, repo-accurate, and
well-scoped. The paper characterization is defensible, the gap admission is explicit and
verified against the current codebase, and the proposed next-goal sequence follows the
same disciplined build-up pattern that closed the v0.2 segment/polygon families.

## Findings

**Paper characterization is plausible and specific.** The report describes the 2012 Kaibo
Wang paper as being about spatial cross-comparison of pathology-segmentation polygon sets
using Jaccard, not generic MinHash/token-set similarity. The title ("Accelerating
Pathology Image Data Cross-Comparison on CPU-GPU Hybrid Systems") and the stated workload
assumptions (axis-aligned edges, integer vertices, image-grid structure) are precise
enough that the distinction is not hand-waving. The characterization is internally
consistent.

**Gap admission is honest and verified.** The report states that current RTDL lacks:
(1) full overlay/materialization, and (2) any first-class overlap-area primitive. Both are
confirmed by the current repo. The workload cookbook (`docs/rtdl/workload_cookbook.md`)
explicitly notes overlay outputs a seed schema (`requires_lsi`, `requires_pip`), not
final polygon fragments. The v0.2 user guide "Current Limits" section explicitly disclaims
full overlay materialization. No hidden capability claims.

**Recommendation to accept the narrow line is justified.** The four acceptance reasons
(historical fit, spatial fit, product fit, validation fit) are coherent and proportionate.
The PostGIS backing story is concrete and uses the same `ST_Area(ST_Intersection(...))`
pattern already proven in the v0.2 validation flow. The public-data story names two real,
well-known pathology datasets (NuInsSeg, MoNuSAC family) with specific justifications.

**Next-goal sequence is appropriately layered.** Goals 137–142 follow the same build-up
discipline as the v0.2 segment/polygon family (charter → CPU/PostGIS primitive → data
acquisition → aggregate workload → Linux audit → documentation). CPU-first ordering is
explicit; GPU-backend claims are deferred until the primitive maps cleanly. No premature
GPU maturity claims.

**One minor process gap.** The goal doc lists "at least 2+ review/consensus coverage
before final acceptance" as a required outcome, but the report status is
`accepted-with-notes` without explicitly recording which reviews satisfied that threshold.
This external review may itself count as one, but the coverage count is not stated in the
report.

**Scope boundary against v0.2 is maintained.** Goal 126 confirms `segment_polygon_anyhit_rows`
was chosen as the v0.2 second family and closed. Goal 136 correctly positions Jaccard as
post-v0.2. The workload cookbook and user guide do not list any Jaccard entry — consistent
with it being unimplemented.

## Summary

The package is clean. The paper characterization is specific and plausible; the gap
admission is confirmed against the actual codebase; the narrow pathology-only boundary vs
generic-Jaccard rejection is disciplined; and the next-goal sequence is concrete without
overclaiming. The only gap is that the report does not explicitly record which
agents/reviews satisfied the "2+ coverage" requirement before acceptance. That is a
process bookkeeping note, not a technical honesty issue.
