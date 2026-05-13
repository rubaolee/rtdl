# Goal1907 Gemini Review Request - v2 Boundary And Source-Tree Policy

Please perform an independent read-only review of the v2.0 non-hardware boundary work.

## Context

- v2.0 is not released.
- RTX pod evidence is still required for the current performance gate.
- This review is about non-hardware public wording and package/source-tree policy only.
- Do not authorize v2.0 release.

## Files To Review

- `docs/partner_acceleration_boundaries.md`
- `docs/reports/goal1900_partner_acceleration_boundary_doc_2026-05-13.md`
- `docs/reports/goal1902_v2_source_tree_only_release_exception_proposal_2026-05-13.md`
- `scripts/goal1906_public_v2_claim_boundary_scan.py`
- `docs/reports/goal1906_public_v2_claim_boundary_scan_2026-05-13.md`
- `tests/goal1906_public_v2_claim_boundary_scan_test.py`
- `docs/reports/goal1899_v2_strict_birth_gate_current_board_2026-05-13.md`

## Review Questions

1. Does the partner boundary doc clearly say RTDL accelerates explicit RTDL primitive calls over partner-owned data, not arbitrary PyTorch/CuPy programs?
2. Does the source-tree-only proposal honestly block package-install claims unless final 3-AI consensus accepts the exception?
3. Does Goal1906 provide a useful local guardrail against premature public wording?
4. Are any public claims too broad around package-install support, arbitrary PyTorch/CuPy acceleration, whole-application acceleration, broad RT-core speedup, true zero-copy, or v2.0 release readiness?
5. Does Goal1899 keep v2.0 blocked until pod evidence and final release consensus exist?

## Required Output

Write the review to:

`docs/reviews/goal1907_gemini_review_v2_boundary_and_source_tree_2026-05-13.md`

Use one of these verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Do not edit any file except the requested review file.
