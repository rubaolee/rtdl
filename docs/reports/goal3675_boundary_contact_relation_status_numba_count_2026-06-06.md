# Goal3675 Boundary-Contact Relation Status And Numba Count

Date: 2026-06-06

Status: internal performance-hardening evidence, not release authorization.

## Purpose

Goal3675 tests a broad-CDB RayJoin PIP blocker on the current RTDL v2.9/v-next lane:
the fastest prepared-points scalar count route is very fast, but on the full county
slice it overcounts by 308 rows. Prior owner-side repairs could recover exact rows,
but they required app/data policy and did not give a clean generic runtime primitive.

This goal adds a more generic signal:

- native OptiX candidate streams now expose a relation-status column;
- boundary-status rows also expose the generic boundary-element ordinal that caused
  the candidate acceptance;
- the Python partner layer can refine or count those candidates without RayJoin/CDB
  vocabulary entering the native engine;
- a Numba CUDA count-only continuation is provided for users who need custom logic
  without writing CuPy RawKernel/CUDA C strings.

## Implementation

Native generic columns:

- `relation_status` values:
  - `1`: accepted by closed-shape interior predicate;
  - `2`: accepted by closed-shape boundary predicate;
  - `0`: unknown/not accepted, rejected by safe refiners.
- `relation_boundary_ordinal`:
  - boundary element ordinal for status `2`;
  - sentinel `0xffffffff` otherwise.

Python partner continuations:

- `PreparedClosedShapeMembershipCandidateRefinerCupy.refine_boundary_contacts(...)`
  verifies only the emitted boundary element and compacts exact rows.
- `PreparedClosedShapeMembershipCandidateRefinerCupy.count_boundary_contacts_numba(...)`
  counts exact accepted candidates with Numba CUDA and does not materialize a row stream.
- Both paths default to safe validation. A caller may explicitly set
  `validate_columns=False` for trusted native streams produced immediately by RTDL.

Current carrier boundary: the prepared refiner still uses CuPy arrays as the
device-memory carrier because the OptiX column handoff currently exposes CuPy
views. The custom continuation logic for the count-only route is Numba CUDA,
not CuPy RawKernel or user-written CUDA C. A future partner-neutral carrier can
remove the CuPy carrier dependency without changing the generic relation-status
contract.

The native engine remains app-agnostic: it exposes relation status and boundary
element ordinals, not RayJoin maps, CDB faces, county ownership, or GIS policy.

## A5000 Evidence

Pod:

```text
ssh root@69.30.85.203 -p 22057 -i id_ed25519_rtdl_codex
GPU: NVIDIA RTX A5000, driver 580.126.09
Repo path: /root/rtdl
OptiX library: /root/rtdl/build/librtdl_optix.so
Runtime env: PYTHONPATH=src:., RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS=1e-9
Numba env: /root/rtdl/.venv_numba, numba 0.65.1, cupy 14.1.1
```

Dataset:

```text
data/rayjoin_public_cdb/br_county_start0_count16545.cdb
points: 16545
shapes: 15700
exact count: 47262
candidate rows from relation-status stream: 47264
```

Artifact:

```text
docs/reports/goal3675_rayjoin_pip_full_county_candidate_refine_timing_a5000/summary_boundary_contact_numba_count_resident_stream_diagnostic.json
```

Hot medians, 10 repeats after 3 warmups:

| Route | Median sec | Exact? | Count / rows | Notes |
| --- | ---: | --- | ---: | --- |
| prepared-points device-filtered scalar count | 0.000416 | no | 47570 | fastest, but +308 over exact |
| candidate columns + full CuPy simple-ring refine | 0.024268 | yes | 47262 | exact row stream; row materialization path |
| candidate columns + fused boundary-contact CuPy refine | 0.023279 | yes | 47262 | exact row stream; still compact-output dominated |
| candidate columns + Numba boundary-contact count | 0.021484 | yes | 47262 | exact scalar count; still pays one-shot stream allocation/free |
| resident candidate columns + Numba boundary-contact count | 0.001502 | yes | 47262 | exact scalar count over reused device stream |

Additional diagnostic:

- native candidate traversal median inside the one-shot column routes is about `0.00044 s`;
- the large `0.021-0.024 s` one-shot exact timings are therefore not caused by RT traversal;
- they are caused by the current stream allocation/free/materialization contract and
  compacted row-output shape.

## Design Conclusion

Goal3675 gives a precise answer to the current RayJoin PIP performance question.

The RT traversal is already fast. The weak contract is the device stream handoff:
for count-only workloads, the current exact route materializes or owns a candidate
row stream even when the caller only needs a scalar count. A count-only continuation
should not use per-kept-row output atomics, should not allocate/free a full row stream
on every call, and should not copy rows to host for timing.

The next major runtime target should therefore be one of these generic primitives:

- reusable native output buffers for closed-shape candidate streams;
- a generic exact scalar-count primitive using relation-status and boundary-contact
  correction without materialized row output;
- or a device-resident stream owner that can be reused across repeated queries and
  consumed by Numba/CuPy without per-call allocation/free.

This is a language/runtime problem, not a RayJoin-specific trick.

## Claim Boundary

This goal does not authorize:

- RTDL beats RayJoin;
- RayJoin paper reproduction;
- public RT-core speedup claims;
- release readiness;
- true zero-copy claims;
- a default broad-CDB PIP route.

Accepted claim scope:

- RTDL/OptiX can emit app-agnostic relation-status and boundary-ordinal columns;
- a Numba CUDA continuation can consume those columns and produce the exact full-county
  count without user-written CUDA strings;
- resident candidate-stream timing demonstrates that reusable device-resident stream
  ownership is the next high-value runtime primitive.

## Validation

Local Windows:

```text
py -3 -m py_compile src/rtdsl/closed_shape_topology.py scripts/goal3675_rayjoin_pip_full_county_candidate_refine_timing.py tests/goal3675_closed_shape_candidate_relation_status_columns_test.py
PYTHONPATH=src;. py -3 -m unittest tests.goal3675_closed_shape_candidate_relation_status_columns_test
PYTHONPATH=src;. py -3 -m unittest tests.goal3675_closed_shape_candidate_relation_status_columns_test tests.goal3673_ordinal_selective_owner_side_filter_test tests.goal3671_side_aware_owner_face_filter_test
```

Pod:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal3675_closed_shape_candidate_relation_status_columns_test
. .venv_numba/bin/activate
PYTHONPATH=src:. python -m unittest tests.goal3675_closed_shape_candidate_relation_status_columns_test
timeout 900 python scripts/goal3675_rayjoin_pip_full_county_candidate_refine_timing.py --repeat 10 --warmup 3 --output docs/reports/goal3675_rayjoin_pip_full_county_candidate_refine_timing_a5000/summary_boundary_contact_numba_count_resident_stream_diagnostic.json
```

## Independent Review

- Gemini review: `docs/reviews/goal3676_gemini_review_goal3675_boundary_contact_numba_count_2026-06-06.md`, verdict `accept`.
- Claude review was attempted with `docs/handoff/HANDOFF_CLAUDE_GOAL3675_BOUNDARY_CONTACT_NUMBA_COUNT_REVIEW_2026-06-06.md`, but Claude returned a weekly-limit message and no review file was produced. This does not count as Claude consensus.
