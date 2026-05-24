# Goal2572 Primitive Catalog And Promotion Rules

Date: 2026-05-23

## Purpose

Goal2572 turns the post-benchmark-app primitive discussion into a concrete
catalog and promotion rule. The immediate problem is that RTDL currently has
several primitive-like surfaces:

- stable generic execution tokens;
- stable scalar reductions;
- experimental collection;
- grouped-reduction substrate operations;
- app adapters and partner operations;
- benchmark-specific rejected candidates.

Putting them into one flat list makes the system look unorganized. The new
catalog makes the layering explicit.

## Added Artifact

Added:

- `docs/rtdl_primitive_catalog.md`

The catalog defines:

- what an RTDL primitive means;
- the difference between primitive, app code, app adapter, shared substrate,
  experimental primitive, and rejected candidate;
- the current stable core execution primitive list;
- the current stable scalar reduction list;
- the current experimental primitive list;
- the current grouped-reduction operation list;
- a user selection guide by behavior;
- benchmark-app primitive injection history;
- promotion pipeline and scheduling/control rules.

## Current Counts

The source-of-truth constants are:

- 4 stable core execution primitives from
  `src/rtdsl/v1_5_migration_inventory.py`:
  `ANY_HIT`, `FIXED_RADIUS_COUNT_THRESHOLD_2D`, `DB_COMPACT_SUMMARY`,
  `POLYGON_PAIR_EXACT_AREA_SUMMARY`.
- 6 stable scalar reductions:
  `COUNT_HITS`, `REDUCE_FLOAT(MIN)`, `REDUCE_FLOAT(MAX)`,
  `REDUCE_FLOAT(SUM)`, `REDUCE_INT(COUNT)`, `REDUCE_INT(SUM)`.
- 1 experimental primitive:
  `COLLECT_K_BOUNDED`.
- 8 grouped-reduction substrate operations from `src/rtdsl/grouped_reduction.py`:
  `group_any`, `group_count`, `group_sum_i64`, `group_sum_f64`,
  `group_min_i64`, `group_max_i64`, `group_sum_count_i64`,
  `group_stats_i64`.

## Main Design Decision

RTDL should organize primitives by behavior and maturity:

```text
stable execution primitive
+ stable reduction
+ experimental collection
+ shared grouped/columnar substrate
+ app adapter / partner operator
+ rejected candidate
```

Users should not start from app names. They should start from behavior:

- existence -> `ANY_HIT`;
- scalar count -> `ANY_HIT` + `COUNT_HITS`;
- radius threshold -> `FIXED_RADIUS_COUNT_THRESHOLD_2D`;
- grouped aggregate -> grouped-reduction substrate;
- rows/witnesses -> collection path or candidate collection primitive;
- custom math -> app/partner operator, not native engine primitive.

## Benchmark-App Injection Rule

Benchmark apps may inject pressure, but not directly inject stable primitives.

The accepted path is:

```text
app code -> candidate primitive -> experimental primitive -> stable primitive
```

The rejected path is:

```text
app math -> native engine symbol with generic-looking name
```

Barnes-Hut Goal2549 is the control example: the native inverse-square scalar
candidate was rejected because the operation hardcoded app/workload math.

## Boundary

This is an internal architecture catalog. It does not authorize:

- public release wording;
- public speedup claims;
- external ABI stability;
- treating grouped-reduction operations as stable external primitives;
- promoting `COLLECT_K_BOUNDED`;
- treating app adapters as engine primitives;
- claiming Barnes-Hut native aggregate-frontier support.

## Validation

Added `tests/goal2572_primitive_catalog_test.py`.

The test verifies:

- every stable generic primitive constant appears in the catalog;
- every stable scalar reduction appears in the catalog;
- every experimental primitive appears in the catalog;
- every grouped-reduction operation appears in the catalog;
- benchmark-app injection history is covered;
- the rejected Barnes-Hut inverse-square candidate is named;
- promotion stages and user selection rules are present;
- public/release/speedup/ABI overclaims remain blocked.

No pod was used. This is documentation and architecture-boundary organization.
