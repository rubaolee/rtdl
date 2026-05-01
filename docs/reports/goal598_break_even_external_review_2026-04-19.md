# External Review: Goal598 Apple RT Segment-Intersection Break-Even Analysis

**Date:** 2026-04-19
**Reviewer:** External System (Gemini CLI)
**Target:** `docs/reports/goal598_v0_9_2_apple_rt_segment_intersection_break_even_2026-04-19.md`

## Verdict: ACCEPT

**Rationale:**
The proposed masked chunked nearest-hit strategy is a sound and reasonably bounded experiment for optimizing the Apple RT `segment_intersection` path. The analysis accurately points out that `MPSIntersectionTypeAny` over a multi-primitive AS lacks the primitive indices required for exact output.

Shifting to a chunked nearest-hit design with primitive masking (up to 32 primitives per chunk) effectively addresses the high overhead of building individual quadrilateral acceleration structures, potentially reducing AS builds by up to 32x. Even though worst-case dispatch counts remain bounded at `R` for dense all-pair scenarios, the reduction in AS build overhead makes this a worthwhile architectural experiment.

**Conditions for Implementation:**
The implementation must adhere strictly to the conditions in the break-even analysis:
1. The work remains a bounded v0.9.2 experiment.
2. All specified parity tests must pass—especially those validating left-major output ordering, multi-hit scenarios in a single chunk, and exact analytic refinement.
3. If the experiment fails to improve the measured median performance or introduces parity failures, the changes must be reverted and a technical stop recorded, leaving the current path intact.
