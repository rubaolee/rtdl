# Goal4414 V3.0 Midterm Review Packet

Date: 2026-06-15

Status: midterm review packet for 3-AI consensus. This document does not authorize public performance claims.

Current commit under review: `7ab19f4a`

## Review Question

After the rapid V3.0 work from M1 through M17, should the project continue V3 implementation in the current direction?

The requested verdict is one of:

- `accept-with-boundary`: continue V3 work under the stated boundaries.
- `needs-more-evidence`: pause implementation until named evidence is added.
- `request-changes`: repair specific code/docs/tests before continuing.
- `reject`: current direction is unsound.

## Scope

In scope:

- V3 governance and plan gates from Goal4392 and Goal4393.
- M8-M17 implementation/evidence since the first design gates.
- Claim boundaries around same-stream, no-hidden-copy, device-residency, partner use, and public performance wording.
- Next work target after M17.

Out of scope:

- Any final V3 release decision.
- Any public RT-core speedup claim.
- Whole-app benchmark publication.
- Paper-reproduction claims.
- Automatic partner or backend selection claims.

## Prior 3-AI Gates

| Gate | Consensus state | Effect |
|---|---|---|
| Goal4392 overall plan | `v3_0_overall_plan_accepted_m1_design_only_implementation_blocked` | Accepted the V3 plan but only opened M1 design. |
| Goal4393 M1 IR | `v3_0_m1_ir_frozen_m2_skeleton_allowed` | Froze the app-agnostic execution-graph IR and allowed M2 planner-skeleton work only. |

Both gates keep these boundaries binding:

- no app-specific public Python API names;
- no app-specific native engine semantics;
- no public performance claim before the release-grade harness and external review;
- partner work must be explicit and disclosed;
- best practical partner and Numba reference are expected for partner-dependent benchmark apps unless omission is justified;
- same-stream/device-resident/no-hidden-copy wording must be evidence-backed.

## Midterm Progress Summary

| Milestone | Evidence | Result | Boundary |
|---|---|---|---|
| M1 | `docs/reports/goal4393_v3_0_m1_execution_graph_ir_design_2026-06-15.md` | Frozen IR design after 3-AI review. | No native execution or claims. |
| M2-M7 | `docs/reports/goal4394*` through `goal4399*` | Local planner, instrumentation, component/topology/frontier/harness preparation. | Mostly static/local prep. |
| M8 | `goal4402_v3_0_m8_aggregate_frontier_measured_lowering_2026-06-15.md` | Same-contract native Embree/OptiX lowering at up to 6s scale; parity passed. | Not RT-core speedup evidence; rows host-materialized. |
| M9 | `goal4403_v3_0_m9_grouped_stream_partner_2026-06-15.md` | CuPy and Numba partner rows work for grouped-stream device-resident route; Numba/PTX blocker fixed. | Sub-ms evidence, no same-stream/no-hidden-copy yet. |
| M10 | `goal4406_v3_0_m10_same_stream_evidence_2026-06-15.md` | CUDA-event same-stream producer-to-partner proof for CuPy and Numba. | Same-stream only, not zero-copy. |
| M11 | `goal4407_v3_0_m11_no_hidden_copy_evidence_2026-06-15.md` | Fixed-radius grouped-union same-stream handoff passes transfer-counter no-hidden-copy for CuPy and Numba. | Internal readiness only. |
| M12 | `goal4408_v3_0_m12_no_hidden_copy_contract_2026-06-15.md` | App-agnostic no-hidden-copy classifier/validator extracted. | Contract, not app proof. |
| M13 | `goal4409_v3_0_m13_hit_stream_no_hidden_copy_evidence_2026-06-15.md` | Hit-stream row-reduction handoff window passes M12 on second workload. | Starts after native enqueue; not full input path. |
| M14 | `goal4410_v3_0_m14_hit_stream_full_window_transfer_audit_2026-06-15.md` | Full producer+consumer audit exposed expected 262,144-byte per-run ray upload. | Audit only; identified real debt. |
| M15 | `goal4411_v3_0_m15_prepared_hit_stream_no_hidden_copy_evidence_2026-06-15.md` | Prepared ray batch removes per-run query-ray upload; hot path HtoD drops to 88 bytes. | One-time prepare outside window. |
| M16 | `goal4412_v3_0_m16_partner_device_ray_hit_stream_no_hidden_copy_evidence_2026-06-15.md` | Partner-owned CuPy device ray columns feed prepared hot path; hot path still passes. | One-time prepare still had ray-id host bookkeeping debt. |
| M17 | `goal4413_v3_0_m17_partner_device_ray_prepare_no_hidden_copy_evidence_2026-06-15.md` | Device-column prepare now has 0 CUDA transfer calls/bytes; hot path remains 88-byte launch-param HtoD only. | Device-only batch is hit-stream-safe; grouped host-indexed paths fail closed. |

## Most Important Evidence

M10 same-stream evidence:

| Points | Partner | Native event ms | Partner event ms | Same-stream ready |
|---:|---|---:|---:|---|
| 8,192 | CuPy | 0.292 | 0.005 | true |
| 8,192 | Numba | 0.295 | 0.006 | true |
| 65,536 | CuPy | 0.761 | 0.005 | true |
| 65,536 | Numba | 0.762 | 0.007 | true |

M11 no-hidden-copy evidence:

| Points | Partner | Counter calls/bytes | HtoD | DtoH/DtoD/unknown | Verdict |
|---:|---|---:|---:|---:|---|
| 65,536 | CuPy | 1 / 96 | 96 | 0 / 0 / 0 | pass |
| 65,536 | Numba | 1 / 96 | 96 | 0 / 0 / 0 | pass |

M14-M17 hit-stream progression:

| Step | Prepare window | Hot window HtoD | Query rays uploaded each run | Key result |
|---|---|---:|---|---|
| M14 host-packed | not prepared | 262,232 bytes | yes | debt exposed and explained |
| M15 host-prepared | outside measured window | 88 bytes | no | per-run upload removed |
| M16 partner-device-prepared | outside measured window | 88 bytes | no | partner device columns feed hot path |
| M17 partner-device prepare | 0 calls / 0 bytes | 88 bytes | no | prepare ray-id DtoH debt removed |

M17 validation signature:

- `[16384, 16384, 16384, 67100672, 8192, 0, 0, 1]`

Validation:

- Local V3/M17 broad suite: 153 tests passed.
- Pod V3/M17 broad suite: 153 tests passed.
- Pod OptiX rebuild passed with auto-detected `sm_89`.
- Pod runtime smoke passed: host-packed grouped argmin still works; device-column grouped argmin fails closed with a clear host-ray-id bookkeeping error.

## Supported Internal Claims

The current evidence supports these internal engineering claims:

- RTDL has a V3 no-execution graph/metadata skeleton rooted in an externally reviewed app-agnostic IR.
- RTDL can measure same-stream native OptiX producer to Python partner continuation with CUDA events.
- RTDL has an app-agnostic transfer-counter contract for no hidden named-column movement in a measured window.
- The no-hidden-copy contract passes on at least two workload shapes: grouped-union component labels and ray-triangle hit-stream rows.
- Prepared/device-resident ray batches remove the per-run query-ray upload from the hit-stream hot path.
- Partner-owned CuPy device ray columns can be prepared into a hit-stream-safe RTDL ray batch with zero measured CUDA transfer calls in the prepare window.

## Unsupported Claims

The current evidence does not support:

- public V3 performance claims;
- whole-app benchmark speedups;
- author-code parity;
- RT cores generally beating Embree;
- RT cores generally beating CUDA-core partners;
- automatic backend or partner selection;
- arbitrary user OptiX callbacks as stable API;
- grouped argmin over device-only prepared ray batches;
- end-to-end application zero-copy including final scalar/table materialization.

## Midterm Risks

1. **Milestone drift:** M8-M17 advanced faster than the original M2-M7 labels. The work stayed bounded, but future docs should align new evidence milestones with the original plan.
2. **Micro-evidence risk:** M10-M17 are strong systems evidence, but not yet benchmark-app-scale performance proof.
3. **CuPy-heavy hit-stream evidence:** M16/M17 use CuPy for partner device-ray generation and row reduction. Numba remains validated in the grouped-stream path, but not yet in the hit-stream row-reduction path.
4. **Grouped device-only contract gap:** M17 intentionally makes device-column prepared batches fail closed for host-indexed grouped argmin. The next grouped path needs a device-side grouped contract instead of host ray-id bookkeeping.
5. **Public wording risk:** `true_zero_copy_ready=true` appears inside internal M12/M15-M17 metadata for measured windows. Public docs must keep saying "measured-window no-hidden-copy", not end-to-end zero-copy.

## Recommended Next Target

Next target: M18 device-side grouped contract for prepared device-column ray batches.

Reason:

- M17 closed the hit-stream prepare/hot-path data-movement debt.
- The next real limitation is explicit in the runtime smoke: grouped argmin still requires host ray-id bookkeeping.
- A device-side grouped contract would generalize the M17 win from hit-stream row reduction to grouped reductions, which are needed by DBSCAN, RayDB/ranked-summary, RayJoin assembly, and nearest/argmin-style workloads.

M18 should require:

- app-agnostic device-side grouped input contract;
- no app-specific public/native names;
- CuPy best-partner row and Numba reference row, or a written Numba omission if impossible;
- transfer-counter window covering prepare plus grouped execution;
- same-stream/event evidence when a Python partner consumes outputs;
- fail-closed behavior for unsupported host-indexed paths;
- no public speedup wording.

## Questions For Claude And Gemini

1. Is the M1-M17 progress still consistent with the Goal4392/4393 app-agnostic V3 boundary?
2. Are M10-M17 evidence windows honest, or do any claims overreach their measurement windows?
3. Is M17 a valid closure of the M16 ray-id host-bookkeeping debt?
4. Is the fail-closed grouped argmin behavior the right boundary, or should it be treated as a blocker before continuing?
5. Is M18 device-side grouped contract the right next target?
6. What must be fixed before continuing V3 implementation?

## Codex Provisional Verdict

`accept-with-boundary`

Codex recommends continuing V3 work, with M18 as the next target, while preserving the no-public-claims boundary. The current evidence is strong enough for internal architecture progress but not for public performance wording.
