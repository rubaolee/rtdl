# Independent Codex Review: V4 Goal4646 Pre-Tag Wording Fixes

Date: 2026-06-25

Reviewer: Codex independent review seat `Meitner`

Verdict:

`accept_goal4646_wording_fixes_tag_unblocked`

## Findings

Critical: none.

High: none.

Medium: none.

Informational:

- broader grep still finds the old wording in historical review/design records,
  but not in the current public tag surfaces inspected for this gate;
- preserved historical artifacts are not tag-blocking.

## Answers

1. Are Fix 1, Fix 2, and Fix 3 genuinely completed?
   Yes.

2. Does current public wording avoid the old unqualified high-performance label?
   Yes. Current public wording uses the bounded operator label.

3. Is the raw 5.185x geomean demoted from public headline to internal scorecard
   math?
   Yes. It is internal scorecard math / "do not headline" language.

4. Are point-nearest and AABB clearly labeled as scale-dependent
   algorithmic-complexity wins, not kernel-quality or near-OptiX wins?
   Yes.

5. Does every representative ratio have a baseline/denominator and scale?
   Yes.

6. Did the changes preserve V4.0 scope boundaries and forbidden claims?
   Yes.

7. Is the public tag unblocked by wording, or are amendments still required?
   The public tag is unblocked by wording.

## Verification

- targeted wording/release group: `39 tests OK`
- full V4 group: `185 tests OK`
- catalog dry-run: `status: passed`, bounded label printed
- quickstart: `status: ok`, bounded label printed

## Tag-Blocker Disposition

The public tag wording gate is closed. No required amendments before tag.

## Non-Authorization

This review only unblocks the Goal4646 wording/tag gate. It does not authorize
broad V4 speedup, whole-application speedup, all-benchmark speedup,
near-handwritten-OptiX performance, public true-zero-copy, Tier-3 callback
support, raw OptiX callback support, CuPy performance, C ABI, embedding,
non-Python host bindings, app-specific native kernels, Barnes-Hut coverage,
Spatial RayJoin coverage, or LibRTS paper reproduction.
