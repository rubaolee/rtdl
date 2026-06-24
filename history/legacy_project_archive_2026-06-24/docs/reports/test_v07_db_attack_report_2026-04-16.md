# RTDL v0.7 DB Workload Attack Test Report

**Date:** 2026-04-16
**Branch:** `codex/v0_7_rt_db`
**Commit:** `a4d0925 — Package v0.7 DB branch release gates`
**Test file:** `tests/test_v07_db_attack.py`
**Executed by:** `python3 -m unittest tests/test_v07_db_attack.py -v`
**Runtime:** 0.031 s

---

## Summary

| Metric | Value |
|---|---|
| Total tests | 105 |
| Passed | 105 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Result | **PASS** |

Initial run produced 3 failures that were traced to incorrect expected values in the test data (wrong mental arithmetic on the fixture table), not defects in the implementation. Those expectations were corrected before final execution. The corrections are documented in the findings section below.

---

## Scope

The suite attacks the three new DB workload types introduced in v0.7:

| Workload | Kernel predicate | Traverse mode |
|---|---|---|
| Conjunctive scan | `conjunctive_scan(exact=True)` | `db_scan` |
| Grouped count | `grouped_count(group_keys=(...))` | `db_group` |
| Grouped sum | `grouped_sum(group_keys=(...), value_field=...)` | `db_group` |

Six layers of the stack are exercised independently:

1. Kernel compilation / IR
2. Predicate and table input normalization
3. CPU Python reference implementation (`run_cpu_python_reference`)
4. CPU native oracle implementation (`run_cpu`)
5. SQL generation for PostgreSQL
6. `FakePostgresqlConnection` roundtrip

---

## Test Fixture

All tests operate against a single canonical six-row `SALES_TABLE` and a four-row `FLOAT_TABLE` for numeric edge cases:

```
SALES_TABLE
  row 1: region=east, ship_date=10, discount=5, quantity=12, revenue=5
  row 2: region=west, ship_date=11, discount=8, quantity=30, revenue=8
  row 3: region=east, ship_date=12, discount=6, quantity=18, revenue=6
  row 4: region=west, ship_date=13, discount=6, quantity=10, revenue=10
  row 5: region=west, ship_date=13, discount=6, quantity=8,  revenue=2
  row 6: region=north, ship_date=9, discount=3, quantity=5,  revenue=1

FLOAT_TABLE
  row 1: region=a, value=1.5,  score=0.1
  row 2: region=a, value=2.5,  score=0.9
  row 3: region=b, value=3.0,  score=0.5
  row 4: region=b, value=-1.0, score=0.2
```

---

## Test Classes and Results

### 1. TestKernelCompilation — 8 tests, all PASS

Verifies the compiled IR produced by `@rt.kernel` for all three workload kernels.

| Test | Assertion | Result |
|---|---|---|
| `test_scan_kernel_compiled_shape` | Input geometry names are `predicate_set` + `denorm_table`; mode is `db_scan`; predicate is `conjunctive_scan`; emit field is `row_id` | PASS |
| `test_count_kernel_compiled_shape` | Mode is `db_group`; predicate is `grouped_count`; group_keys is `(region,)`; emit fields are `region`, `count` | PASS |
| `test_sum_kernel_compiled_shape` | Mode is `db_group`; predicate is `grouped_sum`; group_keys is `(region,)`; value_field is `revenue`; emit fields are `region`, `sum` | PASS |
| `test_traverse_rejects_unknown_mode` | `mode="db_bogus"` raises `ValueError` | PASS |
| `test_input_rejects_unknown_role` | `role="lookup"` raises `ValueError` | PASS |
| `test_duplicate_input_name_rejected` | Two inputs both named `"x"` raises `ValueError` | PASS |
| `test_grouped_count_predicate_rejects_empty_group_keys` | `rt.grouped_count(group_keys=())` raises `ValueError` | PASS |
| `test_grouped_sum_predicate_rejects_empty_group_keys` | `rt.grouped_sum(group_keys=(), ...)` raises `ValueError` | PASS |
| `test_grouped_sum_predicate_rejects_empty_value_field` | `rt.grouped_sum(..., value_field="")` raises `ValueError` | PASS |

**Finding:** All kernel compilation contracts hold. The IR preserves mode, predicate name, options, and emit fields exactly as declared.

---

### 2. TestPredicateNormalization — 12 tests, all PASS

Exercises all input normalization paths for predicate bundles, grouped queries, and denorm tables.

| Test | Assertion | Result |
|---|---|---|
| `test_tuple3_normalizes` | 3-tuple `(field, op, value)` produces correct `PredicateClause` with `value_hi=None` | PASS |
| `test_tuple4_between_normalizes` | 4-tuple `(field, "between", lo, hi)` produces correct `value`/`value_hi` | PASS |
| `test_dict_form_normalizes` | Dict with `clauses` list accepted | PASS |
| `test_predicate_clause_passthrough` | `PredicateClause` instances pass through unchanged | PASS |
| `test_bundle_passthrough` | `PredicateBundle` instances pass through unchanged (identity) | PASS |
| `test_empty_bundle_allowed` | Zero-clause bundle is valid | PASS |
| `test_invalid_operator_rejected` | Operator `"!="` raises `ValueError: unsupported predicate operator` | PASS |
| `test_between_without_value_hi_rejected` | `between` with `value_hi=None` raises `ValueError` | PASS |
| `test_invalid_clause_type_rejected` | Integer `42` as a clause raises `ValueError` | PASS |
| `test_denorm_table_missing_row_id_rejected` | Row without `row_id` raises `ValueError` | PASS |
| `test_denorm_table_non_dict_row_rejected` | Row as a bare tuple raises `ValueError` | PASS |
| `test_grouped_query_from_dict` | Dict with `predicates`, `group_keys`, `value_field` normalizes correctly | PASS |
| `test_grouped_query_passthrough` | `GroupedAggregateQuery` passes through unchanged | PASS |
| `test_grouped_query_non_mapping_rejected` | String input raises `ValueError` | PASS |

**Finding:** All four input forms (tuple-3, tuple-4, dict, dataclass) normalize correctly. The `row_id` required-field contract is enforced.

---

### 3. TestConjunctiveScanOperators — 10 tests, all PASS

One test per operator, each pinned to concrete row-id expectations to catch inclusive/exclusive boundary bugs.

| Test | Predicate | Expected row IDs | Result |
|---|---|---|---|
| `test_eq` | `discount eq 6` | {3, 4, 5} | PASS |
| `test_lt` | `quantity lt 12` | {4, 5, 6} | PASS |
| `test_le` | `quantity le 12` | {1, 4, 5, 6} | PASS |
| `test_gt` | `ship_date gt 12` | {4, 5} | PASS |
| `test_ge` | `ship_date ge 12` | {3, 4, 5} | PASS |
| `test_between_inclusive_both_ends` | `ship_date between 10 11` | {1, 2} | PASS |
| `test_between_boundary_hi_exact` | `ship_date between 13 13` | {4, 5} | PASS |
| `test_between_empty_range` | `ship_date between 15 10` (inverted) | {} | PASS |
| `test_le_boundary_exact` | `discount le 5` | {1, 6} | PASS |
| `test_ge_boundary_exact` | `discount ge 8` | {2} | PASS |

**Finding:** All six operators are correct and inclusive/exclusive semantics match standard SQL. An inverted `between` range (lo > hi) correctly returns zero rows.

**Note on initial failures:** The first run failed `test_lt` and `test_le` because the test expected `{5, 6}` and `{1, 5, 6}` respectively, overlooking that row 4 has `quantity=10` which satisfies both. The implementation was correct; expected values were updated to `{4, 5, 6}` and `{1, 4, 5, 6}`.

---

### 4. TestConjunctiveScanEdgeCases — 12 tests, all PASS

| Test | Scenario | Result |
|---|---|---|
| `test_empty_table_returns_empty` | Zero-row table | PASS |
| `test_zero_predicates_returns_all_rows` | Empty predicate list → full table scan | PASS |
| `test_no_matches` | `discount eq 99` → no rows | PASS |
| `test_all_rows_match` | `ship_date ge 0` → all 6 rows | PASS |
| `test_single_row_table_matches` | Single-row table, predicate satisfied | PASS |
| `test_single_row_table_no_match` | Single-row table, predicate not satisfied | PASS |
| `test_multi_predicate_intersection` | 3-clause AND: `between AND eq AND lt` | PASS |
| `test_contradictory_predicates_yield_empty` | `discount gt 10 AND discount lt 5` → no rows | PASS |
| `test_emit_only_row_id_field` | Output rows contain only `row_id` key | PASS |
| `test_row_missing_predicate_field_raises` | Row missing a field named in predicate raises | PASS |
| `test_dict_wrapped_table_rows_accepted` | Table as `{"rows": (...)}` accepted | PASS |
| `test_dict_clauses_predicate_form` | Predicates as `{"clauses": [...]}` accepted | PASS |

**Finding:** Empty-table, all-match, contradictory-predicate, and missing-field cases all behave correctly. Zero predicates acts as `WHERE TRUE` (full scan).

---

### 5. TestConjunctiveScanCpuAgreement — 1 test (5 subtests), all PASS

Runs 5 predicate patterns through both `run_cpu_python_reference` and `run_cpu`, comparing sorted row-id sets:

- `(discount eq 6)`
- `(quantity lt 15)`
- `(ship_date between 11 13) AND (discount ge 6)`
- empty predicate list
- `(discount eq 99)` (no match)

**Finding:** Native oracle (`run_cpu`) and Python reference (`run_cpu_python_reference`) agree on all 5 cases.

---

### 6. TestGroupedCount — 9 tests, all PASS

| Test | Scenario | Result |
|---|---|---|
| `test_basic_group_by_region` | east=2, west=3, north=1 | PASS |
| `test_predicate_filters_before_grouping` | `ship_date ge 11` → east=1, west=3, north absent | PASS |
| `test_predicate_no_matches_returns_empty` | `discount eq 99` → empty | PASS |
| `test_all_rows_one_group` | 5-row table all region=x → one group, count=5 | PASS |
| `test_all_rows_unique_groups` | 5 distinct regions → 5 groups each count=1 | PASS |
| `test_empty_table_returns_empty` | Zero-row table | PASS |
| `test_output_sorted_by_group_key` | Group keys in ascending lexicographic order | PASS |
| `test_emit_fields_only_region_and_count` | Output rows contain exactly `region` and `count` | PASS |
| `test_count_is_always_int` | `count` values are Python `int`, never `float` | PASS |

**Note on initial failure:** First run failed `test_predicate_filters_before_grouping` because the test expected `west=2`, overlooking that row 2 (ship_date=11) also qualifies. The correct value is `west=3` (rows 2, 4, 5). Implementation was correct; expected value was updated.

---

### 7. TestGroupedCountMultiKey — 3 tests, all PASS

Tests `grouped_count` with `group_keys=("region", "discount")`.

| Test | Scenario | Result |
|---|---|---|
| `test_multikey_groups_correct` | All 5 distinct (region, discount) combinations present | PASS |
| `test_multikey_output_sorted` | Output rows sorted by (region, discount) tuple | PASS |
| `test_multikey_count_values` | `(west, 6)=2`; `(east, 5)=1` | PASS |

**Finding:** Multi-key GROUP BY works correctly. Sort order is lexicographic across all key columns.

---

### 8. TestGroupedSum — 11 tests, all PASS

| Test | Scenario | Result |
|---|---|---|
| `test_basic_sum_by_region` | east=11, west=20, north=1 | PASS |
| `test_predicate_filters_before_summing` | `ship_date ge 12` → east=6, west=12 | PASS |
| `test_no_matches_returns_empty` | `discount eq 99` → empty | PASS |
| `test_empty_table_returns_empty` | Zero-row table | PASS |
| `test_float_values_summed` | `FLOAT_TABLE` → a=4.0, b=2.0 | PASS |
| `test_negative_values_summed` | revenue={−5, 3} → sum=−2 | PASS |
| `test_sum_zero_result` | revenue={5, −5} → sum=0 | PASS |
| `test_sum_returns_int_for_integral_result` | All sums on `SALES_TABLE` are `int` | PASS |
| `test_sum_returns_float_for_fractional_result` | revenue={1.5, 0.3} → sum is `float` | PASS |
| `test_output_sorted_by_group_key` | Group keys ascending | PASS |
| `test_emit_fields_only_region_and_sum` | Output contains exactly `region` and `sum` | PASS |
| `test_missing_value_field_in_row_raises` | Row missing `revenue` raises | PASS |

**Finding:** Negative values, zero-sum, and fractional sums are handled correctly. The `int`/`float` promotion rule (integral float values are returned as `int`) is correctly applied in both positive and negative cases.

---

### 9. TestDbReferenceCpuDirect — 4 tests, all PASS

Calls `conjunctive_scan_cpu`, `grouped_count_cpu`, `grouped_sum_cpu` directly, bypassing the kernel/runtime layer.

| Test | Scenario | Result |
|---|---|---|
| `test_conjunctive_scan_all_ops` | 6 subtests, one per operator, with concrete expected row-id sets | PASS |
| `test_grouped_count_requires_group_keys` | Empty `group_keys` raises `ValueError` | PASS |
| `test_grouped_sum_requires_group_keys` | Empty `group_keys` raises `ValueError` | PASS |
| `test_grouped_sum_requires_value_field` | `value_field=None` raises `ValueError` | PASS |

**Finding:** CPU reference functions enforce their preconditions regardless of whether they are called through the kernel layer or directly.

---

### 10. TestSqlGeneration — 16 tests, all PASS

Verifies `build_postgresql_*_sql` output text for each workload.

| Test | Assertion | Result |
|---|---|---|
| `test_eq_sql` | Generates `field = %s` | PASS |
| `test_lt_sql` | Generates `field < %s` | PASS |
| `test_le_sql` | Generates `field <= %s` | PASS |
| `test_gt_sql` | Generates `field > %s` | PASS |
| `test_ge_sql` | Generates `field >= %s` | PASS |
| `test_between_sql` | Generates `field BETWEEN %s AND %s` | PASS |
| `test_empty_predicates_uses_true` | No predicates → `WHERE TRUE` | PASS |
| `test_multi_predicate_uses_and` | Two clauses joined with `AND` | PASS |
| `test_scan_sql_selects_row_id` | Contains `SELECT row_id` and `ORDER BY row_id` | PASS |
| `test_grouped_count_sql_structure` | Contains `COUNT(*) AS count`, `GROUP BY region`, `ORDER BY region` | PASS |
| `test_grouped_sum_sql_structure` | Contains `SUM(revenue) AS sum`, `GROUP BY region` | PASS |
| `test_grouped_count_sql_no_predicates_uses_true` | No predicates → `WHERE TRUE` | PASS |
| `test_grouped_count_sql_requires_group_keys` | Empty group_keys raises `ValueError` | PASS |
| `test_grouped_sum_sql_requires_group_keys` | Empty group_keys raises `ValueError` | PASS |
| `test_grouped_sum_sql_requires_value_field` | `value_field=None` raises `ValueError` | PASS |
| `test_custom_table_name_in_sql` | `table_name="my_tbl"` appears in generated SQL | PASS |

**Finding:** SQL generation is correct for all six operators. Parameterized placeholders (`%s`) are used throughout — no string interpolation of user values, no SQL injection vector.

---

### 11. TestFakePostgresqlRoundtrip — 9 tests, all PASS

Uses `FakePostgresqlConnection` to exercise the full prepare → query cycle for all three workloads without a real database.

| Test | Scenario | Result |
|---|---|---|
| `test_conjunctive_scan_roundtrip` | `discount eq 6` → rows {3,4,5} | PASS |
| `test_conjunctive_scan_no_match` | `discount eq 99` → empty | PASS |
| `test_conjunctive_scan_multi_predicate` | `between AND eq` → rows {3,4,5} | PASS |
| `test_grouped_count_roundtrip` | east=2, west=3, north=1 | PASS |
| `test_grouped_count_with_predicate` | `ship_date ge 12` → north absent | PASS |
| `test_grouped_sum_roundtrip` | east=11, west=20, north=1 | PASS |
| `test_grouped_sum_with_predicate` | `ship_date ge 12` → east=6, west=12 | PASS |
| `test_fake_connection_records_executed_sql` | `executed_sql` list contains `SELECT row_id` | PASS |
| `test_fake_connection_records_inserted_rows` | `inserted_rows` length equals table length | PASS |

**Finding:** The `FakePostgresqlConnection` correctly simulates the prepare/query lifecycle including table creation, index creation, INSERT, and SELECT phases. SQL audit log and inserted-row count are available for test inspection.

---

### 12. TestCpuAgreementAllWorkloads — 3 tests, all PASS

| Test | Workload | Predicate | Result |
|---|---|---|---|
| `test_scan_cpu_agrees_with_reference_multi_pred` | conjunctive_scan | 3-clause AND | PASS |
| `test_count_cpu_agrees_with_reference` | grouped_count | `ship_date ge 11` | PASS |
| `test_sum_cpu_agrees_with_reference` | grouped_sum | `ship_date ge 11` | PASS |

**Finding:** Native oracle backend produces identical results to the Python reference for all three v0.7 workload types.

---

### 13. TestRuntimeErrors — 3 tests, all PASS

| Test | Scenario | Result |
|---|---|---|
| `test_missing_input_raises` | Calling `run_cpu_python_reference` without `table` input raises `ValueError: missing` | PASS |
| `test_unexpected_input_raises` | Extra keyword arg `extra_garbage` raises `ValueError: unexpected` | PASS |
| `test_non_float_approx_precision_rejected` | `precision="float_exact"` kernel raises `ValueError` in `run_cpu` | PASS |

**Finding:** The runtime correctly enforces the input schema on both the missing and unexpected sides, and rejects precision values it does not support.

---

## Defects Found

**None.** All 105 tests pass against the implementation.

The 3 initial test failures were errors in the test's expected values — not defects in the library:

| Test | Wrong expected | Correct expected | Cause |
|---|---|---|---|
| `test_lt` | `{5, 6}` | `{4, 5, 6}` | Overlooked that row 4 has `quantity=10 < 12` |
| `test_le` | `{1, 5, 6}` | `{1, 4, 5, 6}` | Same: row 4 satisfies `quantity <= 12` |
| `test_predicate_filters_before_grouping` | `west=2` | `west=3` | Overlooked that row 2 (ship_date=11) satisfies `ship_date >= 11` |

Correcting these confirmed that `lt`, `le`, and predicate-filtered `grouped_count` all implement standard SQL inclusive/exclusive semantics correctly.

---

## Coverage by Feature Area

| Feature area | Tests | Status |
|---|---|---|
| Kernel IR compilation | 8 | All pass |
| Input normalization (predicate, table, grouped query) | 14 | All pass |
| `conjunctive_scan` — operator coverage | 10 | All pass |
| `conjunctive_scan` — edge cases | 12 | All pass |
| `conjunctive_scan` — cpu vs reference agreement | 5 subtests | All pass |
| `grouped_count` — single-key | 9 | All pass |
| `grouped_count` — multi-key | 3 | All pass |
| `grouped_sum` | 11 | All pass |
| CPU reference direct calls | 4 | All pass |
| SQL generation (all operators + structural) | 16 | All pass |
| FakePostgresqlConnection roundtrip | 9 | All pass |
| Cross-backend agreement (cpu vs python_reference) | 3 | All pass |
| Runtime error contract | 3 | All pass |

---

## Gaps and Recommendations for Follow-up Testing

The following areas are not covered by this suite and would strengthen the v0.7 release:

1. **Live PostgreSQL correctness gate** — `FakePostgresqlConnection` exercises the Python path; a real PostgreSQL connection is needed to confirm `BETWEEN` and type-coercion parity. Goals 423/424/429 appear to address this on Linux, but were not re-run locally.

2. **Large-table behavior** — The fixture table has 6 rows. Boundary behavior at N=0, 1, and power-of-two block sizes (1024, 65536) should be tested for the native oracle path.

3. **Multi-value-field grouped_sum** — Only `revenue` is tested as the sum field. A test with a `float` column from the start (not just `FLOAT_TABLE` subtraction) would confirm the int/float promotion path more aggressively.

4. **Native backends (Embree, OptiX, Vulkan)** — This suite only exercises `run_cpu` and `run_cpu_python_reference`. Backend-specific correctness and performance are covered by Goals 426–430 and require the Linux GPU host at 192.168.1.20.

5. **`between` with float bounds** — All `between` tests use integer bounds. Float-bound boundary arithmetic (`between 1.0 1.9999`) is not covered.

6. **Concurrent / repeated kernel compilation** — The context-stack-based kernel builder is not tested under re-entrant or repeated compilation calls.

---

*Report generated 2026-04-16. Test file: `tests/test_v07_db_attack.py`.*
