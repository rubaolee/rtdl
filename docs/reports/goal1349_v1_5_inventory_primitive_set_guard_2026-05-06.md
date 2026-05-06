# Goal1349 v1.5 Inventory Primitive-Set Guard

Date: 2026-05-06

## Scope

This slice hardens the v1.5 generic migration inventory validator.

Changes:

- Added explicit v1.5 generic primitive sets:
  - stable generic primitives: `ANY_HIT`, `FIXED_RADIUS_COUNT_THRESHOLD_2D`, `DB_COMPACT_SUMMARY`, `POLYGON_PAIR_EXACT_AREA_SUMMARY`;
  - experimental generic primitives: `COLLECT_K_BOUNDED`;
  - stable summary primitives: `COUNT_HITS`, `REDUCE_FLOAT(MIN)`, `REDUCE_FLOAT(MAX)`, `REDUCE_FLOAT(SUM)`, `REDUCE_INT(COUNT)`, `REDUCE_INT(SUM)`.
- Made `validate_v1_5_generic_migration_inventory()` reject unknown generic primitive names.
- Made the validator split comma-separated summary primitive lists and reject unknown summary primitive names.
- Exported the primitive-set constants through `rtdsl`.
- Added tests proving unknown primitive names and pseudo-primitives such as grouped booleans are rejected.

## Validation

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1304_v1_5_generic_migration_inventory_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test
```

Result:

- Ran 14 tests.
- Result: OK.

## Boundary

This is an internal v1.5 contract guard. It does not authorize public v1.5 wording, public speedup wording, release, tagging, or any new backend implementation outside Embree and OptiX.
