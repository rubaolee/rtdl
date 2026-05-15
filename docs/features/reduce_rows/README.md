# Reduce Rows

`rt.reduce_rows(...)` is a backend-neutral standard-library helper for reducing
already-emitted RTDL rows into deterministic app summary rows.

Use it when an RTDL kernel gives you per-probe rows and the app needs a small
summary, such as:

- `any` blocker per pose
- `count` neighbors per point
- `sum` weights per group
- `min` or `max` distance across emitted rows

## Run First

```bash
PYTHONPATH=src:. python examples/rtdl_reduce_rows.py
```

## Example

```python
pose_flags = rt.reduce_rows(
    edge_hit_rows,
    group_by="pose_id",
    op="any",
    value="any_hit",
    output_field="pose_blocked",
)
```

Input rows:

```python
(
    {"pose_id": 100, "link_id": 1, "any_hit": 0},
    {"pose_id": 100, "link_id": 2, "any_hit": 1},
    {"pose_id": 200, "link_id": 1, "any_hit": 0},
)
```

Output rows:

```python
(
    {"pose_id": 100, "pose_blocked": 1},
    {"pose_id": 200, "pose_blocked": 0},
)
```

## Supported Operations

| Operation | `value` required? | Meaning |
| --- | --- | --- |
| `any` | yes | output `1` if any value in the group is truthy, otherwise `0` |
| `count` | no | count emitted rows per group |
| `sum` | yes | add values per group |
| `min` | yes | minimum value per group |
| `max` | yes | maximum value per group |

`group_by` can be a field name, a tuple/list of field names, `None`, or an
empty tuple. Groups are emitted in first-seen input order.

## Scalar Reduction Primitives

For app-name-free scalar summaries, use
`rt.run_generic_scalar_reduction(...)`. This helper standardizes the stable
Current scalar primitive names and result layouts:

| Primitive | `value_field` required? | Result layout |
| --- | --- | --- |
| `COUNT_HITS` | no | `scalar_int64_hit_count` |
| `REDUCE_INT(COUNT)` | no | `scalar_int64_count` |
| `REDUCE_INT(SUM)` | yes | `scalar_int64_sum` |
| `REDUCE_FLOAT(MIN)` | yes | `scalar_float64_min` |
| `REDUCE_FLOAT(MAX)` | yes | `scalar_float64_max` |
| `REDUCE_FLOAT(SUM)` | yes | `scalar_float64_sum` |

Example:

```python
summary = rt.run_generic_scalar_reduction(
    rows,
    summary_primitive="REDUCE_FLOAT(SUM)",
    value_field="intersection_area",
)
```

Empty-input identities are intentionally narrow: count and sum return zero,
while float min/max raise because they have no identity for empty input.

## Boundary

These helpers run in Python over rows that have already been emitted by RTDL.
They are useful because they remove repeated app boilerplate and keep ITRE as
`input -> traverse -> refine -> emit -> reduce`.

They are not native RT backend reductions and must not be described as OptiX,
Embree, Vulkan, HIPRT, or Apple RT acceleration. Native reductions should only
be added later if repeated measurements show Python-side row reduction is the
bottleneck.
