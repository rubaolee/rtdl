# Goal 501: v0.7 DB Comprehensive Attack Report Response

Date: 2026-04-17

External input:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/v07_db_attack_test_report.md`

Preserved local copy:

- `/Users/rl2025/rtdl_python_only/docs/reports/v07_db_attack_test_report_2026-04-17.md`

## Verdict

`ACCEPTED AND REMEDIATED`.

The external report identified five bug classes plus two additional crash-class
defects in the v0.7 DB normalization and native encoding paths. Current `main`
already contained the Goal 500 missing-field `ValueError` improvement, but the
new report exposed additional still-actionable gaps. This response fixes the
confirmed local issues and adds regression coverage.

## Bug Response Matrix

| Report item | Local response |
| --- | --- |
| Bug 1: `_encode_db_scalar(None)` encoded as text `"None"` | Fixed. `_encode_db_scalar(None)` now returns a zero-initialized scalar instead of text. |
| Bug 2: flat predicate dict silently becomes match-all | Fixed. `normalize_predicate_bundle` now requires dict wrappers to contain `clauses`; flat predicate dicts raise `ValueError`. |
| Bug 3: grouped query empty `group_keys` validation deferred | Fixed. `normalize_grouped_query` now validates `GroupedAggregateQuery` objects and dict-normalized queries immediately. |
| Bug 4: absent text predicate value crashes oracle grouped paths | Fixed. text predicate values are encoded with order-aware values so absent equality predicates match no rows and absent range bounds preserve ordering instead of raising `KeyError`. |
| Bug 5: `row_id > uint32` native overflow | Fixed by bounded contract. `normalize_denorm_table` rejects non-integer row IDs and values outside `[0, 4294967295]` before any backend can truncate them. |
| Crash A: row key insertion-order mismatch | Fixed. native row/table encoding now compares schema sets and encodes values in the first row's canonical field order, so equivalent rows with different dict insertion order are accepted. |
| Crash B: non-numeric `row_id` accepted | Fixed. `normalize_denorm_table` rejects non-integer `row_id` values at normalization. |

## Files Changed

- `/Users/rl2025/rtdl_python_only/src/rtdsl/db_reference.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/oracle_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/vulkan_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/test_v07_db_attack.py`

## Design Decisions

### Row ID Width

The report offered two options for `row_id` overflow: widen all native structs or
reject out-of-range IDs. This response chooses rejection because the current
native Oracle, Embree, OptiX, and Vulkan DB paths all use 32-bit row IDs in
their ABI or traversal metadata. A Python-side bounded contract is safer than
silently widening only one backend.

### Absent Text Predicate Values

For absent text equality predicates, the fix assigns an encoded value that no
row owns, yielding an empty result instead of a crash. For ordered predicates and
`between`, the encoding uses insertion-order bounds so native integer comparison
preserves Python string ordering for the encoded table domain.

### Key Order

Rows with the same keys but different insertion order are valid denormalized
table rows. Native table encoders now keep the first row's field order for
wire-format layout and validate later rows by key set, not insertion order.

## Validation

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.test_v07_db_attack tests.goal469_v0_7_db_attack_gap_closure_test -v
```

Result:

```text
Ran 126 tests in 0.345s
OK
```

Whitespace check:

```text
git diff --check
```

Result:

```text
OK
```

## Boundary

This was a local correctness-hardening response. It did not rerun Linux
PostgreSQL, OptiX, Vulkan, or remote large-table performance gates. Those remain
separate Linux-host validation tasks when release-gate evidence needs to be
refreshed.
