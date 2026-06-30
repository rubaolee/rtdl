# Goal3405 - Claude Review of Goal3403: Pair Column Capacity Status Contract

Date: 2026-06-04
Reviewer: Claude (claude-sonnet-4-6), independent read-only pass
Source commit reviewed: `8bdc8a647bc4e126d43f7eeccc71d774f156a00d`

**Verdict: accept-with-boundary**

---

## Files Inspected

- `src/rtdsl/optix_runtime.py` (lines 1545-1597 `PairColumnStreamCapacityStatus`;
  lines 1600-1951 `OptixNativeDevicePairColumnOutput`)
- `scripts/goal3400_exact_device_columns_overflow_probe.py`
- `docs/reports/goal3403_pair_column_capacity_status_contract_2026-06-04.md`
- `tests/goal3403_pair_column_capacity_status_contract_test.py`
- `docs/reports/goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json`
- `docs/reports/goal3398_full_br_county_exact_device_columns_2026-06-04.json`
- `docs/reports/goal3400_exact_device_columns_overflow_probe_2026-06-04.json`

---

## Q1 - Is the capacity-status contract generic and app-agnostic?

**Yes, with a narrow metadata-enrichment coupling that is correctly bounded.**

`PairColumnStreamCapacityStatus` (line 1550) is a frozen dataclass with no
geometry-specific or application-specific fields. Its constructor accepts only
`capacity`, `row_count`, `required_capacity`, `overflowed`, and
`overflow_policy` - all plain integers and booleans. The single policy constant
`PAIR_COLUMN_STREAM_OVERFLOW_POLICY_FAIL_CLOSED = "fail_closed"` (line 1547) is
generic.

The `capacity_status` property on `OptixNativeDevicePairColumnOutput` (lines
1644-1651) has no branching on `native_symbol` and returns the same
`PairColumnStreamCapacityStatus` regardless of stream type. The app-specific
branching in `to_metadata()` (lines 1666-1690) affects metadata label
enrichment for the exact closed-shape bridge, but the capacity-status object
itself - and its invariants - is uniform across all pair-column streams.

---

## Q2 - Does it correctly distinguish successful from fail-closed overflowed streams?

**Yes. Both directions are enforced and tested.**

`__post_init__` (lines 1558-1573) enforces:

| Condition | Rule |
|---|---|
| `overflowed=True` | `row_count == 0` AND `required_capacity > capacity` |
| `overflowed=False` | `required_capacity <= capacity` |

The test `test_capacity_status_requires_fail_closed_overflow` (lines 41-58)
verifies both the happy-path and all four guard raises. The pod artifacts
confirm correct values in practice:

| Artifact | capacity | required | overflowed | row_count |
|---|---:|---:|---|---:|
| goal3394 (4096-chain slice) | 11 316 | 11 316 | false | 11 316 |
| goal3398 (full br_county) | 47 262 | 47 262 | false | 47 262 |
| goal3400 (forced max_rows=100) | 100 | 11 316 | true | 0 |

All three pass the invariants.

---

## Q3 - Does it preserve explicit caller choice rather than hidden automatic retry or dispatch?

**Yes. No automatic retry or dispatch exists anywhere in the new code.**

- `raise_if_overflowed()` (line 1579) raises with the message "retry explicitly
  with max_rows>=required_capacity". It never retries itself.
- `as_cupy_columns()` (line 1734) raises on overflow; it does not fall back.
- `retry_capacity_hint` (line 1576) is an informational integer; nothing in
  `PairColumnStreamCapacityStatus` or `OptixNativeDevicePairColumnOutput` acts
  on it.
- All metadata scopes in both successful artifacts record
  `hidden_dispatch_allowed: false`, `automatic_partner_selection_allowed: false`,
  and `native_default_route_authorized: false`.

The contract document is explicit: "The runtime reports what happened; the caller
chooses whether to retry with the required capacity."

---

## Q4 - Do the refreshed pod artifacts prove success and overflow status metadata?

**Yes. All three artifacts are pinned to commit `8bdc8a64` and carry the full
capacity-status block.**

`test_refreshed_pod_artifacts_carry_capacity_status` (lines 121-148) checks
the commit hash prefix for all three artifacts and reads `capacity_status` from
four metadata scopes on the successful artifacts and from the top-level
`capacity_status` key on the overflow artifact. The JSON structures are
consistent with those assertions.

One structural asymmetry is intentional and correctly handled: the overflow
probe (goal3400) stores `capacity_status` at the top level of the JSON (probe
schema `rtdl.goal3400.exact_device_columns_overflow_probe.v1`), while the
successful stream artifacts nest it under `metadata`. The test accounts for this
difference explicitly.

---

## Q5 - Does any wording overclaim release, speedup, RT-core use, true zero-copy, RayJoin reproduction, hidden dispatch, or app-specific native-engine behavior?

**No overclaims found.**

Every artifact carries a `claim_boundary` block with all seven boolean flags
set to `false`:

```
release_authorized: false
public_speedup_claim_authorized: false
rayjoin_paper_reproduction_claim_authorized: false
rt_core_speedup_claim_authorized: false
true_zero_copy_claim_authorized: false
native_default_route_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
```

The contract report boundary section (final paragraph) explicitly disclaims
automatic retry, chunked execution, streaming overflow recovery, device-only
exact predicates, true zero-copy, hidden dispatch, public speedup claims,
RT-core speedup claims, RayJoin reproduction claims, and release authorization.

---

## Observations

### Minor - `partial_result_returned` is structurally always `False`

In `to_metadata()` (line 1596):

```python
"partial_result_returned": bool(self.overflowed) and int(self.row_count) != 0,
```

Because `__post_init__` enforces `row_count == 0` when `overflowed=True`, this
expression evaluates to `False` for every valid instance of
`PairColumnStreamCapacityStatus`. The field is not wrong - it correctly asserts
that fail-closed overflows return no partial rows - but it is structurally
unreachable as `True` under the current contract. If the intent is to document
the policy guarantee rather than a live runtime observation, the field could
be written as `False` directly or as `not self.overflowed or self.row_count == 0`
to make the intent clear. This is a clarity note, not a correctness issue.

### Informational - `required_capacity` is sourced from `candidate_event_count`

`OptixNativeDevicePairColumnOutput.required_capacity` (line 1637) delegates to
`relation_row_count` which returns `candidate_event_count`. For the exact
host-refined bridge, `candidate_event_count` holds the post-refinement exact
row count (not a raw candidate count), so `required_capacity == exact_row_count`
in success cases. The pod artifacts confirm this identity. This derivation is
correct and consistent with Goal3401's fix to the misleading metadata.

---

## Summary

The `PairColumnStreamCapacityStatus` dataclass is a clean, generic, fail-closed
capacity contract. Its validation invariants are tight, its metadata shape is
consistent across all pod artifacts at all four metadata scopes, and it carries
no hidden retry or dispatch logic. All claim-boundary flags are correctly set to
false. The only note is a permanently-false `partial_result_returned` field that
could be documented more explicitly. No overclaiming, no silent behavioral
changes, no blocked items.

**Verdict: accept-with-boundary**

The boundary is: this contract records capacity state and fail-closed policy for
internal RTDL OptiX pair-column streams. It does not authorize retry execution,
chunked or streaming overflow recovery, public speedup or RT-core claims,
RayJoin paper reproduction, true zero-copy wording, hidden dispatch, or release.
