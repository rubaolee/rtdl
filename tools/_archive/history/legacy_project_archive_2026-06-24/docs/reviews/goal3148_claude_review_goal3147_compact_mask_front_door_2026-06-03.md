# Goal3148: Claude Review of Goal3147 — Compact-Mask Front Door

**Date:** 2026-06-03
**Reviewer:** Claude (claude-sonnet-4-6)
**Subject:** Goal3147 — expose `compact_mask_i64` through the v2.8 segmented typed stream partner-consumer front door
**Verdict:** `accept`

---

## Findings by Severity

### Informational (non-blocking)

**I-1 — Eager `group_ids` computation discarded by `compact_mask_i64` branch**
File: `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`, lines 538–542 and 573–578

`_reference_inputs_for_plan` builds a `group_ids` tuple unconditionally at the top of the function, but the `compact_mask_i64` branch discards it entirely and returns a fresh `{"values": ..., "mask": ...}` dict. The wasted allocation is small for typical test payloads, but it is dead work on any hot path through this function. Not a bug; the returned dict is correct.

**I-2 — Redundant `tuple()` wrapping in `_partner_input_column_mapping`**
File: `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`, lines 594–597

The `compact_mask_i64` branch assigns `mapping` from a `list` to an already-correct tuple literal, then calls `return tuple(mapping)` on it — `tuple()` of a tuple is a no-op. Harmless, but inconsistent with the style of every other branch.

Neither finding warrants a code change before acceptance. They are documented here for future cleanup.

---

## Answers to the Five Review Questions

### Q1 — Does Goal3147 correctly promote `compact_mask_i64` from the deferred map into supported operations?

**Yes.**

`compact_mask_i64` appears in `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS` (adapter.py line 39). `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_DEFERRED_OPERATIONS` is now an empty dict (adapter.py lines 41–42). The summary function exposes both facts. Tests `goal3147:22–23` and `goal3145:31–32` (which also references this operation) confirm the promotion. The pod artifact commit `a2ed0069` matches the HEAD commit for Goal3147 in git, confirming the artifact was recorded from the right revision.

### Q2 — Is the operation honestly modeled as a stable candidate-stream filter, not as a grouped reduction?

**Yes.**

The report (line 11) explicitly states: "`compact_mask_i64` is not a grouped reduction. It is a stable row-filter continuation over a typed candidate stream." The implementation respects this:

- `_reference_inputs_for_plan` returns `{"values": ..., "mask": ...}` with no `group_count` or `group_ids` — the filter semantics are not laundered through grouping.
- `_partner_input_column_mapping` omits the leading `("group_ids", ...)` entry that all grouped operations carry; it returns only `(("values", first), ("mask", second))`.
- Test fixtures use `stream_kind="candidate_stream"` and `ordering="stable_row_order"`.
- The artifact records `stable_input_order: true` at both row sizes, and `host_prefix_sum_used: true` is honestly disclosed rather than hidden.

### Q3 — Is the implementation app-agnostic and composed from existing generic helpers?

**Yes.**

The Numba path delegates to `run_numba_compact_mask_i64` (adapter.py line 719), the same generic kernel already exercised by prior goals. The non-Numba path uses `partner_mask_indices` and `partner_take_columns_by_indices` (adapter.py lines 735–739), which are the generic partner adapters. No benchmark-app names, no road-hazard-specific identifiers, and no app-specific engine logic appear anywhere in the added code. The `app_specific_engine_logic_allowed: False` invariant is enforced in both `__post_init__` (adapter.py lines 84–97) and `validate_segmented_typed_stream_adapter` (adapter.py lines 249–262).

The probe script (`goal3147_compact_mask_front_door_pod_probe.py`) builds its test data with `np.arange` and a modulo-based boolean mask — generic data with no domain coupling.

### Q4 — Is the canonical output schema (`values`, `original_indices`) correct and stable?

**Yes.**

Both paths — the reference oracle (adapter.py lines 573–578) and the Numba partner path (adapter.py lines 728–733) and the generic partner path (adapter.py lines 739–747) — return exactly `{"values": ..., "original_indices": ...}`. Metadata records `"canonical_output_schema": ("values", "original_indices")` in both the Numba branch (line 728) and the generic branch (line 745). Tests `goal3147:68` and `goal3111:651–654` verify this schema. The artifact's per-row `canonical_output_schema` field matches. No third output column is introduced; no output is silently dropped.

### Q5 — Does the RTX 4000 Ada artifact prove only correctness/availability, with all promotion and speedup boundaries intact?

**Yes.**

The artifact (`compact_mask_front_door_pod_probe_2026-06-03.json`) records:

- `all_match: true`
- Both row sizes (1 M and 4 M) show `values_match_reference: true` and `indices_match_reference: true`
- `stable_input_order: true` and `host_prefix_sum_used: true` at every row
- `canonical_output_schema: ["values", "original_indices"]` at every row
- Every claim-boundary flag false: `v2_8_release_authorized`, `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`
- Per-row: `partner_consumer_promoted: false`, `release_authorized: false`, `public_speedup_claim_authorized: false`, `rt_core_speedup_claim_authorized: false`, `true_zero_copy_claim_authorized: false`

The probe includes an explicit warmup pass (default `--warmup-rows 4096`) so that JIT compilation time is excluded from the measured rows, and the elapsed times in the artifact (0.046 s at 1 M rows, 0.175 s at 4 M rows) are plausible continuation-only timings for a host-prefix-sum-based compact operation. No performance comparison to any baseline is made; no speedup is claimed.

---

## Boundary Confirmation

This review does not authorize any of the following:

- v2.8 release
- Public speedup claims
- RT-core speedup claims
- True-zero-copy claims
- Device-resident result stream
- Hidden dispatch or automatic partner selection
- App-specific engine logic

This is an internal preview review of a front-door promotion only.

---

## Summary

Goal3147 is a clean, bounded promotion of one deferred operation into the v2.8 partner-consumer front-door surface. The semantic model (stable filter, not grouped reduction), the output schema, the helper composition, and the artifact boundary flags are all correct and consistent. Two minor code-quality observations (eager `group_ids` computation, redundant `tuple()` call) are documented above but do not block acceptance.

**Verdict: `accept`**
