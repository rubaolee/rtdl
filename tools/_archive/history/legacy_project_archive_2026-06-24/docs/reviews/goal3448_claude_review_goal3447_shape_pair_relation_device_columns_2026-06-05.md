# Review: Goal3447 — Shape-Pair Active Relation Device Columns

**Reviewer:** Claude (claude-sonnet-4-6)
**Date:** 2026-06-05
**Commit reviewed:** `2b62228f`
**Verdict:** `accept-with-boundary`

---

## Summary

Goal3447 adds a generic, device-resident relation-column stream for prepared OptiX shape-pair relation flags. The three-way count invariant (host active count == scalar device active count == resident relation-column row count) is cleanly proven over 4 pod iterations. The native implementation is app-agnostic, the typed-stream schema is generic and non-authorizing, fail-closed capacity behavior is correct, and all claim-boundary flags are explicitly false in the artifact. The goal is accepted as an internal runtime primitive with the boundaries enforced below.

---

## Review Question Findings

### Q1 — Native app-agnosticism

The `run_prepared_shape_pair_relation_active_device_columns_optix` function operates exclusively on `ShapePairRelationFlags`, `GpuPolygonRef`, generic vertex arrays, and output buffers. The kernel `shape_pair_relation_active_relation_device_columns_kernel` uses only `ShapePairRelationFlags`, `GpuPolygonRef`, and raw `unsigned long long` / `uint32_t` output columns. The struct `RtdlNativeShapePairRelationDeviceColumns` in the prelude uses no application-domain names.

The test at `tests/goal3447_shape_pair_active_relation_device_columns_test.py:105-106` greps the workloads function body and asserts that `"rayjoin"`, `"cdb"`, `"county"`, and `"soil"` are absent. The source code confirms this: no RayJoin, CDB, or overlay terminology appears inside the function body.

The app-layer `run_packed_left_active_relation_device_columns` in `rtdl_rayjoin_v2_spatial_join_app.py` adds `"app": "rayjoin_v2_spatial_join"` and `"workload": "overlay_seed"` to its result dict, and also adds explicit `"native_engine_boundary"` text explaining that the engine sees only generic flags. This app-level framing stays above the native layer and is acceptable.

**Pass.** No app leakage into the native layer.

### Q2 — Generic, reusable typed-stream schema

The schema identifiers are:

- `stream_id`: `shape_pair_relation_flags_2d_device_columns`
- `producer_primitive`: `shape_pair_relation_flags_2d`
- `schema_id`: `shape_pair_relation_flags_2d_device_columns`
- `contract_version`: `rtdl.v2_8.typed_result_stream.v1`

Field names are `left_id`, `right_id`, `requires_segment_intersection`, `requires_point_containment`. The test verifies that old polygon-specific names (`left_polygon_id`, `right_polygon_id`, `requires_lsi`, `requires_pip`) are absent.

The typed stream sets `app_specific_engine_logic_allowed: false`, `automatic_partner_selection_allowed: false`, `hidden_dispatch_allowed: false`, and `status: "internal_contract_no_native_promotion"`. The `claim_boundary` string in both the stream and the typed producer metadata explicitly enumerates all prohibited wording.

**Pass.** The schema is generic and structurally reusable. The `grouped_continuation_ready: true` flag describes schema readiness, not execution: no actual grouped continuation code exists yet. This must not be misread as a completion claim.

### Q3 — Fail-closed capacity behavior

The native overflow check is:

```cpp
if (overflow != 0u || active_count > static_cast<unsigned long long>(max_rows)) {
    columns_out->row_count = 0u;
    columns_out->overflow = 1u;
    return;
}
```

This double-checks both the kernel-set overflow flag and a direct comparison of `active_count` to `max_rows`, which prevents a race between the atomic counter increment and the overflow flag write from producing a partial result. On overflow, `row_count` is zeroed and `overflow` is set before returning. The locally-scoped `std::unique_ptr<NativeShapePairRelationDeviceColumnsOwner>` goes out of scope at the early return and frees device allocations correctly.

On the Python side, `_cupy_column` raises `RuntimeError` with a clear retry message on overflow. `raise_if_overflowed` is provided for callers that want explicit enforcement. The metadata records `overflow_policy: "fail_closed"` and `partial_result_returned: false`.

The pod evidence records `overflow: false` and `partial_result_returned: false` for all 4 runs, which confirms the path tested is non-overflow, not that the overflow path was exercised. The overflow path is not pod-tested, but the code logic is straightforward and the double-check is conservative.

**Pass.** Fail-closed is correct. Visibility is adequate.

### Q4 — Python lifetime / CuPy owner handling

`OptixShapePairRelationDeviceColumnOutput` owns an `_OptixNativeDevicePairColumnsOwner`, which wraps the native `owner_handle`. The `as_cupy_columns` method calls `cp.cuda.UnownedMemory(device_ptr, ..., self.owner)` — passing `self.owner` as the CuPy `owner` argument. CuPy will hold a reference to `self.owner`, preventing its `__del__` from running while CuPy arrays are alive. This creates correct lifetime extension for the GC path.

**Risk identified:** If the caller explicitly calls `output.close()` while CuPy arrays from `as_cupy_columns` are still live, the native device memory is freed (via the release symbol) while the CuPy arrays still hold pointers to it. CuPy's `UnownedMemory` reference to `self.owner` keeps `_OptixNativeDevicePairColumnsOwner` alive as a Python object but does not prevent `close()` from running, and `_closed=True` prevents double-free but does not un-free the already-freed memory.

The docstring on `as_cupy_columns` says "the owning native handle must stay alive while the arrays are used," and the metadata has `scope: "rtdl_primitive_handoff_only"`, `memory_manager_boundary: "not_a_general_purpose_memory_manager"`, and `lifetime: "caller_retained"`. The constraint is documented, and `true_zero_copy_authorized: False` is explicit throughout.

This pattern matches prior device-column outputs in the codebase (e.g., `OptixClosedShapeBoundaryEventDeviceColumnOutput`) and is an acceptable internal-use-only arrangement. The boundary must be re-stated in the acceptance: callers must not call `close()` on `OptixShapePairRelationDeviceColumnOutput` while CuPy column arrays are live.

**Conditional pass.** No pre-existing divergence from the pattern already in place; boundary condition must be explicitly carried forward.

### Q5 — Pod evidence proves the narrow claim

Evidence artifact `goal3447_shape_pair_active_relation_device_columns_pod_2026-06-05.json`, commit `2b62228f`, GPU NVIDIA RTX A5000 (driver 580.126.09):

| Iteration | host count | scalar device count | column row count | match |
|-----------|-----------|---------------------|-----------------|-------|
| 0         | 4543      | 4543                | 4543            | true  |
| 1         | 4543      | 4543                | 4543            | true  |
| 2         | 4543      | 4543                | 4543            | true  |
| 3         | 4543      | 4543                | 4543            | true  |

Per-iteration `column_device_summary`:
- `cupy_wrap_available: true` all 4 runs
- `cupy_flag_rows_all_active: true` all 4 runs (every emitted row has at least one dependency flag set)
- `cupy_row_count: 4543` all 4 runs

Timing observations:
- Iteration 0 scalar device time (434ms) vs iterations 1–3 (~6–17ms): expected first-iteration CUDA JIT warm-up effect; not a correctness concern.
- Iteration 3 column time (9.99ms) vs iterations 1–2 (~3.6ms): due to elevated `left_upload` (3.99ms vs ~0.56ms), a normal GPU memory-bandwidth variance. Not a correctness concern. Reported `column_speedup_vs_host` minimum of 13.8x still demonstrates substantial device-path advantage.
- `all_counts_match: true` in summary.

The narrow claim — host active count equals scalar device active count equals resident relation-column row count, with CuPy wrapping available — is proven.

The pod does not test the overflow path. The pod does not prove grouped continuation output correctness (there is none yet). The CuPy `cupy_flag_rows_all_active` check provides basic column-content sanity but does not verify that specific `(left_id, right_id)` pairs are correct against a reference.

**Pass for the stated narrow claim.**

### Q6 — What remains before full overlay relation-row or richer grouped continuation

The following gaps remain explicitly open:

1. **No exact relation witnesses.** `exact_relation_witness_rows_materialized: false` throughout. No intersection geometry, crossing points, or area fragments are produced.

2. **No grouped continuation.** `grouped_continuation_ready: true` in the stream metadata describes schema readiness, not running code. No partner or native reducer has been applied to the column output to produce richer per-left-shape summaries.

3. **No content verification of column values.** The pod confirms row counts but does not verify that each `(left_id, right_id)` pair in the output columns is the correct active pair from a reference answer. A regression test using a small known dataset would be needed before this primitive is used as the foundation for a correctness claim.

4. **Single GPU, single dataset.** The pod covers one geometry pair (15700 left / 949 right shapes) on one GPU. Capacity behavior under overflow conditions and behavior near the `max_rows` boundary are untested.

5. **Whole RayJoin overlay gap.** Full overlay (area computation, relation-row materialization, spatial predicate evaluation over active pairs) requires a partner or native stage not present here.

---

## Boundary Enforcement

The following wording remains unauthorized and must not be derived from this review acceptance:

- **v2.8 release** — not authorized
- **Public speedup wording** — not authorized (reported speedup vs. host path is internal development data, single GPU, single dataset)
- **RT-core speedup wording** — not authorized
- **RayJoin paper reproduction wording** — not authorized
- **RTDL-beats-RayJoin wording** — not authorized
- **True-zero-copy wording** — not authorized; CuPy wrapping is an internal handoff, not a zero-copy pipeline claim
- **Full overlay relation-row or overlay-area completion** — not authorized; no witnesses, no grouped continuation, no correctness verification against reference answer

What is authorized by this review:

- Goal3447 establishes a **generic RTDL runtime primitive**: a CUDA-resident compacted relation-column stream (`left_id`, `right_id`, `requires_segment_intersection`, `requires_point_containment`) produced from prepared OptiX shape-pair relation flags.
- The three-way count invariant is proven on a real GPU over 4 iterations.
- CuPy wrapping is functional as an internal development convenience, scoped to the `rtdl_primitive_handoff_only` lifetime contract.
- The primitive narrows the RayJoin overlay gap by making active relation dependencies resident on device rather than returning to host materialized rows, enabling a future partner or native continuation stage without a host round-trip.

---

## Conditions on Acceptance

1. `grouped_continuation_ready: true` in the stream metadata must not be cited as evidence that grouped continuation is complete or ready for external use.
2. Callers of `as_cupy_columns` must not call `close()` on the `OptixShapePairRelationDeviceColumnOutput` while CuPy column arrays are live. This constraint is currently documented in the docstring and scope/lifetime metadata but should be reiterated in any downstream partner-handoff documentation.
3. Content correctness of emitted `(left_id, right_id)` pairs against a reference answer remains unverified; this must be addressed before the column output is used as the foundation for a correctness claim in a downstream goal.
