# Goal3402 - Independent Review: Goal3401 Capacity Metadata Fix

Date: 2026-06-04
Reviewer: Claude (claude-sonnet-4-6), independent read-only pass
Verdict: **accept-with-boundary**

---

## Findings

### Finding 1 — Capacity assignment is correct for successful streams

The native bridge `rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_2d`
(`src/native/optix/rtdl_optix_workloads.cpp`, ~line 8183) initialises the struct with
`capacity = max_rows` and then takes one of three terminal paths:

| Path | `capacity` assignment | Line |
| --- | --- | --- |
| `exact_count == 0` (empty success) | `columns_out->capacity = 0u;` | ~8204 |
| `exact_count > max_rows` (overflow) | *(no assignment — retains initial `max_rows`)* | ~8212 |
| `exact_count <= max_rows` (success) | `columns_out->capacity = static_cast<uint64_t>(exact_count);` | ~8233 |

Both success branches override the initial `max_rows` sentinel with the actual number of
exact host-refined rows. The overflow path deliberately does not reset capacity, so the
caller's bounded value is preserved. This is the intended semantic.

### Finding 2 — Overflow path fails closed correctly

The overflow branch sets `overflow = 1u` and `row_count = 0u`, returns early without
uploading any column data, and leaves `capacity = max_rows` (set at ~line 8184). The
CuPy wrapper independently guards against exposing overflowed columns with the error
`cannot wrap an overflowed device pair-column stream`. Both layers agree: overflow is
fail-closed.

### Finding 3 — Artifacts confirm the fix on all three probes

All three JSON artifacts are stamped to commit `3b09c58a` (the fix commit).

| Probe | exact_rows | capacity | overflow | Old misleading value |
| --- | ---: | ---: | --- | --- |
| 4096-chain slice (goal3394) | 11316 | 11316 | false | 15409152 (point×shape) |
| Full `br_county.cdb` (goal3398) | 47262 | 47262 | false | 259756500 (point×shape) |
| Forced `max_rows=100` (goal3400) | 11316 | 100 | true | n/a |

Both successful probes have `v2_8_typed_producer_metadata.capacity == exact_relation_row_count`
and `typed_result_stream.page_capacity == exact_relation_row_count`. The point×shape
worst-case values are absent from all current artifacts.

The test suite (`tests/goal3401_exact_device_columns_capacity_metadata_fix_test.py`)
explicitly validates:
- `producer["capacity"] == producer["row_count"] == producer["exact_relation_row_count"]`
- `assertNotEqual(producer["capacity"], payload["point_count"] * payload["shape_count"])`
- `assertNotEqual(producer["capacity"], 259756500)` (old full-cdb sentinel)
- Overflow: `payload["capacity"] == 100 == payload["max_rows"]` with `row_count == 0`
- Native source contains both assignment forms
- All `claim_boundary` values in all three artifacts are `false`

### Finding 4 — No forbidden wording found

Every `claim_boundary` field across all three JSON artifacts and the report is `false`:
`release_authorized`, `public_speedup_claim_authorized`, `rayjoin_paper_reproduction_claim_authorized`,
`rt_core_speedup_claim_authorized`, `rtdl_beats_rayjoin_claim_authorized`,
`true_zero_copy_claim_authorized`, `native_default_route_authorized`. The typed-stream
contract also carries `hidden_dispatch_allowed: false` and `app_specific_engine_logic_allowed: false`.

The goal3401 report explicitly lists what is not implemented:
> "It does not implement chunked overflow recovery, a device-only exact predicate, true
> zero-copy, hidden dispatch, public speedup claims, RT-core speedup claims, RayJoin paper
> reproduction claims, or release authorization."

No release, speedup, RayJoin-reproduction, RT-core speedup, true-zero-copy, hidden
dispatch, or app-specific-engine language appears in any artifact.

---

## Evidence Chain

| Artifact | Commit | Role |
| --- | --- | --- |
| `goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json` | 3b09c58a | 4096-slice success probe |
| `goal3398_full_br_county_exact_device_columns_2026-06-04.json` | 3b09c58a | Full-dataset success probe |
| `goal3400_exact_device_columns_overflow_probe_2026-06-04.json` | 3b09c58a | Forced-overflow probe |
| `goal3394_optix_exact_membership_device_columns_bridge_2026-06-04.md` | — | Bridge boundary document |
| `goal3398_full_br_county_exact_stream_and_grouped_count_2026-06-04.md` | — | Scale evidence |
| `goal3400_exact_device_columns_overflow_probe_2026-06-04.md` | — | Overflow boundary document |
| `goal3401_exact_device_columns_capacity_metadata_fix_2026-06-04.md` | 3b09c58a | Goal self-report |
| `tests/goal3401_exact_device_columns_capacity_metadata_fix_test.py` | — | Automated validation |
| `src/native/optix/rtdl_optix_workloads.cpp` (~lines 8183–8239) | — | Native implementation |

Pod: NVIDIA RTX A5000, driver 580.126.09.

---

## Release Boundary

Goal3401 is a metadata accuracy fix only. It does not alter the underlying host-refined
exact-membership algorithm, allocation strategy, device-to-host transfer behavior,
memory management contract, or any observable numerical result. The bridge remains
host-refined (`host_refined_exact_rows_inside_native_bridge: true`,
`device_only_exact_predicate_produced: false`).

This review does not authorize release, public speedup wording, RayJoin paper reproduction,
RT-core speedup, true-zero-copy, hidden dispatch, or app-specific native-engine behavior.
