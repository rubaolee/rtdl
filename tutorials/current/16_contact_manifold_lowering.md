# Contact Manifold Lowering

Contact manifold work is a good example of RTDL composition. RTDL does not need
to teach a physics engine. It teaches the row pipeline:

```text
shape bounds -> broadphase pair rows -> witness candidate rows
  -> bounded witness rows -> overflow validation
```

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/contact_manifold_lowering.py --mode both
```

## Relation Shape

The first relation is broadphase:

| Field | Meaning |
| --- | --- |
| `pair_id` | A candidate shape pair. |
| `moving_id` | The moving shape. |
| `static_id` | The static shape. |

The second relation is witness candidates. Each candidate belongs to a pair and
has a depth or score. The continuation keeps a bounded number of witnesses per
pair and reports whether more candidates existed than the output could hold.

Toy input:

| pair_id | moving_id | static_id |
| ---: | ---: | ---: |
| 1 | 100 | 200 |
| 2 | 101 | 201 |

Possible witness candidate rows:

| pair_id | witness_id | depth | score |
| ---: | ---: | ---: | ---: |
| 1 | 900 | 0.12 | 0.90 |
| 1 | 901 | 0.04 | 0.50 |
| 1 | 902 | 0.02 | 0.40 |
| 2 | 910 | 0.00 | 0.10 |

With a bounded output of `k = 2`, pair 1 keeps two witnesses and records
overflow because a third candidate existed:

| pair_id | kept_witness_ids | overflow |
| ---: | --- | --- |
| 1 | `[900, 901]` | `true` |
| 2 | `[910]` | `false` |

That is the RTDL lesson. The physics meaning of a contact point stays in the
application.

## V4 Mapping

The script maps the two generic shapes to V4 surfaces:

- `aabb_index_query` for broadphase pair rows,
- `closest_hit_argmin` for grouped witness selection.

The app owns what a contact point means. V4 owns the reusable row production and
bounded continuation shapes.

Next: [Graph Triangle Counting Lowering](17_graph_triangle_counting_lowering.md)
