# Goal 501 External Review — Claude Verdict

**Date:** 2026-04-17
**Reviewer:** Claude (claude-sonnet-4-6)
**Verdict:** ACCEPT

---

## Scope

Reviewed the v0.7 DB attack report (`v07_db_attack_test_report_2026-04-17.md`), the self-response document (`goal501_v0_7_db_comprehensive_attack_report_response_2026-04-17.md`), and the diffs in `db_reference.py`, `oracle_runtime.py`, `embree_runtime.py`, `optix_runtime.py`, `vulkan_runtime.py`, and `tests/test_v07_db_attack.py`.

---

## Bug-by-Bug Verdict

| Report item | Fix present? | Fix correct? | Regression test present? |
|---|---|---|---|
| Bug 1: `_encode_db_scalar(None)` → TEXT "None" | Yes | Yes — `if value is None: return _RtdlDbScalar()` at `oracle_runtime.py:481` | Yes — `test_encode_db_scalar_none_is_null_not_text_none`, `test_encode_db_clause_eq_value_hi_is_null_not_text_none` |
| Bug 2: flat predicate dict → silent match-all | Yes | Yes — `if "clauses" not in payload: raise ValueError` at `db_reference.py:35` | Yes — `test_flat_predicate_dict_rejected_instead_of_match_all` |
| Bug 3: empty `group_keys` validation deferred | Yes | Yes — `_validate_grouped_query` called on both passthrough and dict paths (`db_reference.py:46,60`) | Yes — `test_grouped_query_empty_group_keys_rejected_at_normalization` |
| Bug 4: oracle `KeyError` for absent text predicate value | Yes | Yes — `_encode_db_text_clause_values` (`oracle_runtime.py:576`) adds predicate values into encoding domain; `eq` uses sentinel 0; range operators use bisect bounds. Same fix applied to Embree, OptiX, Vulkan backends. | Yes — `test_encode_db_text_fields_absent_eq_value_encodes_no_match_sentinel`, `test_count_text_predicate_absent_value_returns_empty_like_reference`, `test_sum_text_predicate_absent_value_returns_empty_like_reference` |
| Bug 5: `row_id > uint32` silent truncation | Yes | Yes — bounded contract via `_coerce_row_id` rejects out-of-range IDs at normalization (`db_reference.py:195`) and again in `_encode_db_table` (`oracle_runtime.py:514`). Option B (reject early) chosen over Option A (widen struct); rationale documented and sound — all backends share the 32-bit ABI. | Yes — `test_denorm_table_large_row_id_rejected_before_native_overflow`, `test_scan_rejects_large_row_id_before_native_overflow` |
| Crash A: row key-insertion order mismatch | Yes | Yes — `_encode_db_table` and `_encode_db_table_columnar` (Embree) now compare `set` of keys instead of ordered tuple, and encode values in first-row field order. | Yes — `test_encode_db_table_accepts_same_schema_different_key_order` |
| Crash B: non-numeric `row_id` accepted | Yes | Yes — `_validate_row_id` / `_coerce_row_id` rejects non-integer and bool `row_id` at normalization. | Yes — `test_denorm_table_non_numeric_row_id_rejected` |

---

## Test Run

```
PYTHONPATH=src:. python3 -m unittest tests.test_v07_db_attack -v
Ran 120 tests in 0.014s
OK
```

All 120 tests pass with no failures or errors.

---

## Design Decision Assessment

**Bug 5 / row_id width:** Choosing rejection (Option B) over widening (Option A) is defensible. The native Oracle, Embree, OptiX, and Vulkan DB paths all use 32-bit row IDs in their wire ABI; widening only the Python-side ctypes struct without coordinating the native side would create a new divergence. The bounded contract is clear and documented.

**Bug 4 / absent text predicate encoding:** Adding absent predicate values into the encoding domain (so they receive a valid code that no table row owns) is more robust than the sentinel-0 fallback alone. The bisect-based range encoding for `lt`/`le`/`gt`/`ge`/`between` correctly preserves ordering semantics for out-of-domain bounds.

---

## Limitations of This Review

This review covers Python-layer correctness only. It does not cover:
- Native oracle C++ source (not included in the diff).
- Embree, OptiX, and Vulkan native DB execution paths beyond the Python encoding layer — the key-order and text-encoding fixes are applied to the Python prepare/encode layer but native behavior under those fixes was not exercised by the test suite here.
- Linux PostgreSQL, large-table performance, or GPU gates.

Within the Python-layer scope, all seven reported defects are fixed, bounded honestly, and covered by regression tests.
