# Goal3395 — Claude Review: OptiX Exact Device Columns Bridge (Goal3394)

**Date:** 2026-06-04
**Reviewer:** Claude (external, read-only)
**Verdict:** accept-with-boundary

---

## Scope

Review of the Goal3394 native bridge that exposes exact host-refined
point/closed-shape membership pairs as native-owned CUDA device columns via:

- Native ABI: `rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_2d`
- Release ABI: `rtdl_optix_release_point_closed_shape_membership_exact_device_columns_2d`
- Python: `PreparedOptixPointClosedShapeMembership2D.exact_device_columns(points)`

Files inspected:

- `src/native/optix/rtdl_optix_prelude.h` (struct definitions, ABI declarations)
- `src/native/optix/rtdl_optix_workloads.cpp` (implementation, lines 8163–8242)
- `src/native/optix/rtdl_optix_api.cpp` (C ABI wrapper, lines 594–650)
- `src/rtdsl/optix_runtime.py` (Python method and metadata, lines 1588–1622, 10658–10734)
- `scripts/goal3394_optix_exact_membership_device_columns_live_probe.py`
- `docs/reports/goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json`
- `docs/reports/goal3394_optix_exact_membership_device_columns_bridge_2026-06-04.md`
- `tests/goal3394_optix_exact_membership_device_columns_bridge_test.py`

---

## Q1 — ABI naming and app-agnosticism

The symbol is correctly named. It follows the established naming pattern for the
prepared-handle family:

```
rtdl_optix_prepared_point_closed_shape_membership_candidate_device_columns_2d  (candidate)
rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_2d      (exact, new)
rtdl_optix_prepared_point_closed_shape_membership_point_id_count_device_columns_2d  (count)
```

The `exact` token is positioned correctly between `membership` and
`device_columns` — it identifies the semantic kind of the output stream, not
a specific application, dataset, or tolerance. The release symbol follows the
same `release_…_exact_device_columns_2d` suffix convention. The struct output
type (`RtdlNativeDevicePairColumns`) is the existing generic pair-column type
shared with the candidate and RayJoin hit-stream families. No app-specific
fields or specializations were introduced.

**Finding: pass.**

---

## Q2 — Implementation boundary honesty

The core implementation is `run_prepared_point_closed_shape_membership_exact_device_columns_2d_optix()`
(workloads.cpp:8163–8237).

The execution path is:
1. Call `run_prepared_point_closed_shape_membership_2d_optix(prepared, points, point_count, 1u, &exact_rows, &exact_count)` — the existing exact host-refined path with `positive_only=1`. Host memory.
2. If exact_count == 0 or exact_count > max_rows: return early, no device allocation.
3. Allocate two `CUdeviceptr` buffers (`cuMemAlloc`) of `sizeof(unsigned long long) * exact_count`.
4. Widen the uint32 IDs from the host rows into `std::vector<unsigned long long>` and `upload()` to device.
5. Hand ownership via `NativeClosedShapeMembershipCandidateDeviceColumnsOwner` and fill `RtdlNativeDevicePairColumns`.

All three boundary invariants hold:

| Invariant | Observed |
|---|---|
| Host-refined exact rows inside native bridge | ✓ `run_prepared_point_closed_shape_membership_2d_optix` called internally |
| Exact pair columns are native-owned device-resident | ✓ `cuMemAlloc` + upload, owner handle released by separate C ABI call |
| Device-only exact predicate production: false | ✓ explicit in metadata at all three layers; no direct BVH-traversal exact predicate written |

The overflow guard (line 8209) fires before any device allocation occurs, so an
overflow result leaves no dangling device memory. The null-pointer guard on the
prepared handle appears in both the workloads.cpp static function and the api.cpp
C ABI wrapper, providing defense-in-depth without being excessive.

One structural observation: `columns_out->candidate_event_count` is populated
with `exact_count` (line 8201). The field name "candidate" is a semantic
mismatch for an exact stream — it was inherited from the `RtdlNativeDevicePairColumns`
struct that is shared with the candidate-stream path. This is not a correctness
defect (the live probe confirms exact pair identity), but it is a pre-graduation
ABI smell. A future exact-native ABI pass might introduce a dedicated
`exact_event_count` field or separate struct, at the cost of changing the
consumer interface.

**Finding: pass with noted ABI smell.**

---

## Q3 — Python method and metadata after metadata correction

The `exact_device_columns` method (optix_runtime.py:10658–10734) is clean. It:

- Detects missing symbols and raises an informative `RuntimeError` rather than
  silently using a default (lines 10676–10691).
- Uses `OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_SYMBOL` (not the
  candidate symbol) for both the run and release bindings.
- Names the `OptixNativeDevicePairColumnOutput` with `native_symbol=OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_SYMBOL`
  and `field_names=("point_id", "shape_id")`.
- Default capacity formula: `max(1, point_count * polygon_count)`, which is
  conservative and avoids under-allocation at the cost of potentially large
  pre-allocation for dense datasets. This is acceptable for a bridge at this
  maturity level.

The `to_metadata()` method (lines 1591–1621) branches on
`native_symbol == OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_SYMBOL`
and applies an explicit overlay:

```python
stream_metadata["stream_id"]         = "point_closed_shape_membership_2d_exact_device_columns"
stream_metadata["stream_kind"]       = "exact_relation_stream"
stream_metadata["producer_primitive"] = "point_closed_shape_membership_2d_exact_host_refined"
stream_metadata["status"]            = "internal_contract_host_refined_exact_device_columns"
producer_metadata["producer_output_residency"] = "device_resident_exact_id_columns"
producer_metadata["host_refined_exact_rows_inside_native_bridge"] = True
producer_metadata["device_only_exact_predicate_produced"]         = False
```

This correctly prevents candidate-stream metadata from leaking into an exact
result. The runtime block (`output_residency`) uses a conditional to distinguish
the exact-device-resident case from the candidate-device-resident case from
empty/overflow. The three-branch logic is correct given the field reuse on
`RtdlNativeDevicePairColumns`.

The JSON artifact confirms all these fields are set correctly at runtime
(`rtdl_commit: 87a2acbb`, after the metadata correction commit).

**Finding: pass.**

---

## Q4 — Live probe: exact pair identity and device residency

Probe configuration: RTX A5000 pod, BR county dataset, chains 256–4351 (4096
chains, 3762 shapes).

| Measure | Expected | Observed |
|---|---|---|
| Exact host-refined rows | — | 11316 |
| Native exact device-column rows | == host rows | 11316 |
| Missing exact pairs | 0 | 0 |
| Extra pairs | 0 | 0 |
| Device resident | true | true |
| Overflow | false | false |
| Native symbol | `…exact_device_columns_2d` | confirmed |

The probe correctly performs a bidirectional set-difference check
(`exact_pairs - column_pairs` and `column_pairs - exact_pairs`) rather than
just a row-count comparison. Both differences are empty. Device residency is
confirmed by `columns.device_resident`.

The traversal time (0.001482 s) includes host-to-device upload and covers a
4096-point × 3762-shape problem. This time reflects the full bridge cost
including the host-refined exact computation and is consistent with the existing
GoalXXXX candidate-stream timings seen elsewhere in this project.

**Finding: strong evidence for exact pair identity and device residency on a
realistic 4096-chain probe.**

---

## Q5 — Claim boundaries

All claim boundary flags are blocked at every layer:

| Claim | JSON top-level | typed_result_stream | v2_8_typed_producer_metadata |
|---|---|---|---|
| `release_authorized` | false | false | false |
| `public_speedup_claim_authorized` | false | false | false |
| `rayjoin_paper_reproduction_claim_authorized` | false | — | — |
| `rtdl_beats_rayjoin_claim_authorized` | false | — | — |
| `rt_core_speedup_claim_authorized` | false | false | false |
| `true_zero_copy_claim_authorized` | false | false | false |
| `native_default_route_authorized` | false | — | — |

The typed-result-stream `claim_boundary` string explicitly lists the full
prohibition: release, public speedup wording, broad RT-core wording,
true-zero-copy wording, hidden dispatch, hidden partner selection,
app-specific native-engine behavior, user-defined shader injection.

The v2_8_typed_producer_metadata carries the same prohibition. The Codex
self-report (docs/reports/…md) repeats it in plain English.

The test `test_claim_boundaries_stay_blocked` iterates every `claim_boundary`
key and asserts it is false. The test `test_metadata_labels_exact_host_refined_bridge_not_candidate_stream`
asserts the implementation boundary flags separately
(`host_refined_exact_rows_inside_native_bridge=true`,
`device_only_exact_predicate_produced=false`).

**Finding: pass. Claim boundaries are blocked redundantly and mechanically
enforced by the test suite.**

---

## Q6 — What remains before graduation from bridge to final primitive

The following gaps must be addressed before this can graduate to a final
production primitive, roughly in priority order:

**1. Device-only exact predicate (blocking)**
The current bridge calls `run_prepared_point_closed_shape_membership_2d_optix`
on the host and uploads results. For a true native exact stream the exact
membership predicate must be computed on the GPU without host-side row
materialization. This requires a robust device-side winding-number or
signed-crossing accumulator. Until then, the bridge cannot claim OptiX-native
exact membership, only OptiX-native exact pair *upload*.

**2. GEOS/double parity test**
The codebase has conditional GEOS support (`RTDL_OPTIX_HAS_GEOS`). There is no
probe in this work that cross-validates the exact host-refined rows against a
GEOS-based reference for numerically ambiguous cases (near-boundary points,
vertex-coincident points, self-intersecting polygon rings). Until a GEOS parity
probe exists, the exact path has unknown behavior on degenerate geometry.

**3. Relation-witness stream**
`exact_relation_witness_rows_materialized` is false in all metadata. Downstream
consumers (e.g., grouped continuation, shape-pair relation) may need the
*evidence* for each membership decision, not just the pair IDs. A richer
witness stream — encoding which ray crossing established membership — is
identified in Goal3393's accepted direction and remains unimplemented.

**4. Overflow streaming / chunking fallback**
When `exact_count > max_rows` the bridge returns overflow=1 with no rows and no
partial result. The default capacity formula `point_count * polygon_count`
prevents this for moderate inputs but becomes a large pre-allocation for dense
datasets. A streaming or chunked fallback would improve robustness before
graduating to a recommended path.

**5. Multi-dataset coverage**
Only the BR county dataset at a single chain window (256–4351) has been probed.
Validation against at least one additional dataset (different polygon density,
presence of holes, or international coordinate ranges) would increase confidence
before widening adoption.

**6. ABI field naming (`candidate_event_count`)**
See Q2. The reuse of `candidate_event_count` in `RtdlNativeDevicePairColumns`
for an exact count is a pre-graduation ABI smell. Not blocking for the bridge,
but should be resolved before the exact primitive is exposed as a first-class
API surface.

---

## Summary

Goal3394 correctly implements the first native bridge step agreed in Goal3393.
The native ABI is app-agnostic and correctly named. The implementation boundary
is honest: host-refined exact rows are computed inside the bridge, pair IDs are
uploaded to native-owned device memory, and device-only exact predicate
production remains false at every metadata layer. The metadata correction at
commit `87a2acbb` correctly distinguishes the exact stream from the candidate
stream and the test suite mechanically enforces the boundary. The live 4096-chain
probe provides strong evidence of exact pair identity (11316/11316, 0 missing,
0 extra). All release, speedup, RayJoin, RT-core, zero-copy, and default-route
claims are blocked redundantly across the JSON artifact, the metadata contract
strings, and the test assertions.

The primary graduation blocker is the host-refined exact path inside the native
bridge. This bridge does not authorize release or any public performance claim.
It is an honest internal contract.

**Verdict: accept-with-boundary.**
