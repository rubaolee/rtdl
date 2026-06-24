# Handoff: Claude Review Goal3338 RayJoin Owner-Face Topology Helper Chain

This supersedes Goal3331, Goal3334, and Goal3336 handoffs. Review the current RayJoin PIP count-boundary chain through Goal3337.

Expected review output:

- `docs/reviews/goal3338_claude_review_rayjoin_owner_face_topology_helper_chain_2026-06-04.md`

## Scope

Review Goals 3320, 3321, 3322, 3324, 3326, 3327, 3328, 3329, 3330, 3332, 3333, 3335, and 3337.

Latest additions beyond Goal3336:

- Goal3337 adds `chains_to_incident_face_candidate_rows(...)` in `src/rtdsl/datasets.py`.
- It exposes generic incident face candidates for probe coordinates without choosing ownership.
- Pod validation for the helper/owner-face chain passed 12 tests on the RTX A5000 pod after fast-forwarding to `a23f77a0`.

## Main Questions

1. Is the chain app-agnostic end to end?
2. Does Goal3337 help future owner-face derivation without smuggling RayJoin/CDB ownership policy into RTDL?
3. Does the evidence honestly show both progress and remaining ambiguity?
4. Should the next engineering step be deterministic owner-face derivation, device owner-face filtering, or broader topology event streams?
5. Are claim boundaries intact?

## Suggested Validation

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest `
  tests.goal3337_incident_face_candidate_rows_helper_test `
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

Codex local checkpoint:

```text
Ran 40 tests in 0.049s
OK
```

Pod checkpoint after Goal3337:

```text
Ran 12 tests in 0.002s
OK
```

## Boundaries

- No release, public speedup, RT-core speedup, true zero-copy, RTDL-beats-RayJoin, or RayJoin paper reproduction claims.
- Current fast PIP count remains validated-domain-only.
- Native engine must remain app-agnostic; owner-face policy is explicit input/derivation, not hidden engine behavior.
- Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
