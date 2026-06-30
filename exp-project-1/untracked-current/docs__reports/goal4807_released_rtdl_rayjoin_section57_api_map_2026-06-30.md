# Goal4807 Released RTDL RayJoin Section 5.7 API Map

Date: 2026-06-30

## Scope

Goal4807 is a read-only map of released RTDL V4.0.0 APIs for RayJoin paper
Section 5.7 Polygon Overlay. It answers one narrow question:

> Can an installed user reproduce Section 5.7 from released RTDL V4.0.0 +
> Python + Numba without editing RTDL?

This report does not implement a user app, does not run POD performance, and
does not modify RTDL source.

## Clean Environment Proof

Fresh worktree:

```text
C:\Users\Lestat\Desktop\work\rtdl_goal4807_v4_0_0_clean_api_map
```

Command:

```powershell
git rev-parse HEAD
```

Full output:

```text
6ca0849b9930295f742485cae9a17196216e0dcf
```

Command:

```powershell
git status --porcelain
```

Full output:

```text
```

The porcelain status is empty.

Command:

```powershell
git diff -- src/rtdsl src/native
```

Full output:

```text
```

The diff is empty. Goal4807 made no edits to `src/rtdsl/**` or `src/native/**`.

Import-path proof from the clean checkout:

```json
{
  "PYTHONPATH": "src",
  "cwd": "C:\\Users\\Lestat\\Desktop\\work\\rtdl_goal4807_v4_0_0_clean_api_map",
  "rtdsl_file": "C:\\Users\\Lestat\\Desktop\\work\\rtdl_goal4807_v4_0_0_clean_api_map\\src\\rtdsl\\__init__.py",
  "v4_file": "C:\\Users\\Lestat\\Desktop\\work\\rtdl_goal4807_v4_0_0_clean_api_map\\src\\rtdsl\\v4.py",
  "has_status_v4": false
}
```

The clean tag import uses the fresh worktree path, not the main development
worktree. `rtdsl.v4` in this tag does not expose `status_v4`; the authoritative
release boundary is `claim_boundary_v4()`.

## Released V4 Public Surface Relevant To This Map

The V4 front door exposes generic measured operator surfaces such as:

- `v4_ray_triangle_any_hit_flags_2d_device_arrays`
- `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- `v4_point_group_nearest_witness_2d_device_arrays`
- `v4_aabb_index_query_2d_all_ops_count_prepared_runner`
- `v4_aggregate_frontier_device_columns_2d_prepared_runner`
- `v4_ray_triangle_custom_predicate_early_exit_3d_numba`

The released tag also contains RayJoin-specific bundled helpers:

- `src/rtdsl/rayjoin_overlay.py`
- `src/rtdsl/rayjoin_paper_suite.py`
- `src/rtdsl/rayjoin_artifacts.py`
- `src/rtdsl/v2_13_rayjoin_authors_code_packet.py`
- `scripts/rayjoin_paper_reproduction_suite.py`

Per the Claude authority file, calls through those `rayjoin_*` helpers classify
as `bundled_rayjoin_helper`. They support only the claim that RTDL ships a
RayJoin compatibility helper. They do not support the stronger claim that a
normal user composed Section 5.7 from generic V4 language operators.

## Section 5.7 Stage Map

| Section 5.7 stage | Released callable path found | Classification | Language-claim support |
| --- | --- | --- | --- |
| LSI, segment pair intersections | `scripts/rayjoin_paper_reproduction_suite.py::_run_rtdl_lsi` calls `rtdsl.rayjoin_overlay._run_lsi_rows`, which sets the RayJoin LSI predicate environment and uses RTDL segment-pair internals. | `bundled_rayjoin_helper` | No. Low-level segment-pair internals exist, but the exact Section 5.7 contract is reached through bundled RayJoin helper logic. |
| Vertex PIP, map0 vertices in map1 | `rtdsl.rayjoin_overlay._run_point_location_faces` and `_PreparedPointLocationRunner` call directed segment point-location with RayJoin CDB point-location environment. | `bundled_rayjoin_helper` | No. The V4 front door does not expose an exact generic point-in-polygon / CDB face-location operator for this stage. |
| Vertex PIP, map1 vertices in map0 | Same `rayjoin_overlay` point-location pair route, with reversed map direction and RayJoin-specific scale/grouping environment. | `bundled_rayjoin_helper` | No. Same reason as the previous row. |
| Midpoint PIP | `rtdsl.rayjoin_overlay` derives midpoint points from LSI rows, then routes them through the bundled point-location helper pair. | `bundled_rayjoin_helper` | No. This is composition inside the RayJoin helper, not a released V4 generic user composition surface. |
| Output-chain construction | `rtdsl.rayjoin_overlay._assemble_output_chains` and `write_output_chains`. | `bundled_rayjoin_helper` | No. Output-chain assembly is RayJoin overlay application logic, not a generic V4 operator. |

## Numba Assessment At Goal4807

Released V4.0.0 has certified or measured Numba-related surfaces:

- `v4_fixed_radius_graph_component_union_3d_device_arrays`
- `v4_ray_triangle_custom_predicate_early_exit_3d_numba`
- generic Numba continuation helpers in `numba_partner_continuation.py`

However, Goal4807 found no released V4 surface that exposes the Section 5.7
LSI/PIP/midpoint/output-chain dataflow as generic device columns suitable for a
user-level Numba continuation. The available custom predicate surface is
deliberately narrow: pure boolean/scalar Numba C-ABI device predicates with RTDL
owning the traversal action. It does not authorize arbitrary OptiX callbacks,
shared-state mutation, dynamic allocation, or variable-length output.

Therefore, Numba remains a possible later assessment item for Goal4812, but the
Goal4807 map does not support claiming that released V4.0.0 already lets a user
compose Section 5.7 with Numba from generic V4 public APIs.

## Planner Checks

The clean V4 planner recognizes generic operators such as
`ray_triangle_any_hit_flags`. It fails closed for app identity or unsupported
requests:

- `rayjoin`: `pushdown_fail_closed_app_identity_kernel`
- `polygon_overlay`: `unsupported_no_fused_surface`
- `line_segment_intersection`: `unsupported_no_fused_surface`
- `point_in_polygon`: `unsupported_no_fused_surface`
- `point_location`: `unsupported_no_fused_surface`
- `directed_segment_point_location`: `unsupported_no_fused_surface`

This is consistent with the V4 rule: generic operator pushdown is allowed;
application identity kernels are not.

## Provisional Outcome

Goal4807 result:

```text
api_map_complete__released_v4_section57_generic_language_route_not_found
```

Live likely final labels:

- `complete_bounded_available_input_reproduction`, if later goals are allowed to
  use and clearly label the bundled RayJoin helper route.
- `blocked_by_released_rtdl_capability_gap`, if the required standard remains
  "normal user composes Section 5.7 from generic released V4 + Python + Numba."

The stronger generic-language reproduction is currently blocked because all
five required Section 5.7 stages map to `bundled_rayjoin_helper`, not to
`generic_rtdl_operator` or `numba_user_continuation`.

## No-Edit Statement

No source edits were made. No runtime modifications are proposed. If the user
requires generic-language Section 5.7 reproduction, the missing surfaces must be
recorded as product gaps rather than patched into the released V4.0.0 tag.

## Goal-Level Mistake Audit

1. Was I being stupid?
   No for this Goal4807 pass: the work stayed read-only and used a fresh clean
   checkout.
2. If yes, what action made it stupid?
   Not applicable in this pass.
3. Is there another path that avoids getting stuck on a bad premise?
   Yes: treat bundled helper success and generic-language success as separate
   claims, and do not convert helper evidence into a language claim.
4. Can I now try the different path that actually solves the problem?
   Yes: submit this API map for review. Only if it passes should Goal4808 decide
   whether to build a fail-closed user app, and that app must preserve the same
   classification boundaries.
