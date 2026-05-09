# RTDL v1.6 Release Statement

Status: proposed final release statement. Do not publish until final 3-AI
release consensus is accepted and explicit release/tag authorization is
confirmed.

Proposed release statement:

> RTDL v1.6 is the first Python+RTDL architecture milestone. Python remains the
> app/control layer, while RTDL owns the supported RT-shaped primitive contract
> and bridge to native Embree/OptiX execution. The stable public surface is
> limited to reviewed primitive subpaths: `ANY_HIT`, `COUNT_HITS`,
> `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`. RTDL does not
> optimize arbitrary Python code or whole applications; performance claims
> remain scoped to exact reviewed primitive subpaths.

## What This Release May Claim

- `v1.6` closes the first Python+RTDL architecture track.
- Python remains the app/control layer.
- RTDL owns the supported RT-shaped primitive contract and native bridge.
- Embree and OptiX are the active v1.6 closure backends.
- The stable primitive boundary is `ANY_HIT`, `COUNT_HITS`,
  `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`.
- Source-tree usage remains the supported usage style, for example
  `PYTHONPATH=src:. python -m unittest ...`.
- Windows and Linux source-tree validation passed for the scoped release slice.
- Real NVIDIA OptiX runtime validation passed on the Linux validation host for
  the scoped primitive/reduction paths.
- v1.7-v2.0 are the staged Python+partner+RTDL mechanism track.

## What This Release Must Not Claim

- package-install support;
- arbitrary user-Python optimization;
- whole-application speedup;
- broad NVIDIA RTX/GPU acceleration;
- that every `--backend optix` run is a NVIDIA RT-core speedup;
- true zero-copy support;
- partner tensor handoff support;
- stable `COLLECT_K_BOUNDED` promotion;
- app-free native internals;
- active Vulkan, HIPRT, or Apple RT implementation targets.

## Performance Boundary

v1.6 is an architecture anchor, not a performance freeze.

The post-v1.6 performance track remains active and high priority:

- improve NVIDIA OptiX/RT-core primitive execution;
- continue `COLLECT_K_BOUNDED` optimization and promotion analysis;
- reduce Python/native and host/device bulk data movement;
- prove or reject true device-memory zero-copy paths with measured hardware
  evidence;
- keep Embree as the CPU same-contract fallback and comparison baseline.

No public speedup wording is added by this release statement.

## Evidence Pointers

- `docs/reports/goal1599_v1_6_python_rtdl_historical_milestone_readiness_2026-05-09.md`
- `docs/reviews/goal1599_v1_6_readiness_3ai_consensus_2026-05-09.md`
- `docs/reports/goal1600_v1_6_python_rtdl_readiness_gate_2026-05-09.md`
- `docs/reviews/goal1600_v1_6_readiness_gate_3ai_consensus_2026-05-09.md`
- `docs/reports/goal1601_v1_6_release_surface_proposal_2026-05-09.md`
- `docs/reviews/goal1601_v1_6_release_surface_proposal_3ai_consensus_2026-05-09.md`
- `docs/reports/goal1602_v1_6_public_docs_overclaim_audit_2026-05-09.md`
- `docs/reviews/goal1602_v1_6_public_docs_overclaim_audit_3ai_consensus_2026-05-09.md`
- `docs/reports/goal1603_v1_6_stable_native_path_app_leakage_audit_2026-05-09.md`
- `docs/reviews/goal1603_v1_6_stable_native_path_app_leakage_audit_3ai_consensus_2026-05-09.md`
- `docs/reports/goal1604_v1_6_blocked_claim_regression_gate_2026-05-09.md`
- `docs/reviews/goal1604_v1_6_blocked_claim_regression_gate_3ai_consensus_2026-05-09.md`
- `docs/reports/goal1605_v1_6_windows_linux_optix_validation_2026-05-09.md`
- `docs/reviews/goal1605_v1_6_windows_linux_optix_validation_3ai_consensus_2026-05-09.md`
