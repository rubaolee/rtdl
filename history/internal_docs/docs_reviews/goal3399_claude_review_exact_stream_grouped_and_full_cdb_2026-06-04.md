# Goal3399 — Claude Review: Exact Stream Grouped-Count Continuation and Full CDB (Goals 3396–3398)

**Date:** 2026-06-04
**Reviewer:** Claude (external, read-only)
**Verdict:** accept-with-boundary

---

## Scope

Review of Goals 3396, 3397, and 3398 as a coherent continuation of the Goal3394
exact device-column bridge accepted in Goal3395.

- **Goal3397** — Added `relation_row_count` / `exact_relation_row_count` aliases
  in Python metadata and probe artifacts; labelled the shared ABI field as
  `legacy_pair_column_count_field`.
- **Goal3396** — Proved the Goal3394 exact device-column stream feeds the generic
  compact grouped-count continuation on the 4096-chain `br_county` slice.
- **Goal3398** — Ran both paths on the full available `br_county.cdb` dataset
  (16545 chains, 15700 shapes).

Files inspected:

- `src/rtdsl/optix_runtime.py` (lines 1547–1875, key: 1579–1630, 1796–1860)
- `scripts/goal3394_optix_exact_membership_device_columns_live_probe.py`
- `scripts/goal3396_exact_device_columns_grouped_count_live_probe.py`
- `docs/reports/goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json`
- `docs/reports/goal3394_optix_exact_membership_device_columns_bridge_2026-06-04.md`
- `tests/goal3394_optix_exact_membership_device_columns_bridge_test.py`
- `docs/reports/goal3396_exact_device_columns_grouped_count_live_probe_2026-06-04.json`
- `docs/reports/goal3396_exact_device_columns_grouped_count_continuation_2026-06-04.md`
- `tests/goal3396_exact_device_columns_grouped_count_continuation_test.py`
- `docs/reports/goal3398_full_br_county_exact_device_columns_2026-06-04.json`
- `docs/reports/goal3398_full_br_county_exact_grouped_count_2026-06-04.json`
- `docs/reports/goal3398_full_br_county_exact_stream_and_grouped_count_2026-06-04.md`
- `tests/goal3398_full_br_county_exact_stream_and_grouped_count_test.py`

---

## Q1 — Does Goal3397 adequately resolve the naming concern?

The Goal3395 review flagged that `RtdlNativeDevicePairColumns.candidate_event_count`
is reused as the exact row count for the exact-device-column stream, and called
it a pre-graduation ABI smell.

Goal3397 added the following in `optix_runtime.py`:

```python
# line 1580 – Python property alias
@property
def relation_row_count(self) -> int:
    return int(self.candidate_event_count)

# lines 1612–1613 – metadata overlay (exact-symbol branch only)
producer_metadata["exact_relation_row_count"] = int(self.relation_row_count)
producer_metadata["legacy_pair_column_count_field"] = "candidate_event_count"
```

The approach is correct for this maturity level:

1. **The ABI field is not silently reinterpreted.** `relation_row_count` is a
   Python-layer alias; the underlying C struct field remains `candidate_event_count`
   and is explicitly labelled as a legacy slot in every exact-stream artifact.

2. **Every artifact layer carries the label.** The Goal3394 probe JSON, the
   Goal3398 full-dataset JSON, and the nested `v2_8_typed_producer_metadata`
   block all include `"legacy_pair_column_count_field": "candidate_event_count"`.
   A reader encountering any of these artifacts can determine exactly which
   low-level field backs the `exact_relation_row_count` alias.

3. **New probe code uses the alias, not the raw field.** The Goal3396 probe
   script reads `exact_columns.relation_row_count` (line 96), not
   `exact_columns.candidate_event_count`, so new consumer code is already
   guided to the clean surface.

4. **The test mechanically enforces the label.** `test_metadata_labels_exact_host_refined_bridge_not_candidate_stream`
   (goal3394 test, line 55) asserts `legacy_pair_column_count_field == "candidate_event_count"`.
   The Goal3398 test (line 37) does the same. Neither test would pass if the
   label were dropped or renamed by accident.

The one remaining gap is expected: the ABI field itself (`candidate_event_count`
in `RtdlNativeDevicePairColumns`) is not yet renamed. Goal3397 correctly declines
to rename the shared C struct field mid-bridge, because that would require
coordinating with the candidate-stream and RayJoin hit-stream consumers that also
write to it. The label makes that intent explicit.

**Finding: Goal3397 resolves the naming concern at the Python/metadata/test
level exactly as far as it can without touching a shared C ABI. The label
`legacy_pair_column_count_field` is the correct mechanism. Pass.**

---

## Q2 — Does Goal3396 prove useful composition from exact columns into grouped count?

The composition chain demonstrated is:

```
prepared.exact_device_columns(points)
  -> grouped_count_by_left_id_compact_device_columns(group_capacity=max_point_id + 1)
  -> CuPy readback (test comparison only, not part of production path)
```

Evidence from the 4096-chain probe (`rtdl_commit: 0c3fc543`):

| Measure | Value |
|---|---:|
| Exact device rows (input to grouped count) | 11316 |
| Exact relation row-count alias | 11316 |
| Host point groups | 4094 |
| Device point groups | 4094 |
| Missing groups | 0 |
| Extra groups | 0 |
| Mismatched group values | 0 |
| Grouped-count source rows | 11316 |
| Grouped-count output rows | 4094 |
| Grouped overflow | false |
| Reduction seconds | 9.326e-06 |
| Compaction seconds | 7.186e-06 |

The method `grouped_count_by_left_id_compact_device_columns` (optix_runtime.py:1796)
passes `self.left_ids_device_ptr` and `self.row_count` directly to the generic
backend symbol without any intermediate Python materialization of pair rows. The
intermediate exact pair data is never transferred to host between the two steps.
This is the key property the proof is establishing.

The group count (4094 of 4096 chains) is consistent with 2 probe points falling
inside no shape in this slice. The test asserts group count matches and zero
missing/extra/mismatched entries, which is a full correctness check, not just a
row-count comparison.

The `grouped_count_by_left_id_compact_device_columns` symbol is the same one
used by the candidate-stream grouped-count path, confirming it is genuinely
generic: it operates on the left-id column pointer regardless of whether the
upstream stream is a candidate or exact stream.

**Finding: Goal3396 proves the composition works correctly at the 4096-chain
scale. The exact columns feed the generic compact grouped-count continuation
without intermediate host materialisation of pair rows. Pass.**

---

## Q3 — Does Goal3398 close the full br_county chain-offset gap?

Evidence from the full-dataset probe (`rtdl_commit: 7ff13999`, start=0, count=16545):

### Exact device columns

| Measure | Value |
|---|---:|
| Points | 16545 |
| Shapes | 15700 |
| Exact rows | 47262 |
| Device-column rows | 47262 |
| Exact relation row-count alias | 47262 |
| Missing exact pairs | 0 |
| Extra pairs | 0 |
| Device resident | true |
| Overflow | false |
| Traversal seconds | 0.00584 |

### Grouped count continuation

| Measure | Value |
|---|---:|
| Exact device rows (input) | 47262 |
| Host point groups | 16476 |
| Device point groups | 16476 |
| Missing groups | 0 |
| Extra groups | 0 |
| Mismatched group values | 0 |
| Grouped source rows | 47262 |
| Grouped output rows | 16476 |
| Grouped overflow | false |

Both paths scale to the full dataset without overflow or correctness failures.
The 16545 → 16476 group reduction (69 points inside no shape) is plausible for
a full national polygon set. The metadata confirms
`legacy_pair_column_count_field = "candidate_event_count"` also at full scale,
so the labelling is consistent across probe sizes.

One observation worth noting: the full-dataset exact probe JSON carries
`"goal": 3394` (not 3398), because the probe reuses the `goal3394` script with
`--start 0 --count 16545`. This is honest — the artifact is a Goal3394-schema
probe run for Goal3398's scope — but a reader inspecting the artifact in
isolation might be briefly confused about which goal produced it. The report,
tests, and handoff document all correctly describe it as Goal3398 evidence.

A structural concern surfaced by reading the full-dataset numbers: the capacity
pre-allocation is `point_count × shape_count = 16545 × 15700 = 259,756,500`
elements. With two `int64` columns that is approximately **4 GB of VRAM** for a
dataset where the actual exact result occupies 47,262 × 2 × 8 = ~756 KB. The
ratio is ~5500:1. For the RTX A5000 (24 GB VRAM) this is not a blocking problem,
but it is a material pre-graduation gap: the bridge cannot be used on mid-range
GPUs (8–12 GB VRAM) without triggering either `cuMemAlloc` failure or
`grouped_overflow=true`. This was already listed in Goal3395's graduation item
#4 (overflow/chunking fallback); the full-dataset run makes the scale more
concrete.

**Finding: Goal3398 closes the chain-offset gap and demonstrates correctness
at full `br_county` scale. The traversal time (5.8 ms for 16545 × 15700)
is consistent with the host-refined path. The pre-allocation scale (~4 GB)
confirms the overflow/chunking fallback is a concrete near-term gap, not a
hypothetical. Pass for the correctness and scale coverage question.**

---

## Q4 — Are claim boundaries correct?

All seven boundaries are false at every layer across all three goal artifacts:

| Claim | goal3394 slice | goal3398 exact | goal3398 grouped |
|---|---|---|---|
| `release_authorized` | false | false | false |
| `public_speedup_claim_authorized` | false | false | false |
| `rayjoin_paper_reproduction_claim_authorized` | false | false | false |
| `rtdl_beats_rayjoin_claim_authorized` | false | false | false |
| `rt_core_speedup_claim_authorized` | false | false | false |
| `true_zero_copy_claim_authorized` | false | false | false |
| `native_default_route_authorized` | false | false | false |

Implementation boundaries in the full-dataset artifact:

```
host_refined_exact_rows_inside_native_bridge: true
native_exact_device_row_stream_produced: true
device_only_exact_predicate_produced: false
true_zero_copy_claim_authorized: false
```

The Goal3398 test asserts all claim-boundary entries are false programmatically
(lines 54–55). The Goal3396 test does the same. Both reports include explicit
plain-English prohibitions including "does not authorize release, public speedup,
RayJoin paper reproduction, RTDL-beats-RayJoin, RT-core speedup, true-zero-copy,
or native default-route claims."

**Finding: pass. All claim boundaries are blocked redundantly and mechanically
enforced by the test suite at every artifact layer.**

---

## Q5 — What remains before this bridge is a stable v2.8 primitive?

The Goal3395 review listed six graduation items. Goal3397/3396/3398 close item #6
(ABI smell at the Python/metadata layer) partially and close none of the others.
The current picture:

**1. Overflow / chunking fallback (newly concrete, high priority)**
The full-dataset run makes this tangible: ~4 GB pre-allocation for `br_county`.
Any dataset or GPU combination where `point_count × shape_count × 16 bytes >
available_VRAM` will fail silently (cuMemAlloc error) or return overflow=1 with
no partial result. A safe graduation gate requires either a chunked-stream
fallback that materialises exact output in bounded-size passes, or a runtime
VRAM guard that raises before the allocation rather than after.

**2. Device-only exact predicate (blocking for true native claim)**
Host-refined exact rows are still computed and uploaded. Until the exact
membership predicate runs on the GPU, the bridge is an upload primitive, not a
native primitive. This remains the primary claim-gate.

**3. ABI field rename (`candidate_event_count` in `RtdlNativeDevicePairColumns`)**
Goal3397 adds the Python alias and legacy label. The C struct field name is
unresolved. A future ABI pass that adds `exact_event_count` alongside
`candidate_event_count`, or a dedicated `RtdlNativeExactPairColumns` struct,
would close this permanently. This is not blocking for the bridge but is
required before the exact primitive is a first-class C API surface.

**4. GEOS/double parity test**
No probe cross-validates the exact host-refined rows against a reference
implementation on near-boundary or degenerate geometry. The full-dataset run
shows scale correctness but cannot rule out numeric discrepancies on ambiguous
cases because the host-refined path is being compared only to itself.

**5. Multi-dataset coverage**
Only `br_county` has been probed. At least one additional polygon dataset
(different density, holes, or coordinate range) is needed before claiming
the bridge generalises.

**6. Relation-witness stream**
`exact_relation_witness_rows_materialized` is false. Downstream consumers
that need the *evidence* (crossing count, winding number) per pair are
not served by the current stream. Not blocking for the grouped-count
continuation but required for richer downstream primitives.

Summary ranking:

| Gap | Blocking v2.8? |
|---|---|
| Overflow/chunking fallback | yes — concrete ~4 GB issue at full scale |
| Device-only exact predicate | yes — for native claim |
| ABI field rename | no — bridge can graduate without it |
| GEOS parity probe | no — but needed before widening adoption |
| Multi-dataset coverage | no — but needed before widening adoption |
| Relation-witness stream | no — richer primitive, separate goal |

---

## Summary

Goals 3396, 3397, and 3398 form a coherent and well-bounded extension to the
Goal3394 bridge:

- **Goal3397** resolves the `candidate_event_count` naming smell at the Python
  and metadata layer without pretending the C ABI was changed. The
  `legacy_pair_column_count_field` label is the correct mechanism and is
  mechanically enforced by the test suite.

- **Goal3396** proves that exact device columns compose directly with the generic
  compact grouped-count continuation on the 4096-chain slice, with full group
  correctness (0 missing, 0 extra, 0 mismatched). The composition avoids
  intermediate host materialisation of pair rows.

- **Goal3398** scales both paths to the full `br_county` dataset (16545 × 15700,
  47262 exact pairs, 16476 groups) with zero correctness failures. The full-dataset
  run makes the ~4 GB capacity pre-allocation concrete and confirms the
  overflow/chunking fallback is the highest-priority remaining graduation item.

All claim boundaries remain blocked across all artifacts and are mechanically
enforced by 8 passing tests on both local and pod environments. The bridge is an
honest internal contract: host-refined exact rows uploaded to native device
columns, with no release, speedup, RayJoin, RT-core, zero-copy, or default-route
claims authorised.

**Verdict: accept-with-boundary.**
