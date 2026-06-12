# Goal4314: Current Claim-Boundary Canonicalization

Date: 2026-06-11

## Verdict

`accept-with-boundary` for a learner-doc drift reduction slice.

Goal4314 adds a canonical learner-facing claim-boundary page and links the main
public front doors to it. This addresses the Fable5 P10 concern that boundary
prose was correct but repeated across too many places, making drift likely and
making new users work too hard to understand what RTDL does and does not claim.

## What Changed

- Added `docs/learn/current_claim_boundaries.md`.
- Linked that page from:
  - `README.md`;
  - `docs/README.md`;
  - `docs/learn/README.md`;
  - `docs/capability_boundaries.md`;
  - `docs/partner_acceleration_boundaries.md`;
  - `tutorials/current/README.md`;
  - `examples/README.md`.
- Refreshed `docs/reports/goal4248_current_public_docs_claim_boundary_scan.json`.
- Updated the public-doc claim scan test to expect 34 public markdown files.

The canonical page keeps the current public learner milestone as the v2.10
source-tree surface and explicitly states that active v2.11 work is internal
engineering evidence until a reviewed release packet says otherwise.

## Boundary

Goal4314 does not authorize release action, package-install wording, public
speedup wording, whole-application acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, AMD/HIPRT or Intel-GPU
performance wording, automatic partner selection, or app-specific native-engine
logic.

This is documentation structure work only. It makes the existing boundary easier
to find; it does not expand the boundary.

## Validation

Public-doc claim scan:

```text
$env:PYTHONPATH='src;.'; py -3 scripts\goal4248_current_public_docs_claim_boundary_scan.py

status: pass
hard_blocker_count: 0
public_file_count: 34
```

Focused tests:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4314_current_claim_boundary_canonicalization_test tests.goal4248_current_public_docs_claim_boundary_scan_test
```

Expected result: 9 tests pass.
