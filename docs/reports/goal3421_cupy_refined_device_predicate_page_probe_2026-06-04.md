# Goal3421 CuPy Refined Device-Predicate Page Probe

Status: implemented locally; pod evidence required.

## Purpose

Goal3420 proved that the native RT predicate column path is a conservative
device-resident superset on the public RayJoin CDB: it missed zero host-exact
pairs, but emitted 308 extra pairs. This goal adds the next narrow refinement
proof: keep RTDL's RT traversal as the generic broad-phase producer, then apply a
generic CuPy double-precision closed-shape predicate to remove false positives on
device.

## Implementation

The reusable helper is:

```python
rtdsl.refine_closed_shape_membership_candidate_columns_exact_cupy(...)
```

Inputs:

- generic candidate pair columns (`point_id`/`shape_id` or `left_id`/`right_id`)
- point records with `id`, `x`, `y`
- closed-shape records with `id` and `vertices`
- `point_eps`, the explicit boundary tolerance used by the partner predicate

Outputs:

- CuPy `point_id`, `shape_id`, and `membership` columns
- row counts and dropped-candidate metadata
- claim-boundary flags that remain false

The helper is intentionally partner-layer evidence, not the final native v2.8
page-plan producer. It is designed to give the native implementation a concrete
target: RT broad-phase pages followed by device-resident exact/refine filtering.

The first pod run with a strict `1e-12` tolerance removed all Goal3420 false
positives, but it also dropped 217 host-exact boundary pairs under the GEOS
`covers` oracle. The helper therefore exposes `point_eps` explicitly so the
device predicate can be swept and documented rather than silently guessing the
closed-boundary semantics.

## Boundary

- Host exact rows are used only as a correctness oracle in the probe.
- The refined output is produced by CuPy, not by a new native exact predicate.
- Native default-route, RT-core speedup, true zero-copy, release, and paper
  reproduction claims remain blocked.
