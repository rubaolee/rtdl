# Goal1900 - Partner Acceleration Boundary Doc

Status: source-doc-ready-needs-external-review

Date: 2026-05-13

## Scope

Goal1900 adds the user-facing boundary document required by the Goal1814
arbitrary PyTorch/CuPy acceleration blocker:

`docs/partner_acceleration_boundaries.md`

The document explains what RTDL accelerates, what it does not accelerate, and
how partner-owned columns differ from arbitrary partner-program acceleration.

## Key Rule

RTDL accelerates explicit RTDL primitive calls over partner-owned data. RTDL does not accelerate arbitrary PyTorch or CuPy programs.

## Release Boundary

This goal does not close v2.0 by itself. The document is now linked from the
front-page README, docs index, and tutorial ladder, but still needs external
review before the v2.0 release packet.

The blocked claims remain blocked:

- arbitrary PyTorch/CuPy acceleration;
- whole-application acceleration by default;
- broad RT-core speedup;
- package-install support;
- v2.0 release readiness.
