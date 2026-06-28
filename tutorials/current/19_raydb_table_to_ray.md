# RayDB Table To Ray

RayDB-style work shows how ordinary table rows can become RTDL ray rows with
payloads.

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/raydb_table_to_ray.py --mode both
```

## Relation Shape

The tutorial program shows this pipeline:

```text
table rows -> ray rows + primitive rows -> hit rows with payloads
  -> dedup rows -> grouped aggregate rows
```

The useful RTDL idea is payload preservation. A table row becomes a ray row and
carries fields such as `customer_id` and `amount`. If the ray hits a primitive,
the hit row carries those payload fields into the grouping continuation.

Toy table rows:

| row_id | customer_id | amount | ray_payload |
| ---: | ---: | ---: | --- |
| 1 | 10 | 25.0 | ray from predicate A |
| 2 | 10 | 11.0 | ray from predicate B |
| 3 | 20 | 7.0 | ray from predicate A |

Hit rows preserve the payload:

| row_id | primitive_id | customer_id | amount |
| ---: | ---: | ---: | ---: |
| 1 | 100 | 10 | 25.0 |
| 3 | 100 | 20 | 7.0 |

Grouped continuation:

| customer_id | sum_amount |
| ---: | ---: |
| 10 | 25.0 |
| 20 | 7.0 |

The database query meaning stays in the app. RTDL only sees rays, primitives,
payload columns, hit rows, and grouped continuation.

## V4 Mapping

The V4 part names generic execution surfaces:

- `any_hit` for hit rows,
- `any_hit_weighted_sum` for weighted hit continuation,
- `grouped_sum` for grouped aggregation with an explicit partner.

The app owns the table schema and query semantics. V4 owns the reusable hit and
continuation shapes.

Next: [Hausdorff Composition](20_hausdorff_composition.md)
