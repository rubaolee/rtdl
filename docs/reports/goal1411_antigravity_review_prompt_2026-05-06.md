# Antigravity Review Prompt: RTDL v1.5 Release-Candidate Boundary

Please review RTDL v1.5 release-candidate status after the latest commits on
`main`.

## Context

- v1.5 is positioned as standalone RTDL for the supported Embree+OptiX
  language/runtime surface.
- v1.5 is not claiming that the native engine is fully app-agnostic internally.
- The stable primitive layer is app-name-free, but some native Embree/OptiX
  entry points remain workload-shaped compatibility/proof surfaces.
- `COLLECT_K_BOUNDED` row-returning apps are explicitly excluded from v1.5 and
  deferred to v1.5.1.
- v1.6-v2.0 should focus on the partner mechanism track and native-engine
  app-agnostic cleanup.

## Review Questions

1. Do the v1.5 docs, release statement, readiness gates, and tests consistently
   preserve the boundary that v1.5 is standalone for supported Embree+OptiX but
   not yet native-engine app-agnostic internally?
2. Is the RTX pod Embree-vs-OptiX performance interpretation honest, bounded,
   and not presented as whole-app or headline public speedup wording?
3. Does any wording still overclaim "general-purpose engine", "zero app
   knowledge", whole-app speedup, or public RTX speedup?
4. Can v1.5 be considered release-candidate complete internally while keeping
   final public/tag claims gated on explicit approval and required consensus?

## Files To Review

- `docs/release_reports/v1_5/README.md`
- `docs/release_reports/v1_5/release_statement.md`
- `docs/release_reports/v1_5/audit_report.md`
- `docs/release_reports/v1_5/support_matrix.md`
- `docs/reports/goal1410_v1_5_vs_v1_0_rtx_pod_perf_results_2026-05-06.md`
- `docs/reports/goal1411_v1_5_boundary_backend_consensus_status_2026-05-06.md`
- `src/rtdsl/v1_5_readiness.py`
- `src/rtdsl/v1_5_release_public_wording.py`
- `tests/goal1398_v1_5_standalone_release_gate_test.py`
- `tests/goal1407_v1_5_release_public_wording_gate_test.py`

## Desired Output

- `VERDICT: ACCEPT` or `VERDICT: REJECT`
- Required fixes, if any
- Any wording that should be tightened before v1.5 tag approval
