# RTDL v0.4 Code Audit — 2026-04-10

Examiner: Claude (claude-sonnet-4-6)
Repo clone: `/Users/rl2025/claude-work/rtdl_review_2026-04-10`
Date: 2026-04-10

---

## Scope

Full code review of the `fixed_radius_neighbors` workload family introduced in v0.4 (goals 193–199). Covers:

- Contract document
- DSL surface (`api.py`)
- Python reference implementation (`reference.py`)
- Runtime dispatch (`runtime.py`)
- C native oracle (`oracle_runtime.py`, `rtdl_oracle_api.cpp`, `rtdl_oracle_abi.h`)
- Reference kernel and dataset factories (`examples/reference/rtdl_fixed_radius_neighbors_reference.py`)
- Existing tests (goal198, goal199) — 10 tests
- New contract audit tests written during this session (goal200) — 32 tests

---

## v0.4 Commit History

8 commits landed goals 193–199:

| Goal | Description |
|------|-------------|
| 193 | Workload direction selection: `fixed_radius_neighbors` chosen over `point_in_volume` and `trajectory_segment_join` |
| 194 | Implementation plan: phased rollout, contract-first |
| 195 | Contract document: formal definition of the workload semantics |
| 196 | DSL surface: `rt.fixed_radius_neighbors(radius, k_max)` predicate factory |
| 197 | Reference kernel + dataset factories |
| 198 | Truth path: `fixed_radius_neighbors_cpu` + `run_cpu_python_reference` dispatch |
| 199 | CPU oracle: C native implementation + ctypes bridge |

---

## Contract Analysis

The stated contract (`src/rtdsl/contracts/fixed_radius_neighbors.md` or equivalent) defines:

- **2D Euclidean distance**, inclusive boundary (`distance <= radius`)
- **Deterministic output order**: query_id ascending → distance ascending → neighbor_id ascending
- **k_max truncation**: per-query overflow silently drops the farthest candidates; no overflow marker row emitted
- **API validation**: `radius < 0.0` or `k_max <= 0` raise `ValueError`
- **Empty inputs**: both empty query and empty search produce zero rows

All contract points are sound and unambiguous.

---

## Source File Findings

### `src/rtdsl/api.py` — DSL surface

**Status: Correct.**

```python
def fixed_radius_neighbors(*, radius: float, k_max: int) -> Predicate:
    if radius < 0.0:
        raise ValueError("fixed_radius_neighbors radius must be non-negative")
    if k_max <= 0:
        raise ValueError("fixed_radius_neighbors k_max must be positive")
    return Predicate(name="fixed_radius_neighbors", options={"radius": float(radius), "k_max": int(k_max)})
```

- `radius=0.0` is valid (allowed, for coincident-point matching). Correct.
- `k_max=0` raises. Correct.
- Options stored as `float`/`int` to prevent type drift. Correct.

### `src/rtdsl/reference.py` — Python reference implementation

**Finding F-1: Query output order not sorted by query_id (pre-audit state).**

The original `fixed_radius_neighbors_cpu` iterated query_points in input order. When query_points are passed with IDs out of numeric order, output rows do not satisfy the contract's "query_id ascending" guarantee. This was a latent bug because all authored test fixtures pass query_points in ascending id order.

**Fix applied (this session):**

```python
rows.sort(key=lambda row: row["query_id"])
return tuple(rows)
```

Added a final stable sort on `query_id` before returning. Within each query, rows were already sorted by (distance, neighbor_id) from the per-query `candidates.sort`. The new outer sort preserves that inner ordering (Python's sort is stable).

### `src/native/oracle/rtdl_oracle_api.cpp` — C native oracle

**Finding F-2: Same query_id ordering gap in C oracle (pre-audit state).**

The C implementation appended `query_rows` to `rows` in the input order of `query_values`. No final sort by `query_id` was performed. This mirrors F-1.

**Fix applied (this session):**

```cpp
std::stable_sort(
    rows.begin(), rows.end(),
    [](const RtdlFixedRadiusNeighborRow& l, const RtdlFixedRadiusNeighborRow& r) {
      return l.query_id < r.query_id;
    });
```

`std::stable_sort` preserves the per-query (distance, neighbor_id) ordering that was already established by the per-query sort.

**Observation on `kPointEps` in C oracle tie-breaking:**

The C oracle sort comparator uses `kPointEps = 1.0e-12` when comparing distances:

```cpp
if (left.distance < right.distance - kPointEps) return true;
if (right.distance < left.distance - kPointEps) return false;
return left.neighbor_id < right.neighbor_id;
```

This means two distances differing by less than 1e-12 are treated as a tie and broken by neighbor_id. The Python reference uses exact floating-point comparison (`candidates.sort(key=lambda item: (item[0], item[1]))`).

In practice, for 2D Euclidean distances computed from double-precision arithmetic this produces identical results. But theoretically, for distances that differ by less than 1e-12, the C oracle places them in neighbor_id order while Python sorts by exact distance value. This divergence is detectable only with contrived inputs and is unlikely to matter for real workloads. Noted for completeness.

### `src/rtdsl/oracle_runtime.py` — ctypes bridge

**Status: Correct.**

The `_RtdlFixedRadiusNeighborRow` struct, function signatures, and result extraction are correct. The ABI matches `rtdl_oracle_abi.h`. Memory is freed via `rtdl_oracle_free_rows`.

### `src/rtdsl/runtime.py` — Python dispatch layer

**Status: Correct.**

`_run_cpu_python_reference_from_normalized` routes `fixed_radius_neighbors` predicates correctly, reading `radius` and `k_max` from `compiled.refine_op.predicate.options`. No hardcoding.

### `examples/reference/rtdl_fixed_radius_neighbors_reference.py`

**Status: Correct. One minor observation.**

The reference kernel has `radius=0.5, k_max=3` baked in — appropriate for a canonical demonstration fixture. Three dataset builders are provided: authored (hand-crafted), fixture (Brazil county subset), natural earth (GeoJSON sample).

**Observation:** `_oracle_rows` and `_reference_rows` test helper functions written against this kernel would silently ignore any `radius`/`k_max` arguments because the kernel embeds them. The goal200 test file written in this audit used dynamic kernel construction to avoid this trap.

---

## Test Coverage — Before This Session

### goal198 (5 tests) — Truth path

| Test | What it covers |
|------|---------------|
| `test_fixed_radius_neighbors_cpu_authored_rows` | Row count, ids, distances on authored case |
| `test_cpu_python_reference_runs_fixed_radius_neighbors_kernel` | Kernel dispatch via `run_cpu_python_reference` |
| `test_fixture_case_runs_on_cpu_python_reference` | Fixture dataset produces non-empty rows |
| `test_natural_earth_loader_and_case` | GeoJSON loader + natural earth case |
| `test_baseline_runner_supports_fixed_radius_neighbors` | `run_baseline_case` API |

### goal199 (5 tests) — CPU oracle

| Test | What it covers |
|------|---------------|
| `test_lowering_supports_fixed_radius_neighbors` | `lower_to_execution_plan` returns correct fields |
| `test_run_cpu_matches_python_reference_on_authored_case` | Oracle/python parity, authored |
| `test_run_cpu_matches_python_reference_on_fixture_case` | Oracle/python parity, fixture |
| `test_baseline_runner_cpu_backend_supports_fixed_radius_neighbors` | `run_baseline_case(backend="cpu")` |
| `test_baseline_runner_cli_supports_fixed_radius_neighbors` | CLI subprocess integration |

**Gaps identified before this session:**
- No test for empty query or search inputs
- No test for queries outside radius (no-neighbor case)
- No test for exact radius boundary inclusion
- No test for zero radius
- No test for k_max overflow truncation
- No test for tie-breaking by neighbor_id
- No test for multi-query output ordering by query_id
- No API validation test (negative radius, k_max=0)
- No distance accuracy test (confirming sqrt is correct)
- No oracle/python parity on boundary and overflow scenarios

---

## Test Coverage — Added This Session (goal200, 32 tests)

### ContractEmptyInputTest (5 tests)
- Empty query → no rows
- Empty search → no rows
- Both empty → no rows
- Oracle/python parity: empty query
- Oracle/python parity: empty search

### ContractNoNeighborTest (3 tests)
- Query outside radius → no rows
- Mixed queries: only in-radius ones emit rows
- Oracle/python parity: no-neighbor

### ContractRadiusBoundaryTest (3 tests)
- Point at exactly `radius` distance → included
- Point just outside `radius` → excluded
- Oracle/python parity: boundary

### ContractZeroRadiusTest (3 tests)
- radius=0.0 matches coincident point only
- radius=0.0 with no coincident → no rows
- Oracle/python parity: zero radius

### ContractKMaxOverflowTest (4 tests)
- k_max=1: only closest returned
- Overflow: exactly k_max rows emitted
- Overflow: farther neighbors excluded
- Oracle/python parity: overflow

### ContractTieBreakingTest (3 tests)
- Equal distance: sorted by neighbor_id ascending
- Tie-breaking with k_max: lower id wins when tied
- Oracle/python parity: tie-breaking

### ContractRowOrderingTest (2 tests)
- Multi-query output sorted by query_id (exposed F-1)
- Oracle/python parity: multi-query ordering (exposed F-2)

### ContractApiValidationTest (5 tests)
- Negative radius raises `ValueError`
- k_max=0 raises `ValueError`
- k_max=-1 raises `ValueError`
- radius=0.0 does not raise
- k_max=1 does not raise

### ContractQuerySelfMatchTest (2 tests)
- Query and search at same coords → distance 0.0, neighbor emitted
- Oracle/python parity: self-match

### ContractDistanceFieldTest (2 tests)
- Emitted distance equals true Euclidean (3-4-5 triangle: distance=5.0)
- Oracle/python parity: distance accuracy

---

## Summary of Findings

| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| F-1 | Medium | `fixed_radius_neighbors_cpu` output not sorted by query_id | Fixed this session |
| F-2 | Medium | C oracle output not sorted by query_id | Fixed this session |
| F-3 | Info | C oracle uses `kPointEps` for distance tie-breaking; Python uses exact comparison | Accepted; no real-world impact |
| F-4 | Info | Test helpers naively delegating to reference kernel would silently use wrong radius/k_max | Avoided by using dynamic kernel construction in goal200 |

---

## Test Run Results

**Before fixes** (3 failures):
- `test_oracle_zero_radius_matches_python` — helper used baked-in kernel radius=0.5
- `test_oracle_distance_field_matches_python` — helper used baked-in kernel radius=0.5
- `test_multi_query_rows_ordered_by_query_id` — implementation did not sort by query_id

**After fixes** (all pass):
```
Ran 32 tests in 1.568s
OK
```

**Full suite** (goal198 + goal199 + goal200, 42 tests):
```
Ran 42 tests in ~6s
OK
```

No regressions in pre-existing tests.

---

## Verdict

The v0.4 `fixed_radius_neighbors` workload family is correctly designed and substantially complete. The two ordering gaps (F-1, F-2) were latent bugs that only manifested when query input order differed from numeric query_id order — a scenario not covered by the authored fixtures. Both are fixed. The contract, DSL surface, C oracle ABI, and runtime dispatch are all correct. Test coverage is now comprehensive across the full contract surface.
