# Goal4834 Contract Alignment Notes

Date: 2026-06-30

## Sources Re-Read

- Paper: `C:\Users\Lestat\Downloads\ics24 (1).pdf`
- Author source: `/workspace/RayJoin_fresh`, commit
  `02bf6220d6d20b04af77ee20364eced75cc029c9`, read via
  `git show HEAD:<file>` because the worktree contains debug edits.
- Author clarification:
  `C:\Users\Lestat\Downloads\rayjoin_pip_determinism_summary.md`
- RTDL source:
  - `src/native/optix/rtdl_optix_core.cpp`
  - `src/rtdsl/rayjoin_overlay.py`

## Paper Contract

The paper decomposes polygon overlay into LSI plus PIP/point-location:

- LSI casts line segments as rays with `tmin=0`, `tmax=1`.
- PIP casts a vertical ray upward from the query point.
- PIP selects the closest boundary edge and then maps that edge direction to a
  face id.
- Section 3.2 requires high precision beyond FP32, conservative AABB
  representation, integer/scaled coordinates, and Simulation of Simplicity for
  degenerate cases.
- Section 4.1 states RayJoin stores planar graph line segments, precomputes line
  coefficients, uses integer scaling, rational intersections, conservative
  AABBs, and SoS.

Relevant extracted paper text is cached in:

- `history/internal_docs/_tmp_ics24_text_for_rayjoin_check.txt`

## Author Source Contract

Author PIP source:

- `HEAD:src/algo/rt_pip_custom.cu`

Relevant observed lines:

- line 51-58: x-bound exclusion uses map-directed SoS; `query_map_id == 0`
  excludes `x_min`, while `query_map_id == 1` excludes `x_max`.
- line 63-80: computes `xsect_y` and rejects edges below the vertical-ray
  direction.
- line 90-99: equal-height slope comparator exists inside the intersection
  shader.
- line 96 comment: `If im==0 we want the bigger slope, if im==1, the smaller.`
- line 102-114: reports unperturbed `t` to OptiX.

Author overlay source:

- `HEAD:src/app/map_overlay_rt.h`

Relevant observed lines:

- line 205-216: overlay phase order is LSI, two `LocateVerticesInOtherMap`
  passes, then `ComputeOutputPolygons`.
- line 256-303: midpoint point-location writes `xsect1.mid_point_polygon_id`.

Author output-chain source:

- `HEAD:src/app/output_chain.h`

Relevant observed lines:

- line 118-125: output-chain assembly uses `xsect.mid_point_polygon_id` for
  intervals between adjacent intersections.

## Author Clarification Contract

The author-provided clarification explains that the original internal
equal-height comparator is not sufficient because OptiX can prune later equal-`t`
candidates before the shader sees them.

Required semantic patch:

```text
norm_slope = (atan(slope) + pi/2) / pi

query_map_id == 0: prefer larger slope
query_map_id == 1: prefer smaller slope

t_reported = t_edge + max(t_edge, 1.0) * (1.0 - tie_breaker) * 1e-14
```

Interpretation:

- more preferred candidates report a slightly smaller `t_reported`;
- equal-height selection becomes independent of OptiX traversal order.

## Source / Comment / Clarification Tension

The author source comment and author clarification both state:

- map 0 prefers the larger slope;
- map 1 prefers the smaller slope.

The committed source condition:

```text
if ((query_map_id && !flag) || (flag && !query_map_id)) continue;
```

where `flag = current_e_slope > best_e_slope`, appears to execute the opposite
direction when read literally.

Goal4834 resolves this by treating the author clarification as a semantic patch
to the author program, not merely as commentary.

## RTDL Alignment

RTDL OptiX implementation now uses the same direction in both places:

- internal equal-height comparator:

```text
query_map_id == 0u ? current_slope > best_slope : current_slope < best_slope
```

- reported-t preference:

```text
query_map_id == 0u ? normalized_slope : (1.0 - normalized_slope)
```

This prevents the previous mixed state where the internal comparator could
prefer one slope direction while `t_reported` preferred the other.

RTDL overlay midpoint ownership remains per directed map:

- `mid_point_polygon_id_map0`
- `mid_point_polygon_id_map1`

This is required because a single geometric intersection participates in both
map-directed output-chain traversals.
