# Handoff: Claude Review Goal3334 RayJoin Owner-Face Full Chain

This supersedes the narrower Goal3331 handoff by including the catalog wiring and negative owner-face availability evidence.

Please perform an independent read-only review of the RayJoin PIP count-boundary chain:

- Goal3320: full/slice validation boundary
- Goal3321: fail-closed preflight
- Goal3322: per-point mismatch diagnosis
- Goal3324: topology-aware closed-shape membership candidate primitive
- Goal3326: CDB topology row helper
- Goal3327: extra shape-id diagnosis
- Goal3328: CDB topology shape-id probe
- Goal3329: generic OptiX pair-column `as_cupy_columns()` adapter
- Goal3330: owner-face closed-shape membership Python reference contract
- Goal3332: primitive catalog wiring to the owner-face reference contract
- Goal3333: negative owner-face availability probe

Write the review to:

- `docs/reviews/goal3334_claude_review_rayjoin_owner_face_full_chain_2026-06-04.md`

## Key Questions

1. Does the chain correctly keep the current fast count route fail-closed outside validated domains?
2. Is the Goal3330 owner-face contract genuinely app-agnostic, with CDB/RayJoin ownership supplied by the caller rather than inferred by the engine?
3. Does Goal3333 correctly prevent overclaiming by showing simple left/right point-chain owner-face policies are insufficient?
4. Is the Goal3329 CuPy pair-column adapter a safe generic ergonomics improvement?
5. Does Goal3332 wire the new reference contract into primitive discovery without prematurely promoting the primitive?
6. What is the next engineering step before any native/device implementation is justified?

## Must-Check Files

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/datasets.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/primitive_hierarchy.py`
- `docs/rtdl_primitive_catalog.md`
- `docs/reports/goal3330_owner_face_closed_shape_membership_reference_contract_2026-06-04.md`
- `docs/reports/goal3333_rayjoin_probe_point_owner_face_availability_2026-06-04.md`

## Suggested Validation

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest `
  tests.goal3333_rayjoin_probe_point_owner_face_availability_test `
  tests.goal3332_owner_face_contract_primitive_catalog_wiring_test `
  tests.goal3330_owner_face_closed_shape_membership_reference_contract_test `
  tests.goal3329_optix_device_pair_columns_cupy_adapter_test `
  tests.goal3328_rayjoin_cdb_topology_shape_id_probe_test `
  tests.goal3327_rayjoin_pip_extra_shape_id_diagnosis_test `
  tests.goal3326_cdb_topology_rows_test `
  tests.goal3324_closed_shape_topology_membership_candidate_test `
  tests.goal3322_rayjoin_pip_per_point_mismatch_diagnosis_test `
  tests.goal3321_rayjoin_pip_validated_domain_preflight_test `
  tests.goal3320_rayjoin_pip_validation_boundary_test
```

Expected local result from Codex:

```text
Ran 37 tests in 0.069s
OK
```

## Required Boundaries

- Do not authorize release, public speedup, broad RT-core speedup, true zero-copy, RTDL-beats-RayJoin, or RayJoin paper reproduction claims.
- Keep native engine app-agnostic.
- Treat the current RayJoin count fast route as validated-domain-only.
- Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.
