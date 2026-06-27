# RTDL v0.7 DB — Comprehensive Attack Test Report

**Date:** 2026-04-16
**Branch:** `codex/v0_7_rt_db`
**Test file:** `tests/v07_db_comprehensive_attack_test.py`
**Total tests:** 79
**Passing:** 73
**Failing (confirmed bugs):** 6
**Confirmed-crash tests (pass by expecting exception):** 4

---

## Executive Summary

The v0.7 DB workload release introduced three new kernel families — `conjunctive_scan`, `grouped_count`, and `grouped_sum` — across CPU/oracle, Embree, OptiX, and Vulkan backends. The attack suite targeted the Python reference layer (`db_reference.py`), the oracle encoding layer (`oracle_runtime.py`), and the divergence surface between `run_cpu` (native oracle) and `run_cpu_python_reference` (pure Python).

Five distinct bugs were found. Two are silent data-corruption hazards (bugs 1 and 2) where incorrect input is accepted without error and produces wrong results. Two are missing-validation hazards (bugs 3 and 4) where invalid input is accepted and deferred until it crashes deep in the runtime. One is a native overflow hazard (bug 5) causing silent result divergence for large `row_id` values. Additionally, two crash-class bugs were confirmed: the oracle path crashes rather than returning empty results when text predicate values are absent from the table, and it crashes when row dictionaries are constructed with different key-insertion orders.

---

## Test Environment

```
Python version : 3.x (CPython)
PYTHONPATH     : src:.
Working dir    : /Users/rl2025/worktrees/rtdl_v0_4_main_publish
Run command    : PYTHONPATH=src:. python3 -m unittest tests/v07_db_comprehensive_attack_test.py -v
```

---

## Bug 1 — `_encode_db_scalar(None)` silently produces a TEXT scalar

**Severity:** Medium — incorrect encoding, native code currently ignores it but the contract is broken
**Category:** Encoding defect
**Status:** Confirmed failing (3 test failures)

### Affected code

`src/rtdsl/oracle_runtime.py`, lines 478–485:

```python
def _encode_db_scalar(value) -> _RtdlDbScalar:
    if isinstance(value, bool):
        return _RtdlDbScalar(kind=_DB_KIND_BOOL, int_value=1 if value else 0)
    if isinstance(value, int) and not isinstance(value, bool):
        return _RtdlDbScalar(kind=_DB_KIND_INT64, int_value=int(value))
    if isinstance(value, float):
        return _RtdlDbScalar(kind=_DB_KIND_FLOAT64, double_value=float(value))
    return _RtdlDbScalar(kind=_DB_KIND_TEXT, string_value=str(value).encode("utf-8"))
    #                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^
    # None reaches here → kind=4 (TEXT), string_value=b"None"
```

`src/rtdsl/oracle_runtime.py`, lines 562–576:

```python
def _encode_db_clause(clause) -> _RtdlDbClause:
    ...
    return _RtdlDbClause(
        field=str(clause.field).encode("utf-8"),
        op=op_map[str(clause.op)],
        value=_encode_db_scalar(clause.value),
        value_hi=_encode_db_scalar(clause.value_hi),   # ← None for every non-between op
    )
```

### Root cause

`PredicateClause.value_hi` is `None` for all operators except `between`. `_encode_db_scalar` has no `None` branch; `None` falls through to the final `return` and is encoded as a TEXT scalar with string content `b"None"`. This TEXT scalar is then written into the `value_hi` field of `_RtdlDbClause` and transmitted to the native oracle for every `eq`, `lt`, `le`, `gt`, and `ge` predicate.

The native oracle currently appears to ignore `value_hi` for non-`between` operators, so no wrong answers are produced today. However:
- The encoding contract is broken: native code receives a semantically meaningless TEXT scalar instead of a null/zero-initialized value.
- Any future native-side validation of `value_hi` type consistency will trigger spurious errors.
- Any future operator (e.g., `ne`, `in`) added without also adding a `None` guard in `_encode_db_scalar` will silently inherit this bug.

### Failing tests

```
test_encode_db_scalar_none_should_not_silently_encode_as_text
test_encode_db_clause_eq_predicate_value_hi_is_not_text_none
test_encode_db_clause_lt_predicate_value_hi_is_not_text_none
```

### Reproduction

```python
from rtdsl.oracle_runtime import _encode_db_scalar, _encode_db_clause, _DB_KIND_TEXT
from rtdsl.db_reference import PredicateClause

scalar = _encode_db_scalar(None)
assert scalar.kind == 4   # _DB_KIND_TEXT — WRONG; should be 0 or raise

clause = PredicateClause(field="x", op="eq", value=42)
encoded = _encode_db_clause(clause)
assert encoded.value_hi.kind == 4  # TEXT "None" — WRONG
```

### Fix

Add a `None` guard as the first branch in `_encode_db_scalar`:

```python
def _encode_db_scalar(value) -> _RtdlDbScalar:
    if value is None:
        return _RtdlDbScalar()   # zero-initialized null scalar
    if isinstance(value, bool):
        ...
```

Or, guard at the call site in `_encode_db_clause`:

```python
value_hi=_encode_db_scalar(clause.value_hi) if clause.value_hi is not None else _RtdlDbScalar(),
```

---

## Bug 2 — `normalize_predicate_bundle` silently drops a flat predicate dict

**Severity:** High — silent data-correctness bug; all table rows match when filtering was intended
**Category:** Normalization defect
**Status:** Confirmed failing (1 test failure)

### Affected code

`src/rtdsl/db_reference.py`, lines 28–37:

```python
def normalize_predicate_bundle(payload) -> PredicateBundle:
    if isinstance(payload, PredicateBundle):
        _validate_predicate_bundle(payload)
        return payload
    if isinstance(payload, dict):
        payload = payload.get("clauses", ())   # ← silent empty fallback
    clauses = tuple(_normalize_predicate_clause(item) for item in payload)
    bundle = PredicateBundle(clauses=clauses)
    _validate_predicate_bundle(bundle)
    return bundle
```

### Root cause

The public API accepts a dict as a predicate bundle via `{"clauses": [...]}`. When a caller accidentally passes a raw single-predicate dict — `{"field": "region", "op": "eq", "value": "east"}` — the code does `payload.get("clauses", ())`, which returns `()` because the dict has no `"clauses"` key. The result is an empty `PredicateBundle` with no clauses. An empty bundle matches all rows (vacuous truth in `all(... for clause in [])`).

This is a **silent correctness bug**: the caller believes they have applied a filter; they have not. Every row in the table is returned.

### Failing test

```
test_normalize_predicate_bundle_flat_dict_silently_returns_empty_bundle
```

### Reproduction

```python
from rtdsl.db_reference import normalize_predicate_bundle

# User intent: filter where region == "east"
bundle = normalize_predicate_bundle({"field": "region", "op": "eq", "value": "east"})
print(bundle.clauses)   # Output: ()  ← EMPTY — matches all rows
```

### Fix

Add a structural check before treating a dict as a `{"clauses": [...]}` wrapper:

```python
if isinstance(payload, dict):
    if "clauses" not in payload:
        raise ValueError(
            "predicate bundle dict must have a 'clauses' key; "
            "to pass a single predicate, wrap it: {'clauses': [predicate]}"
        )
    payload = payload["clauses"]
```

---

## Bug 3 — `normalize_grouped_query` defers empty `group_keys` validation

**Severity:** Medium — invalid input accepted silently, crashes deep in the runtime
**Category:** Normalization defect
**Status:** Confirmed failing (1 test failure)

### Affected code

`src/rtdsl/db_reference.py`, lines 40–54:

```python
def normalize_grouped_query(payload) -> GroupedAggregateQuery:
    if isinstance(payload, GroupedAggregateQuery):
        return payload   # ← no validation at all on passthrough
    if not isinstance(payload, dict):
        raise ValueError("grouped query input must be a mapping or GroupedAggregateQuery")
    predicates = tuple(...)
    group_keys = tuple(str(value) for value in payload.get("group_keys", ()))
    value_field = payload.get("value_field")
    if value_field is not None:
        value_field = str(value_field)
    return GroupedAggregateQuery(         # ← no validation; group_keys can be ()
        predicates=predicates,
        group_keys=group_keys,
        value_field=value_field,
    )
```

### Root cause

Two sub-issues:

1. When `payload` is an already-built `GroupedAggregateQuery`, it is returned immediately without any validation. An invalid object (e.g., `group_keys=()`) passes through unchecked.
2. When `payload` is a dict, `group_keys` is extracted and a `GroupedAggregateQuery` is constructed with no subsequent validation. An empty `group_keys` tuple produces a valid-looking object that will crash at `grouped_count_cpu` or `grouped_sum_cpu` with `ValueError("grouped_count requires at least one group key")` — far removed from the normalization call site.

Early-validation principle: user input should be rejected as early as possible, at the boundary where it enters the system.

### Failing test

```
test_normalize_grouped_query_empty_group_keys_should_raise_but_does_not
```

### Reproduction

```python
from rtdsl.db_reference import normalize_grouped_query

q = normalize_grouped_query({"predicates": [], "group_keys": []})
print(q.group_keys)   # Output: ()  ← no error yet

# Later, at runtime:
from rtdsl.db_reference import grouped_count_cpu
grouped_count_cpu(table, q)   # ValueError here, not at normalize time
```

### Fix

Add validation after constructing the query:

```python
def normalize_grouped_query(payload) -> GroupedAggregateQuery:
    if isinstance(payload, GroupedAggregateQuery):
        _validate_grouped_query(payload)   # add this call
        return payload
    ...
    query = GroupedAggregateQuery(predicates=predicates, group_keys=group_keys, value_field=value_field)
    _validate_grouped_query(query)
    return query

def _validate_grouped_query(query: GroupedAggregateQuery) -> None:
    if not query.group_keys:
        raise ValueError("grouped query requires at least one group key")
```

---

## Bug 4 — Oracle path crashes (`KeyError`) when grouped-operation text predicate value is absent from table

**Severity:** High — unhandled exception instead of correct empty result
**Category:** Oracle encoding crash
**Status:** Confirmed crash (2 tests pass by expecting `KeyError`)

### Affected code

`src/rtdsl/oracle_runtime.py`, lines 517–553 (`_encode_db_text_fields`):

```python
for field in sorted(encode_fields):
    unique_values = sorted({row[field] for row in table_rows})
    encode_map = {value: index + 1 for index, value in enumerate(unique_values)}
    ...

for clause in clauses:
    field = str(clause.field)
    if field in field_maps:
        encode_map = field_maps[field]
        value = encode_map[clause.value]          # ← KeyError if clause.value not in table
        value_hi = encode_map[clause.value_hi] ...
```

### Root cause

`_encode_db_text_fields` is called by both `_run_grouped_count_oracle` and `_run_grouped_sum_oracle` to encode string-typed fields as dense integers before passing to native code. The `encode_map` is built exclusively from values that appear in the table. If a predicate clause references a text value that is not present in any table row, `encode_map[clause.value]` raises `KeyError`.

The Python reference (`grouped_count_cpu`, `grouped_sum_cpu`) correctly handles this: the predicate simply matches no rows, and an empty result is returned. The oracle path crashes instead.

This is a divergence between the two execution paths and will surprise users running `run_cpu` after validating with `run_cpu_python_reference`.

### Confirming tests

```
test_encode_db_text_fields_eq_value_not_in_table_raises_key_error        (unit)
test_encode_db_text_fields_between_value_hi_not_in_table_raises_key_error (unit)
test_encode_db_text_fields_between_value_lo_not_in_table_raises_key_error (unit)
test_grouped_count_text_predicate_value_not_in_table_oracle_crashes_python_returns_empty
test_grouped_sum_text_predicate_value_not_in_table_oracle_crashes_python_returns_empty
```

### Reproduction

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def count_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])

table = ({"row_id": 1, "region": "east"}, {"row_id": 2, "region": "west"})

# Python reference: correct empty result
rt.run_cpu_python_reference(count_kernel, query={"predicates": [("region", "eq", "south")], "group_keys": ["region"]}, table=table)
# → ()

# Oracle: crash
rt.run_cpu(count_kernel, query={"predicates": [("region", "eq", "south")], "group_keys": ["region"]}, table=table)
# → KeyError: 'south'
```

### Fix

Guard the predicate value lookup in `_encode_db_text_fields`:

```python
if clause.value in encode_map:
    value = encode_map[clause.value]
else:
    # Predicate value not in table → can never match any row.
    # Mark this clause as unmatchable (use a sentinel code of 0,
    # which is outside the 1-based encode_map range).
    value = 0
value_hi = encode_map.get(clause.value_hi, 0) if clause.value_hi is not None else None
```

Alternatively, detect the no-match condition before calling into native and return early with `()`.

---

## Bug 5 — `row_id > 2^32 − 1` silently truncates/saturates in `_RtdlDbRowIdRow` (`c_uint32`)

**Severity:** Medium — silent result divergence; no error, wrong `row_id` returned
**Category:** Native overflow / type width mismatch
**Status:** Confirmed failing (1 test failure)

### Affected code

`src/rtdsl/oracle_runtime.py`, lines 269–272:

```python
class _RtdlDbRowIdRow(ctypes.Structure):
    _fields_ = [
        ("row_id", ctypes.c_uint32),   # ← 32-bit; max value 4,294,967,295
    ]
```

`src/rtdsl/oracle_runtime.py`, line 368:

```python
return tuple({"row_id": int(rows_ptr[index].row_id)} for index in range(row_count_value))
```

### Root cause

`row_id` values in the denorm table are encoded as 64-bit integers (`_RtdlDbScalar` with `kind=INT64`). However, the output struct `_RtdlDbRowIdRow` stores the result as a 32-bit unsigned integer. When the native oracle writes a `row_id > 4,294,967,295` (or `row_id = 2^32`) into this field, the value is silently truncated or saturated. The Python reference path uses `int(row["row_id"])` directly without any bit-width constraint, so it preserves the full value.

Confirmed behavior: `row_id = 2^32 = 4,294,967,296` → oracle returns `4,294,967,295` (UINT32_MAX saturation in native code), Python reference returns `4,294,967,296`. No error is raised by either path.

### Failing test

```
test_large_row_id_uint32_overflow_diverges
```

### Reproduction

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def scan():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])

table = ({"row_id": 2**32, "value": 42},)

py = rt.run_cpu_python_reference(scan, predicates=(("value", "eq", 42),), table=table)
oc = rt.run_cpu(scan, predicates=(("value", "eq", 42),), table=table)

print(py)   # ({'row_id': 4294967296},)
print(oc)   # ({'row_id': 4294967295},)  ← WRONG
```

### Fix — two options

**Option A (preferred): widen the native struct to 64-bit.**

In the C source (`src/native/oracle/rtdl_oracle_api.cpp`), change the result row type to use `int64_t` for `row_id`, and update the ctypes struct:

```python
class _RtdlDbRowIdRow(ctypes.Structure):
    _fields_ = [
        ("row_id", ctypes.c_int64),   # widen to 64-bit
    ]
```

**Option B: add validation in `normalize_denorm_table` and `_encode_db_table`.**

Reject `row_id` values that cannot round-trip through `uint32`:

```python
if not (0 <= int(row["row_id"]) <= 0xFFFFFFFF):
    raise ValueError(f"row_id {row['row_id']} exceeds uint32 range [0, 4294967295]")
```

---

## Additional Confirmed Crashes (tests pass by expecting exception)

These are not counted as "failing tests" because the tests are written to assert the crash occurs. They are documented here as behavioral defects that should be fixed.

### Crash A — `_encode_db_table` rejects rows with different key-insertion orders

**File:** `src/rtdsl/oracle_runtime.py:505`

```python
for index, row in enumerate(table_rows):
    if tuple(str(name) for name in row.keys()) != field_names:
        raise ValueError(f"denorm table row {index} does not match the first-row schema")
```

This check compares key order, not just key presence. Two rows `{"row_id": 1, "x": 10}` and `{"x": 20, "row_id": 2}` have the same keys but different insertion orders, causing the oracle to raise `ValueError`. The Python reference path uses dict key lookup and is completely order-independent. The fix is to normalize each row to canonical field order before comparison rather than rejecting it.

### Crash B — `normalize_denorm_table` accepts non-numeric `row_id` strings

**File:** `src/rtdsl/db_reference.py:57-68`

`normalize_denorm_table` only checks that a `row_id` key is present; it does not validate its type. A `row_id` of `"abc"` passes normalization. `conjunctive_scan_cpu` then calls `int(row["row_id"])`, which raises `ValueError: invalid literal for int() with base 10: 'abc'`. The fix is to validate `row_id` is integer-typed (or at least numeric) during normalization.

---

## Test Coverage Summary

The 79 tests in `tests/v07_db_comprehensive_attack_test.py` are organized into six classes:

| Class | Tests | Area |
|---|---|---|
| `V07DbReferencePythonAttackTest` | 16 | Pure Python `db_reference.py` functions |
| `V07DbNormalizeDefectTest` | 11 | Normalization boundary and silent defects |
| `V07DbEncodingDefectTest` | 11 | White-box oracle encoding internals |
| `V07DbOraclePythonDivergenceTest` | 19 | Oracle vs Python reference divergence |
| `V07DbApiContractTest` | 12 | Kernel compilation and `run_cpu` API contracts |
| `V07DbCorrectnessInvariantTest` | 10 | Mathematical invariants (monotonicity, partition, totals) |

---

## Bug Priority Summary

| # | Bug | Severity | Fix effort |
|---|---|---|---|
| 2 | `normalize_predicate_bundle` flat dict → silent match-all | High | Small (add key check) |
| 4 | `grouped_count`/`grouped_sum` oracle KeyError for absent text predicate | High | Small (guard encode_map lookup) |
| 3 | `normalize_grouped_query` empty `group_keys` not validated | Medium | Small (add validation helper) |
| 1 | `_encode_db_scalar(None)` → TEXT "None" encoding | Medium | Trivial (add None branch) |
| 5 | `row_id` uint32 overflow in oracle result struct | Medium | Medium (widen native struct or add validation) |
| A | Row key-insertion order crash in oracle | Low | Small (normalize key order) |
| B | Non-numeric `row_id` accepted in normalization | Low | Small (add type check) |
