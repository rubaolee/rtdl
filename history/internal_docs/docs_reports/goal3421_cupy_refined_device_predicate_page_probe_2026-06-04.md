# Goal3421 CuPy Refined Device-Predicate Page Probe

Status: implemented with pod evidence on NVIDIA RTX A5000.

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

## Pod Result

The first pod run with a strict `1e-12` tolerance removed all Goal3420 false
positives, but it also dropped 217 host-exact boundary/topology pairs under the
GEOS `covers` oracle. After adding explicit `point_eps`, the sweep still did not
produce an exact match:

| point_eps | host exact | RT candidates | CuPy refined | dropped | pair match | group match | mismatched groups |
| ---: | ---: | ---: | ---: | ---: | --- | --- | ---: |
| 1e-12 | 47,262 | 47,570 | 47,045 | 525 | false | false | 97 |
| 1e-10 | 47,262 | 47,570 | 47,045 | 525 | false | false | 97 |
| 1e-9 | 47,262 | 47,570 | 47,045 | 525 | false | false | 97 |
| 1e-8 | 47,262 | 47,570 | 47,045 | 525 | false | false | 97 |
| 1e-7 | 47,262 | 47,570 | 47,045 | 525 | false | false | 97 |
| 1e-6 | 47,262 | 47,570 | 47,052 | 518 | false | false | 102 |

This is a design result, not just a tuning miss. A simple point-in-ring device
predicate is not enough to reproduce the host GEOS closed-boundary/topology
oracle on this CDB. The v2.8 exact stream needs a topology-aware closed-shape
contract or a native/partner refinement stage that explicitly models the same
boundary semantics as the oracle.

## Boundary

- Host exact rows are used only as a correctness oracle in the probe.
- The refined output is produced by CuPy, not by a new native exact predicate.
- Native default-route, RT-core speedup, true zero-copy, release, and paper
  reproduction claims remain blocked.
- The helper proves that naive device point-in-ring refinement is insufficient
  for the current host oracle; it is not a candidate for promotion as-is.
