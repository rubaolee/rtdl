# External AI Review — Goal1853: Caller-Supplied Partner Column Adapter

**Reviewer:** Claude (claude-sonnet-4-6), independent of Codex  
**Date:** 2026-05-13  
**Verdict:** `accept-with-boundary`

---

## Scope

Goal1853 adds `rtdsl.segment_polygon_anyhit_rows_optix_partner_columns(...)` to
`src/rtdsl/partner_adapters.py`. This is the caller-column variant of the
Goal1850 adapter: rather than accepting Python records and building GPU columns
internally, it accepts pre-built PyTorch/CuPy GPU tensors for segment ray
columns, polygon triangle columns, and triangle AABBs. The adapter allocates
only the bounded witness output tensors, invokes the generic OptiX native
contract, and names/deduplicates app rows in Python.

Files reviewed:

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py` (export surface only, via grep)
- `tests/goal1853_segment_polygon_partner_column_adapter_test.py`
- `tests/goal1850_segment_polygon_partner_adapter_test.py`
- `docs/reports/goal1853_segment_polygon_partner_column_adapter_2026-05-13.md`
- `docs/reports/goal1853_segment_polygon_partner_column_adapter_pod_smoke.json`

---

## Review Questions

### 1. Does the column adapter preserve the app-agnostic native-engine boundary?

**Yes, cleanly.**

The native engine call site (`partner_adapters.py:239–250`) passes only:

- `polygon_triangle_columns` — generic float64/uint32 column dict,
- `polygon_triangle_aabbs` — generic float32 AABB tensor,
- `segment_ray_columns` — generic ray column dict,
- `witness_ray_ids` / `witness_primitive_ids` — output uint32 tensors.

No segment, polygon, GIS name, deduplication policy, or row-naming concept
crosses the native boundary. App-specific interpretation occurs entirely in
Python after the `write_device_any_hit_all_witnesses` call returns (lines
257–262). The metadata key `native_engine_row_contract:
"generic_ray_primitive_witness_pairs"` is present in both the implementation
and the pod artifact for both partners. The boundary is intact.

### 2. Does it genuinely move closer to true zero-copy?

**Yes. This is the key step forward over Goal1850.**

In Goal1850, `_segment_ray_columns` and `_polygon_triangle_columns` are called
inside the adapter to pack Python records into GPU tensors (partner_adapters.py
lines 144–145). That packing is eliminated in the column adapter: the caller
owns those tensors and the adapter receives them directly.

The only allocations the adapter makes are the two witness output columns (lines
236–237), which must be fresh per invocation by design.

The pod artifact confirms this for both partners:

```
direct_device_pointer_observed: true
ray_columns_true_zero_copy_authorized: true
triangle_scene_true_zero_copy_authorized: true
witness_outputs_true_zero_copy_authorized: true
true_zero_copy_authorized: true
```

This is a genuine, non-trivial advance relative to Goal1850.

### 3. Does the pod artifact support the narrow claim for both CuPy and Torch on RTX A4500?

**Yes.**

The artifact (`goal1853_segment_polygon_partner_column_adapter_pod_smoke.json`)
was captured at commit `dc825ce03d075cecb05ffc5b80b04652ff66882a` on "NVIDIA
RTX A4500, 550.127.05". Both `cupy` and `torch` entries record:

- `status: "pass"` at the top level,
- identical correct rows:
  `[{polygon_id: 11, segment_id: 101}, {polygon_id: 12, segment_id: 101}]`,
- `adapter: "segment_polygon_anyhit_rows_optix_partner_columns"`,
- `input_contract: "caller_supplied_partner_device_columns"`,
- `exact_row_semantics_authorized: true`,
- all zero-copy authorization flags true.

The commit hash matches the recent git log entry (`dc825ce0 Add caller supplied
partner column adapter`). The artifact is consistent and traceable.

One observation: the torch elapsed time (0.010 s) is ~24× faster than cupy
(0.244 s). This discrepancy is consistent with PyTorch having a warmer CUDA
context on the first run and does not indicate a correctness problem. The
cupy time is still well within acceptable range for a 2-ray / 2-triangle
smoke test; no performance claim is being made here.

### 4. Are claim boundaries correct?

**Yes, all four are correctly blocked.**

| Blocked claim | Implementation | Artifact | Report |
|---|---|---|---|
| v2.0 release authorization | `v2_0_release_authorized: False` (line 226, 268) | `false` for both partners | Explicit: "not a v2.0 release gate pass" |
| Whole-app speedup claim | `whole_app_speedup_claim_authorized: False` (line 227, 269) | `false` for both partners | Not asserted |
| Broad RT-core speedup claim | Not asserted anywhere | `rt_core_speedup_claim_authorized: false` for both partners | Not asserted |
| Package-install claim | Not present | Not present | Not asserted |

The report's "Boundary" section is explicit and correct. No overclaim is present
in any artifact.

### 5. Should follow-on v2.0 app adapters use this column-supplied shape?

**Yes, with the following guidance.**

The caller-column shape is the right foundation for v2.0 app adapters because:

- It removes the adapter's internal packing step, letting the caller control GPU
  memory lifecycle and reuse tensors across calls.
- It cleanly expresses the contract: the adapter does exactly three things —
  allocate witness output buffers, invoke the native contract, and name app rows.
- Both PyTorch and CuPy callers are supported via the `partner` parameter, and
  `_partner_module` dispatches consistently.

Two minor design notes for follow-on work (neither is a blocking concern here):

1. **Default `output_capacity`** (line 231: `ray_count * triangle_count`) is a
   conservative upper bound that assumes all rays hit all triangles. For large
   inputs this could allocate a very large witness buffer. v2.0 adapters should
   document the recommendation to pass an explicit `output_capacity` when the
   expected hit density is known, or consider a separate bounded-capacity API
   that returns the overflow flag to the caller rather than raising.

2. **`_column_length` fallback** (lines 188–196) handles three column shapes:
   `.shape[0]` for real tensors, `.values` for the test-only `_FakeColumn`,
   and bare `len()` as a last resort. The bare `len()` path could raise
   `TypeError` on some tensor types that do not implement `__len__`. This is
   unlikely to surface in practice but is worth hardening before v2.0 release.

---

## Implementation Observations

- **Export surface is correct.** `__init__.py` line 372 imports
  `segment_polygon_anyhit_rows_optix_partner_columns` from `partner_adapters`,
  and line 1249 adds it to `__all__`. Both are present and consistent.

- **Test coverage split is deliberate but reviewers should understand it.**
  `goal1853_segment_polygon_partner_column_adapter_test.py` validates static
  surface, report content, and pod artifact structure but does not mock-execute
  the adapter logic. The behavioral mock test for the column adapter lives in
  `goal1850_segment_polygon_partner_adapter_test.py:test_column_adapter_keeps_caller_supplied_partner_input_contract`.
  This is an acceptable split for a goal that extends an existing adapter, but
  follow-on goals should consider co-locating behavioral tests with the adapter
  they test.

- **`scene.close()` in `finally` block** (line 251) ensures the native scene is
  released even if `write_device_any_hit_all_witnesses` raises. This is correct.

- **Deduplication** via `sorted(set(zip(...)))` (line 261) matches the Goal1850
  implementation exactly. The deduplication is app-side, not engine-side, which
  is architecturally correct.

---

## Summary

The implementation is sound, the native-engine boundary is clean, the zero-copy
advance is genuine and confirmed by device-side pointer evidence, the pod
artifact is traceable and correct for both CuPy and Torch on RTX A4500, and all
four blocked claims are explicitly and consistently maintained across code,
artifact, and report.

**Verdict: `accept-with-boundary`**

This goal is accepted as a narrow proof that app adapters can consume
caller-supplied PyTorch/CuPy GPU columns directly while keeping app row identity
and deduplication outside the native engine. It is not a v2.0 release gate pass.
The two minor design notes above (output_capacity defaults and `_column_length`
fallback robustness) are flagged for v2.0 adapter hardening but do not block
acceptance of this goal's narrow claim.
