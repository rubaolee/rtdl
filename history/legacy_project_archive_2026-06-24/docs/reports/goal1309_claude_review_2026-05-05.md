# Goal1309 Claude Review

Date: 2026-05-05
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Scope

Reviewed the Goal1308 `REDUCE_FLOAT(SUM)` contract slice (committed) and the
Goal1309 polygon-pair generic area-summary slice (uncommitted), against the
v1.5 boundary constraints supplied in the review request.

Files reviewed:

- `src/rtdsl/float_reduction_contracts.py`
- `tests/goal1308_v1_5_polygon_float_sum_contract_test.py`
- `docs/reports/goal1308_v1_5_polygon_float_sum_contract_2026-05-05.md`
- `src/rtdsl/generic_polygon_primitives.py`
- `examples/rtdl_polygon_pair_overlap_area_rows.py`
- `tests/goal1309_v1_5_polygon_pair_generic_area_summary_test.py`
- `docs/reports/goal1309_v1_5_polygon_pair_generic_area_summary_2026-05-05.md`
- `src/rtdsl/__init__.py` (export verification)

---

## Question 1 — Goal1308: Does it correctly define `REDUCE_FLOAT(SUM)` without overclaiming implementation or public wording?

**Yes.**

### Contract definition

`v1_5_float_sum_reduction_contracts()` defines exactly two contracts:

| app | subpath | status |
|-----|---------|--------|
| `polygon_pair_overlap_area_rows` | `exact_area_sum` | `design_required` |
| `polygon_set_jaccard` | `exact_score_sum` | `blocked_by_collect_k_bounded` |

`design_required` is the correct status for the polygon-pair row — it
explicitly signals that no native float-sum backend exists and no pod
validation has occurred. There is no claim of implementation.

### Primitive and type correctness

Both contracts carry `"reduction_primitive": "REDUCE_FLOAT(SUM)"`, which is
in the bounded stable primitive set. Both use `dtype: float64` and
`abs_tol / rel_tol: 1e-9`.

### Oracle policy language

The polygon-pair contract includes:

> `"integer-grid unit-cell area still requires exact integer parity before
> float tolerance is applied"`

This is the correct hedge for the current workload. Float tolerance is not
applied prematurely; it is reserved for future non-integer or reordered
reductions.

### Jaccard correctly blocked

`polygon_set_jaccard` carries `blocked_by_collect_k_bounded` and its
`claim_boundary` reads `"diagnostic only while COLLECT_K_BOUNDED overflow
policy and OptiX slower status remain unresolved"`. This is consistent with
`COLLECT_K_BOUNDED` remaining experimental and with the Jaccard OptiX-slower
finding being unresolved.

### Public speedup wording

Both `claim_boundary` strings contain the phrase `"public speedup wording
remains blocked"`. The validator at line 82–83 of
`float_reduction_contracts.py` enforces this as a machine-readable invariant:

```python
if "public speedup" not in str(contract["claim_boundary"]):
    raise ValueError("float reduction claim boundary must block public speedup wording")
```

No overclaiming of public NVIDIA speedup wording is present.

### Validator coverage

`validate_v1_5_float_sum_reduction_contracts()` checks all required fields,
valid statuses, correct primitive name, float64 dtype, non-negative
tolerances, non-empty `value_fields`, and the "public speedup" sentinel in
`claim_boundary`. The test `goal1308_v1_5_polygon_float_sum_contract_test.py`
exercises all four contract invariants plus the inventory cross-reference.

**Goal1308 finding: clean. No issues.**

---

## Question 2 — Goal1309: Does it correctly wrap polygon-pair summary as a generic `REDUCE_FLOAT(SUM)` metadata path while preserving the exact integer oracle boundary?

**Yes.**

### Generic wrapper output

`run_generic_polygon_pair_exact_area_summary()` returns:

```text
primitive            = POLYGON_PAIR_EXACT_AREA_SUMMARY
summary_primitive    = REDUCE_FLOAT(SUM)
result_layout        = summary_float64_sums
dtype                = float64
total_intersection_area  (float64)
total_union_area         (float64)
integer_parity_values:
    total_intersection_area  (int)
    total_union_area         (int)
    overlap_pair_count       (int)
```

The float outputs are produced by explicitly casting through `int()` first
(`total_intersection_area = int(summary["total_intersection_area"])`), which
preserves exact-integer semantic before the `float()` conversion. The
`integer_parity_values` dict holds the unconverted integers and is the correct
surface for the current unit-cell oracle comparison. This design allows the
same function to serve both the future float-tolerance reduction path and the
current exact-parity gate.

### Backend scope enforcement

`_validate_backend()` at lines 11–17 of `generic_polygon_primitives.py`:

- Raises `ValueError("... frozen before v2.1")` for vulkan, hiprt, and
  apple_rt.
- Raises `ValueError("unsupported v1.5 generic polygon backend: ...")` for
  anything else.
- Accepts only embree and optix.

This is consistent with the v1.5 active scope constraint.

### Claim boundary

The claim boundary string in the wrapper explicitly states:

> "current integer-grid oracle requires exact integer parity before float
> tolerance applies; not generic polygon overlay, broad GIS, whole-app
> speedup, or public speedup wording."

### Integration in the example

Both the embree and optix summary paths in `run_case()` (lines 322–333 and
345–356 of the example) call `rt.run_generic_polygon_pair_exact_area_summary`
and subsequently set `summary = generic_area_summary["integer_parity_values"]`
before building the payload. This means `payload["summary"]` always carries
exact integer values regardless of which backend is active. The row-output
path is unchanged and does not call the generic wrapper.

The `run_phases` key `query_polygon_exact_area_reduce_float_sum_sec` is
correctly propagated to the top-level `run_phases` dict.

### Test coverage

`goal1309_v1_5_polygon_pair_generic_area_summary_test.py` covers:

1. **Metadata**: primitive, summary_primitive, result_layout, dtype, float
   value, and integer_parity_values correctness.
2. **Integration**: mock of `_positive_candidate_pairs_optix`, assertion that
   `payload["summary"] == generic["integer_parity_values"]`, and that
   `query_polygon_exact_area_reduce_float_sum_sec` is present in run_phases.
3. **Frozen backend rejection**: all three frozen backends raise the correct
   error message.

Coverage is adequate for the current slice.

### Non-blocking observation

`generic_polygon_primitives.py` hardcodes `abs_tol=1e-9` and `rel_tol=1e-9`
rather than importing `V1_5_FLOAT_REDUCTION_DEFAULT_ABS_TOL` and
`V1_5_FLOAT_REDUCTION_DEFAULT_REL_TOL` from `float_reduction_contracts.py`.
The values are identical, so there is no correctness risk. This is not a
blocker. A future cleanup pass could unify the constants.

**Goal1309 finding: clean. No issues.**

---

## Question 3 — Are there any blockers before pod validation and inventory promotion?

**No blockers.**

### Summary table

| Check | Result |
|-------|--------|
| `REDUCE_FLOAT(SUM)` in stable primitive set | Pass |
| No overclaiming of native backend implementation | Pass |
| No public NVIDIA speedup wording | Pass |
| `COLLECT_K_BOUNDED` not promoted to stable | Pass — jaccard entry remains `blocked_by_collect_k_bounded` |
| Vulkan / HIPRT / Apple RT correctly frozen | Pass — backend guard enforces at runtime |
| Integer parity preserved for current oracle | Pass — `integer_parity_values` carries exact ints |
| Float tolerance not applied to current workload | Pass — oracle uses `integer_parity_values`, not float fields |
| `polygon_pair` inventory status is `deferred_app_specific` | Pass per Goal1308 test cross-reference |
| `polygon_set_jaccard` inventory status is `diagnostic_blocked` | Pass per Goal1308 test cross-reference |
| Export surface in `__init__.py` | Pass — `ACTIVE_V1_5_GENERIC_POLYGON_BACKENDS`, `FROZEN_BEFORE_V2_1_POLYGON_BACKENDS`, `run_generic_polygon_pair_exact_area_summary` all present |

### Recommended gate command before pod handoff

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1309_v1_5_polygon_pair_generic_area_summary_test \
  tests.goal1279_v1_4_polygon_pair_primitive_contract_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test
```

This matches the gate listed in the Goal1309 report and covers contract
validation, primitive contract schema, and the new generic wrapper.

---

## Verdict

**ACCEPT** — no blocking issues. The work is ready to proceed to pod
validation. After pod validation passes, the inventory row for
`polygon_pair_overlap_area_rows / candidate_discovery_and_exact_area` may be
promoted from `deferred_app_specific` to `pod_verified_generic`.
