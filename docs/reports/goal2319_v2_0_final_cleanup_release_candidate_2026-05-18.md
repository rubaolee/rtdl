# Goal2319 v2.0 Final Cleanup Release Candidate

Date: 2026-05-18

Status: `current-head-release-candidate`

## Purpose

Goal2319 is the final cleanup packet before the v2.0 release decision. It
does not publish, tag, or announce v2.0. It makes the current release artifacts
consistent after the post-streaming witness work and the RayJoin closure.

## Cleanup Completed

| Area | Operation | Result |
| --- | --- | --- |
| Native app-agnostic scan | Renamed the remaining OptiX diagnostic/profile environment strings and log label from PIP wording to `POINT_PRIMITIVE_ANYHIT` wording. | Strict native scan is back to 9 known uppercase `RTDL_DB_*` constant false positives and 0 real app-shaped `rtdl_...` symbols. |
| Final v2.0 matrix | Refreshed Goal2068 from the post-streaming Goal2085 table. | `mixed_apps` is now `[]`; all 16 current OptiX/RT rows have measured v2/v1.8 ratios below 1.0 under documented contracts. |
| Pre-release gate | Refreshed Goal2069 after the matrix update and made its subprocess test runner source-tree aware. | Focused gate reports `40 tests, 1 skipped`, all passing. |
| Docs reorganization compatibility | Added non-learner breadcrumbs for the v1.8/v2.0 partner gate and restored the Goal1668 directive compatibility path. | Old audit gates remain traceable without cluttering the learner path. |
| Evidence tracking | Promoted the post-streaming witness summary/table artifacts into the release packet. | Goal2085/Goal2088 are now the current performance-table basis, superseding the old full-row witness result. |

## Current Engineering Position

The v2.0 engineering release candidate is clean under the current scoped gates:

- native strict `rtdl_...` app-shaped scan: `0` real hits;
- public claim scan: passing;
- focused pre-release gate: passing;
- all current OptiX/RT matrix rows: measured v2/v1.8 ratio below `1.0`;
- Embree table: filled CPU same-contract evidence, not the headline GPU
  partner-speedup claim;
- RayJoin-style LSI/PIP lane: closed for v2.0 with bounded same-query evidence
  and no claim that RTDL beats the RayJoin paper implementation.

## Allowed Release Wording

- RTDL v2.0 is a Python+partner+RTDL source-tree release candidate.
- RTDL v2.0 keeps the native release surface app-agnostic.
- Current OptiX/RT evidence has 16/16 measured v2 rows faster than v1.8 under
  the documented contracts.
- v2.0 demonstrates partner-owned count, flag, threshold, bounded candidate,
  and streaming witness-column output patterns.

## Still Not Allowed

- package-install or PyPI support;
- arbitrary PyTorch/CuPy acceleration;
- broad RT-core acceleration;
- whole-application speedup claims;
- arbitrary polygon overlay;
- RayJoin-paper reproduction or RTDL-beats-RayJoin claims;
- Triton, Numba, Embree CPU partner, or v3.0 custom-extension claims as part
  of v2.0.

## Required Before Release Button

The strict v2.0 public-closure rule still applies:

1. Obtain a fresh Claude review over this current-head packet.
2. Obtain a fresh Gemini review over this current-head packet.
3. Write the final current-head 3-AI consensus file.
4. Rerun the focused release-prep gate after the reviews and consensus exist.
5. Only then perform the explicit version/tag/publish action requested by the
   user.

## v2.1 And Later

Further tuning is real but no longer a v2.0 blocker:

- deeper RayJoin paper reproduction and phase-boundary comparison;
- exact Hausdorff and X-HD-inspired tuning beyond the current language test;
- general device-resident row-stream/continuation primitives;
- reusable graph partner primitives;
- broader polygon overlay and candidate-summary generalization;
- Triton/Numba partner exploration;
- v3.0 custom engine extensions.

## Verdict

`accept-with-boundary` from Codex pending external review.

The repository is ready for final external v2.0 release review. It is not yet
released and not yet 3-AI-consensus complete.
