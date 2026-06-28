# Hausdorff Composition

Hausdorff distance is a composition of nearest-witness rows and max reductions.
The tutorial keeps both directions visible.

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/hausdorff_distance_recipe.py --mode both
```

## Relation Shape

The symmetric distance is built from two directed passes:

```text
A points -> B candidate rows -> nearest rows -> directed max
B points -> A candidate rows -> nearest rows -> directed max
two directed maxima -> symmetric max
```

An optional threshold decision can use the same row facts, but exact nearest
witness and threshold-only decisions are different outputs. Keep the output
contract explicit.

Example:

| A point | nearest B | distance |
| ---: | ---: | ---: |
| A0 | B0 | 0.10 |
| A1 | B2 | 0.40 |

The directed max from A to B is `0.40`.

Reverse direction:

| B point | nearest A | distance |
| ---: | ---: | ---: |
| B0 | A0 | 0.10 |
| B1 | A1 | 0.20 |
| B2 | A1 | 0.40 |

The directed max from B to A is `0.40`, so the symmetric Hausdorff distance is
`max(0.40, 0.40) = 0.40`.

If a threshold-only route answers "all points are within 0.50", that is not the
same output as the exact witness rows above. It is a cheaper decision with less
information.

## V4 Mapping

The V4 part names:

- `point_group_nearest` for nearest witness rows,
- `fixed_radius` for threshold-style decisions.

The lesson is composition. V4 provides reusable row producers and continuations;
the app decides whether it needs witness rows, a threshold answer, or both.

Next: [Partner Choice And Device Arrays](21_partner_choice_device_arrays.md)
