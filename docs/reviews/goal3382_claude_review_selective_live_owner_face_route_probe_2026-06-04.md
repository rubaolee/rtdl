# Claude Review: Goal3381 Selective Live Owner-Face Route Probe

**Date:** 2026-06-04

**Reviewer:** Claude (Sonnet 4.6)

**Verdict: `accept-with-boundary`**

---

## Scope

Read-only external review of Goal3381 and its supporting chain (Goal3376,
Goal3378, Goal3380). Source files inspected:

- `scripts/goal3381_owner_face_selective_live_route_probe.py`
- `docs/reports/goal3381_owner_face_selective_live_route_probe_2026-06-04.json`
- `docs/reports/goal3381_owner_face_selective_live_route_probe_2026-06-04.md`
- `tests/goal3381_owner_face_selective_live_route_probe_test.py`
- `src/rtdsl/closed_shape_topology.py`
- `tests/goal3380_selective_owner_face_cupy_pipeline_test.py`
- `docs/reports/goal3378_owner_face_all_point_priority_negative_probe_2026-06-04.md`
- `docs/reports/goal3376_owner_face_cupy_optix_candidate_route_probe_2026-06-04.md`

---

## Q1: Live OptiX candidate device columns for the full slice?

**Pass.**

The script makes three live GPU calls on the full 512-chain slice before any
CuPy continuation runs:

```python
prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
exact_rows = tuple(prepared.run(points))            # live exact oracle
candidate_columns = prepared.candidate_device_columns(points)   # live candidates
candidates = candidate_columns.as_cupy_columns()
```

Topology and incident rows are both derived at runtime from the CDB:

```python
topology_rows = rt.chains_to_topology_rows(county)
selected_metadata = _runtime_selected_metadata(county, selected_points)
```

The JSON artifact records all four stored-artifact flags as `false` and
confirms `candidate_rows_from_optix_device_columns: true`,
`exact_oracle_generated_by_live_optix_run: true`, and
`optix_candidate_device_resident: true`. The test
`test_stored_artifacts_are_not_used_as_route_inputs` verifies each flag
programmatically, so any future probe that accidentally replays stored inputs
will fail the test suite.

No concern: the script passes through a `finally` block that calls
`candidate_columns.close()` and `prepared.close()`, so GPU resources are
released even when an exception interrupts the probe.

---

## Q2: App-agnostic primitive, caller-supplied policy?

**Pass, with one clarifying observation.**

The `run_selective_closed_shape_owner_face_priority_membership_pipeline_cupy`
function in `closed_shape_topology.py` (line 981) receives `selected_point_ids`
as an explicit parameter and its docstring states: "The caller supplies
`selected_point_ids` as the explicit ambiguity set. RTDL does not infer which
points need owner-face reconciliation." The output carries
`selected_point_filter_mode: "caller_supplied_ambiguity_set"`. The primitive
itself is entirely app-agnostic; it knows nothing about CDB geometry, RayJoin,
or GIS semantics.

The contract objects `owner_face_membership_contract()` and
`owner_face_priority_pipeline_contract()` are backed by runtime validation
functions that raise if `native_engine_may_infer_app_ownership` or
`native_engine_may_invent_priority` are ever set to `True`.

**Clarifying observation (not a blocker):** The rank signal construction in
`_runtime_selected_metadata` uses:

```python
rank0.append(0 if face_id == OWNER_FACE_BY_POINT[point_id] else 10 + face_id)
```

This assigns priority 0 to whichever face is already known to be correct from
the `OWNER_FACE_BY_POINT` fixture. The priority is therefore not derived from
independent geometric evidence — it is derived from the known answer. This is
the right design for a probe (verifying that the pipeline routes correctly when
given ground-truth input), but it means the rank signal cannot be re-used
directly for a default route. Any future default route must derive the priority
from topological or geometric signals that do not depend on a pre-known answer
table. The probe is honest about this: both the JSON `selected_owner_face_source`
field (`"caller_supplied_fixture_policy_for_known_mismatch_points"`) and the
report boundary section make the fixture-dependency explicit.

---

## Q3: Honest full-slice exact-row parity?

**Pass. Arithmetic is internally consistent and independently verifiable.**

| Measure | Claimed | Verified |
| --- | ---: | ---: |
| OptiX candidate rows | 1429 | 1429 |
| Live exact rows | 1417 | 1417 |
| Candidate extras before filter | 12 | 1429 − 1417 = 12 ✓ |
| Selected ambiguity candidates | 26 | JSON field ✓ |
| Passthrough candidates | 1403 | 1429 − 26 = 1403 ✓ |
| Selected filtered rows | 14 | JSON field ✓ |
| Removed candidate extras | 12 | 26 − 14 = 12 ✓ |
| Final filtered rows | 1417 | 1403 + 14 = 1417 ✓ |
| Missing exact rows | 0 | ✓ |
| Extra rows | 0 | ✓ |

The twelve removed extras are all from the seven known ambiguity points (two
extras per point in the larger cluster, one each in the smaller clusters),
consistent with the Goal3376 live candidate table. The passthrough path
contributes zero extras or drops, which is the expected behavior for non-ambiguous
candidates.

The test `test_full_slice_matches_live_exact_oracle` pins every numeric
claim, and `test_selective_pipeline_repairs_only_caller_supplied_ambiguity_set`
pins the per-point and pass-through counts plus the full removed-extra sample.
If the artifact were manually edited to fabricate parity, the tests would
catch the mismatch on next pod run because they verify the artifact against
hardcoded expected values.

---

## Q4: Claim boundaries correctly blocked?

**Pass.**

The JSON `claim_boundary` object carries seven `false` flags:

```json
"native_default_route_authorized": false,
"public_speedup_claim_authorized": false,
"rayjoin_paper_reproduction_claim_authorized": false,
"release_authorized": false,
"rt_core_speedup_claim_authorized": false,
"rtdl_beats_rayjoin_claim_authorized": false,
"true_zero_copy_claim_authorized": false
```

The test `test_claim_boundary_blocks_public_and_default_route_claims` iterates
all seven flags and asserts each is `False`, then checks three specific strings
in the report text: "does not authorize a default route", "does not infer those
points automatically", and "claim-boundary flags remain false". The
`validate_owner_face_priority_pipeline_contract()` and
`validate_owner_face_membership_contract()` functions add a third enforcement
layer in source: they raise `ValueError` at runtime if any claim-boundary flag
is ever set to `True` in the contract objects.

The probe's own `interpretation` string inside the JSON also restates the
boundary correctly: "it does not discover the ambiguity set, authorize a native
default route, prove zero-copy, or reproduce the RayJoin paper."

No overclaim language detected in any of the inspected files.

---

## Q5: Next highest-risk missing piece

**Ambiguity-set discovery is the primary blocker**, and it is load-bearing in
two distinct ways:

1. **Which points are ambiguous?** The current probe hardcodes the seven
   Goal3328 mismatch points. There is no mechanism in the native engine or
   CuPy continuation to decide at runtime which candidate points need
   owner-face reconciliation. Until a discoverable ambiguity criterion exists,
   the selective pipeline cannot be invoked correctly on an arbitrary CDB
   input — the caller must know the answer in advance.

2. **Which face is the owner?** The rank signal currently encodes the correct
   answer from the fixture. For a default route, the priority must come from
   an independent geometric or topological policy (e.g., boundary-shape
   winding, incident-face area, or a validated signed-distance rule). Goal3378
   already proved that naive incident-chain-length priority drops 410 true exact
   rows when applied globally, so a correct discovery policy is non-trivial.

The secondary risks, roughly in order:

- **Scale.** The probe covers only 512 chains. The county dataset has
  substantially more chains. Behavior at larger CDB scales — including whether
  the number of ambiguous boundary points grows linearly, sub-linearly, or
  non-linearly — is not yet characterized.
- **Stronger topology policy.** Goal3378 showed that applying the current
  priority signal to all points drops true exact rows. A better policy might
  gate owner-face repair on a topology-observable condition (e.g., the
  candidate point lies exactly on the topological boundary between two faces)
  rather than relying on the caller to enumerate mismatch points.
- **Native lowering status.** The `owner_face_priority_pipeline_contract()`
  explicitly marks `native_lowering_status: "blocked_until_contract_stable_and_validated"`.
  Even if the above gaps are closed, the CuPy continuation is not yet a
  candidate for lowering into the native RT engine.

---

## Additional Observations

**Test coverage is well-matched to the artifact.** Five focused tests cover: full-
slice parity, selective-pipeline specifics, stored-artifact flags, claim-boundary
text, and live-API calls. The local `skipped=1` result is expected (CuPy tests
skip on hosts without a CUDA device) and pod runs confirm all five pass on GPU.

**Resource management.** The `try/finally` guard around `candidate_columns.close()`
and `prepared.close()` is correct. GPU objects are released even if the CuPy
pipeline raises, which matters for long-running pod sessions.

**Commit traceability.** The JSON artifact records `rtdl_commit:
6ee730b9490ed727c18c6374dd2c085dc161a0f5`, which matches the commit visible in
git history for Goal3381. The pod run was performed at a slightly earlier commit
(`23e74ab9` in the handoff document) and all 13 tests passed. The one-commit
gap is the record-artifact commit; no source changes occurred between the pod
run and the record commit.

---

## Verdict

**`accept-with-boundary`**

Goal3381 is an honest, well-scoped probe. The live OptiX candidate path is
genuine, the selective CuPy continuation is app-agnostic at the primitive
level, the arithmetic is internally consistent, and all seven claim-boundary
flags are correctly blocked with multi-layer enforcement. The probe advances
the chain from Goal3376 (seven-point selective repair) through Goal3378
(negative all-point proof) and Goal3380 (selective primitive) to the first
full-slice exact parity result.

The result is accepted for what it claims: evidence that the selective
owner-face continuation contract produces exact parity on this 512-chain slice
when the caller supplies the correct ambiguity set and owner-face policy.

What remains blocked: the ambiguity-set discovery problem, independent
priority derivation, larger-scale validation, native lowering, and all
public-claim categories. The next engineering milestone before any default-route
candidate can be proposed is a generic, non-fixture-dependent ambiguity
detection criterion.
