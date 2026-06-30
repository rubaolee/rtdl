# Handoff: Claude Review Goal3336 RayJoin Owner-Face Derivation Chain

This supersedes the Goal3331 and Goal3334 handoffs. Please review the full current RayJoin PIP count-boundary / owner-face chain through Goal3335.

Expected review output:

- `docs/reviews/goal3336_claude_review_rayjoin_owner_face_derivation_chain_2026-06-04.md`

## Scope

Review these goals:

- Goal3320: validation boundary showing broad CDB mismatch exists.
- Goal3321: app-level fail-closed preflight.
- Goal3322: per-point mismatch diagnosis.
- Goal3324: topology-aware closed-shape membership candidate primitive.
- Goal3326: generic CDB topology row helper.
- Goal3327: extra shape-id diagnosis.
- Goal3328: topology shape-id probe.
- Goal3329: generic OptiX pair-column CuPy adapter.
- Goal3330: owner-face closed-shape membership Python reference contract.
- Goal3332: primitive catalog wiring.
- Goal3333: negative probe showing point-chain left/right owner-face policies are insufficient.
- Goal3335: incident-face probe showing the needed owner face is present in local topology for 7/7 known mismatches but tied with other faces, so a deterministic derivation contract is still needed.

## Main Questions

1. Does this chain correctly move from "fast route mismatch" to a generic owner-face/topology contract without putting RayJoin/CDB semantics into the native engine?
2. Is Goal3330 a valid app-agnostic Python reference contract for future native/device lowering?
3. Do Goals3333 and 3335 correctly prevent overclaiming by showing owner-face input is not trivially available and tie-breaking remains unresolved?
4. Is Goal3329's `as_cupy_columns()` helper safe and useful for partner continuations?
5. Does the primitive catalog wiring keep the primitive at candidate status and point to the executable reference contract?
6. What should the next engineering target be: owner-face derivation reference, device owner-face filter, or broader topology event stream?

## Suggested Validation

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest `
  tests.goal3335_rayjoin_incident_face_owner_probe_test `
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

Codex observed:

```text
Ran 40 tests in 0.049s
OK
```

## Boundaries

- Do not authorize release, public speedup, broad RT-core speedup, RTDL-beats-RayJoin, RayJoin paper reproduction, or true zero-copy claims.
- Keep the current fast PIP count route validated-domain-only.
- Keep native engine app-agnostic; owner-face policy must be supplied or derived through generic topology contracts.
- Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
