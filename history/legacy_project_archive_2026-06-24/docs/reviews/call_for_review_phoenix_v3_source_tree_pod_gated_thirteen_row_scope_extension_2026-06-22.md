# Review Request: Phoenix V3 Source-Tree / Pod-Gated Thirteen-Row Scope Extension

Reviewer: Claude preferred; Gemini if Claude is unavailable.
Date: 2026-06-22

## Question

Please review whether Phoenix V3 may extend the already-reviewed
source-tree/pod-gated installer/reproducibility closure from the prior
`source_tree_pod_gated_twelve_row` scope to the current
`source_tree_pod_gated_thirteen_row` surface.

This is not a release-readiness review and must not authorize release.

## Candidate Packet

`docs/rebuild/v3/v3_source_tree_pod_gated_thirteen_row_scope_extension_candidate_2026-06-22.md`

## Current Machine Facts

Current release-readiness gate:

`docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json`

Current facts:

- `status: blocked_not_release`
- `release_authorized: false`
- `m7_qualified_release_rows: 13`
- `release_scope: source_tree_pod_gated_twelve_row`
- `installer_closes_release_blocker: true`
- `installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row`
- `aggregate_13_row_installer_scope_review_required: true`
- `public_speedup_claim_authorized: false`
- `broad_v3_faster_than_v2_claim_authorized: false`

## Required Review Questions

1. Is the candidate scope `source_tree_pod_gated_thirteen_row` precise enough?
2. Does the prior source-tree/pod-gated reproducibility basis cover the new
   thirteenth Spatial supplemental row, or is a fresh pod rerun/install packet
   required?
3. If accepted, what exact machine fields may change?
4. Which fields must remain false?
5. Does this extension authorize release, package-install wording, broad
   hardware portability, public Spatial speedup, RTDL-beats-RayJoin, true
   zero-copy, broad V3-over-V2 speedup, or whole-app claims?
6. If rejected, identify the required fix before a 13-row source-tree/pod-gated
   closure can be recorded.

## Expected Output

- Verdict: one of `accept-with-amendments-not-release`,
  `accept-not-release`, `reject-fix-p0`, or `reject-fix-p1`.
- Findings ordered by severity.
- Required amendments before gate changes, if any.
- Exact allowed field changes.
- Exact fields and claims that remain forbidden.

## Non-Negotiable Boundary

Do not authorize release. The only possible accepted outcome is a scoped
installer/reproducibility extension. Release authorization remains a separate
aggregate 13-row review.
