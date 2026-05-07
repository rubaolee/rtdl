# Goal1473 v1.5.3 Evidence Summary

## Verdict

ACCEPTED.

## Scope

- Track: `v1.5.3_python_rtdl_reduced_copy`
- Primitive: `COLLECT_K_BOUNDED`
- Surface: `typed_host_input_plus_prepared_host_output`

## Parity

- Accepted: `True`
- Required backends: embree, optix
- `embree`: pass=4 fail=0 skipped=0
- `optix`: pass=4 fail=0 skipped=0

## Diagnostic Sweep

- `embree`: ratio_min=0.327082 ratio_max=0.437241 materialization_deltas=19, 19, 11
- `optix`: ratio_min=0.343359 ratio_max=0.436971 materialization_deltas=19, 19, 11

## Evidence Paths

- `docs/reports/goal1467_v1_5_3_typed_host_buffer_pod_results_2026-05-07/goal1467_typed_host_buffer_parity_required_2026-05-07.json`
- `docs/reports/goal1472_v1_5_3_typed_host_reuse_sweep_pod_2026-05-07.json`
- `docs/reports/goal1470_v1_5_3_typed_host_pod_parity_acceptance_2026-05-07.md`
- `docs/reports/goal1472_v1_5_3_typed_host_reuse_sweep_pod_2026-05-07.md`

## Boundary

This summary accepts same-contract Embree+OptiX parity and diagnostic typed-host reuse evidence for the named v1.5.3 subpath only. It does not authorize true zero-copy, public speedup wording, whole-app claims, stable primitive promotion, partner tensor handoff, or release action.
