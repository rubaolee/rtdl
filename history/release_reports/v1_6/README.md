# RTDL v1.6 Release Package

Status: released. The `v1.6` annotated tag was published after final 3-AI
release consensus and explicit release/tag authorization.

RTDL v1.6 is the planned first Python+RTDL architecture closure milestone. It
closes the first architecture track by making the supported public story
explicit: Python remains the app/control layer, RTDL owns the RT-shaped
primitive contract and bridge, and Embree/OptiX execute the validated native
primitive subpaths.

v1.6 is not a performance freeze. NVIDIA RT-core performance, OptiX work,
`COLLECT_K_BOUNDED` promotion, and true device-memory/zero-copy investigation
remain top post-v1.6 priorities.

## Scope

This package records the v1.6 boundary:

- Python-hosted RTDL source-tree usage.
- Active closure backends: Embree and OptiX.
- Stable primitive boundary:
  `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, and
  `REDUCE_INT(COUNT|SUM)`.
- App-generic public primitive-contract wording for the stable surface.
- Explicit exclusion of arbitrary user-Python optimization and whole-app
  speedup claims.
- Explicit distinction between reduced-copy engineering and true zero-copy
  claims.
- Explicit distinction between Python+RTDL (`v1.6`) and Python+partner+RTDL
  (`v1.7-v2.0`).
- Explicit acknowledgement that native internals still include app-shaped
  compatibility/proof paths and are not fully app-agnostic internally.

## Allowed Conclusion

RTDL v1.6 is the first Python+RTDL architecture milestone: Python remains the
app/control layer, RTDL provides the supported RT-shaped primitive contract and
bridge, and Embree/OptiX execute the validated stable primitive subpaths.
Performance claims remain scoped to reviewed exact primitive subpaths.

## Disallowed Conclusions

- Must not claim that `COLLECT_K_BOUNDED` is stable.
- Must not claim that RTDL optimizes arbitrary user Python code.
- Must not claim that RTDL provides whole-application speedup by default.
- Must not claim that every `--backend optix` run is a NVIDIA RT-core speedup.
- Must not claim that true zero-copy is supported.
- Must not claim that partner tensor handoff is part of v1.6.
- Must not claim that package-install usage is supported.
- Must not claim that native internals are fully app-agnostic.
- Must not claim that Vulkan, HIPRT, or Apple RT are active v1.6
  implementation targets.

## Start Here

- [Release Statement](release_statement.md)
- [Support Matrix](support_matrix.md)
- [Audit Report](audit_report.md)
- [Tag Preparation](tag_preparation.md)
- [Goal 1599 v1.6 Readiness Boundary](../../reports/goal1599_v1_6_python_rtdl_historical_milestone_readiness_2026-05-09.md)
- [Goal 1600 Readiness Gate](../../reports/goal1600_v1_6_python_rtdl_readiness_gate_2026-05-09.md)
- [Goal 1601 Release-Surface Proposal](../../reports/goal1601_v1_6_release_surface_proposal_2026-05-09.md)
- [Goal 1602 Public Docs Overclaim Audit](../../reports/goal1602_v1_6_public_docs_overclaim_audit_2026-05-09.md)
- [Goal 1603 Native Path App-Leakage Audit](../../reports/goal1603_v1_6_stable_native_path_app_leakage_audit_2026-05-09.md)
- [Goal 1604 Blocked-Claim Regression Gate](../../reports/goal1604_v1_6_blocked_claim_regression_gate_2026-05-09.md)
- [Goal 1605 Windows/Linux/OptiX Validation](../../reports/goal1605_v1_6_windows_linux_optix_validation_2026-05-09.md)

## Release Gate State

The local v1.6 architecture-boundary gates are complete through Goal 1605:
release-surface proposal, public-docs overclaim audit, native stable-path
app-leakage audit, blocked-claim regression, Windows source-tree validation,
Linux source-tree validation, and real NVIDIA OptiX validation for the scoped
surface.

The final release package review, final 3-AI release consensus, public
front-door docs update, and explicit release/tag authorization are complete.
