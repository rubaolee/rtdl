# Handoff: Claude Review Goal3331 RayJoin Topology / Owner-Face Chain

Please perform an independent read-only review of the recent RayJoin PIP count-boundary chain:

- Goal3327: `docs/reports/goal3327_rayjoin_pip_extra_shape_id_diagnosis_2026-06-04.md`
- Goal3328: `docs/reports/goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.md`
- Goal3329: `docs/reports/goal3329_optix_device_pair_columns_cupy_adapter_2026-06-04.md`
- Goal3330: `docs/reports/goal3330_owner_face_closed_shape_membership_reference_contract_2026-06-04.md`
- Source files:
  - `src/rtdsl/optix_runtime.py`
  - `src/rtdsl/datasets.py`
  - `src/rtdsl/closed_shape_topology.py`
  - `src/rtdsl/__init__.py`
- Tests:
  - `tests/goal3327_rayjoin_pip_extra_shape_id_diagnosis_test.py`
  - `tests/goal3328_rayjoin_cdb_topology_shape_id_probe_test.py`
  - `tests/goal3329_optix_device_pair_columns_cupy_adapter_test.py`
  - `tests/goal3330_owner_face_closed_shape_membership_reference_contract_test.py`

Write your review to:

- `docs/reviews/goal3331_claude_review_rayjoin_topology_owner_face_chain_2026-06-04.md`

## Review Questions

1. Does Goal3327 correctly narrow the county CDB count mismatch from scalar overcount to concrete extra `shape_id` rows while keeping all claims blocked?
2. Does Goal3328 correctly support the topology/ownership diagnosis without implying RayJoin semantics belong in the native engine?
3. Is Goal3329's `OptixNativeDevicePairColumnOutput.as_cupy_columns()` generic, safe, and claim-bounded?
4. Is Goal3330's owner-face membership reference contract app-agnostic, or does it accidentally smuggle CDB/RayJoin policy into RTDL?
5. Are the tests sufficient for the current diagnostic/reference stage?
6. What must be true before this chain can become a native/device primitive rather than a Python reference contract?

## Required Boundaries

- Do not authorize v2.8 release, public speedup, broad RT-core speedup, RTDL-beats-RayJoin, RayJoin paper reproduction, or true zero-copy claims.
- Treat the current fast count route as fail-closed outside validated domains.
- Keep app/dataset ownership policy outside the native engine.
- Use one of the allowed verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Suggested Local Validation

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest `
  tests.goal3330_owner_face_closed_shape_membership_reference_contract_test `
  tests.goal3329_optix_device_pair_columns_cupy_adapter_test `
  tests.goal3328_rayjoin_cdb_topology_shape_id_probe_test `
  tests.goal3327_rayjoin_pip_extra_shape_id_diagnosis_test `
  tests.goal3326_cdb_topology_rows_test `
  tests.goal3324_closed_shape_topology_membership_candidate_test
```
