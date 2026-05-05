# Goal1310: v1.5 Jaccard `COLLECT_K_BOUNDED` Policy

Date: 2026-05-05

## Decision

`polygon_set_jaccard/chunked_candidate_scoring` remains `diagnostic_blocked` for v1.5. Goal1310 defines the missing `COLLECT_K_BOUNDED` policy, but it does not promote Jaccard to a generic native app path and does not authorize public speedup wording.

## Contract

The bounded collection primitive is experimental and diagnostic-only:

| Field | Value |
|---|---|
| Collection primitive | `COLLECT_K_BOUNDED` |
| Input primitive | `ANY_HIT` |
| Follow-on reduction | `REDUCE_FLOAT(SUM)` |
| Result layout | `bounded_candidate_pair_ids` |
| Capacity parameter | `k`, measured in candidate-pair rows |
| Ordering policy | stable by `left_id`, then `right_id`, after candidate discovery |
| Overflow policy | `no_silent_truncation` |
| Failure mode | `fail_closed_overflow` |
| Complete coverage required | yes |
| Score reduction after overflow | no |
| Public wording | blocked |

The important rule is fail-closed behavior: if candidate collection overflows or cannot prove complete coverage, the Jaccard score must not be emitted. A partial candidate set is not an approximate score for this v1.5 contract.

## Why This Blocks Promotion

Jaccard requires both candidate discovery and exact set-area scoring. Embree and OptiX can run the RT-assisted candidate-discovery step, but the score depends on complete candidate coverage before `REDUCE_FLOAT(SUM)` is meaningful. Therefore a generic v1.5 implementation must prove collection completeness or fail before scoring.

Remaining work:

| Work Item | Status |
|---|---|
| Define bounded collection overflow behavior | done in Goal1310 |
| Define Jaccard float-sum tolerance/result-shape contract | done in Goal1308; still blocked behind complete candidate coverage |
| Add native fail-closed collection implementation | not done |
| Run score reduction only after complete coverage | not done |
| Explain OptiX slower-than-Embree result | still required |
| Public speedup wording | blocked |

## Files

- `src/rtdsl/bounded_collection_contracts.py`
- `src/rtdsl/polygon_primitives.py`
- `src/rtdsl/primitive_contract_schema.py`
- `src/rtdsl/v1_5_migration_inventory.py`
- `src/rtdsl/float_reduction_contracts.py`
- `tests/goal1310_v1_5_jaccard_collect_k_bounded_contract_test.py`

## Validation

Local gate:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1280_v1_4_polygon_jaccard_diagnostic_contract_test \
  tests.goal1304_v1_5_generic_migration_inventory_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test
python3 -m py_compile src/rtdsl/bounded_collection_contracts.py src/rtdsl/polygon_primitives.py src/rtdsl/primitive_contract_schema.py src/rtdsl/v1_5_migration_inventory.py
git diff --check
```

Result: passed on 2026-05-05.

## External Review

Claude reviewed the slice in `docs/reports/goal1310_claude_review_2026-05-05.md` and returned Pass. The substantive residual risk is that fail-closed behavior is policy-declared metadata until a native implementation enforces it. One review note identified stale `future_score_primitive_status` wording; this report and `polygon_jaccard_diagnostic_contract` now make the status `blocked_by_collect_k_bounded_runtime`, because the Goal1308 float-sum contract exists but remains unreachable until complete candidate coverage is guaranteed.
