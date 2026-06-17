# Goal4524 / V3 M128 Benchmark Implementation Queue

## Conclusion

M128 turns the post-clean-target app status into a concrete implementation queue. Goal4527 later moves Barnes-Hut into a design-blocker lane because a naive all-node OptiX any-hit mapping cannot preserve aggregate-subtree skip semantics. Goal4528 then validates the RT-DBSCAN prepared graph capture gate without changing the current direct-status component-signature route. Goal4530 validates Triangle Counting's device key/count payload merge, and Goal4531 validates device-output weighted replay while fail-closing CUDA graph capture for that OptiX launch. There is now no runtime build target in this queue; Triangle and Barnes-Hut are design blockers. RTNN and Spatial RayJoin remain claim/evidence packaging blockers rather than missing current primitives, and the other six apps have no immediate V3 runtime blocker.

## Summary

- Next runtime build target: `None`
- Runtime queue: ``
- Design blocker queue: `barnes_hut, triangle_counting`
- Claim/evidence queue: `rtnn, spatial_rayjoin`
- Closed current targets: `rt_dbscan, hausdorff_xhd, robot_collision, contact_manifold, raydb_style, librts_spatial_index`

## Queue

| App | Class | Priority | Remaining gap | Next build target |
| --- | --- | ---: | --- | --- |
| `barnes_hut` | `design_blocker` | 1 | Goal4527 blocks a naive node-AABB OptiX implementation: Barnes-Hut opening accepts a parent aggregate and must suppress its descendants, while a single custom-primitive GAS reports node AABBs independently and cannot enforce subtree-skip semantics without a reviewed generic hierarchical traversal design | do not replace the fail-closed ABI with a direct all-node any-hit route; future work must first design and review a generic hierarchical traversal lowering that proves no double counting, keeps force math outside app-specific native engine code, and then beats fused CPU/Numba and fused Numba CUDA force-summary baselines |
| `rt_dbscan` | `closed_current_target` |  | no current V3 runtime blocker after Goal4510 clean-target closure, Goal4520 live chunk-handle smoke, and Goal4528 prepared graph capture/replay validation | no immediate V3 build target; preserve the current direct-status component-signature route and keep M113 as an internal future same-stream-partner experiment shape |
| `triangle_counting` | `design_blocker` | 2 | Goal4530 validates app-agnostic device key/count payload merge for cross-chunk duplicate keys, and Goal4531 validates a generic prepared weighted-replay device-output stream executor; CUDA graph capture of that OptiX weighted launch is fail-closed with an OptiX/CUDA error, so future M113 graph use needs a reviewed native capture design rather than another benchmark rerun | do not claim Triangle M113 graph readiness; future work must first design a capture-compatible OptiX weighted replay mechanism or accept the stream device-output executor as a non-graph continuation contract |
| `rtnn` | `claim_or_evidence_blocker` | 10 | public paper-reproduction and same-output author claims remain blocked by dataset recipes and output-contract differences, not by a missing current RTDL primitive | freeze exact paper-family dataset recipes and author output contract comparisons before any public RTNN wording expansion |
| `spatial_rayjoin` | `claim_or_evidence_blocker` | 11 | full RayJoin paper-reproduction wording and Section 5.7 8/8 overlay wording remain claim-scoped; the current limitation is not a missing generic primitive for the already scoped 2/8 overlay evidence | keep the current mixed route; only expand public wording with an explicitly scoped author/data packet that states which overlay rows are feasible and which are not |
| `hausdorff_xhd` | `closed_current_target` |  | no current V3 runtime blocker after Goal4513 clean-target audit | no immediate V3 build target; preserve scoped claim boundary |
| `robot_collision` | `closed_current_target` |  | no current V3 runtime blocker after Goal4513 clean-target audit | no immediate V3 build target; preserve scoped claim boundary |
| `contact_manifold` | `closed_current_target` |  | no current V3 runtime blocker after Goal4513 clean-target audit | no immediate V3 build target; preserve scoped claim boundary |
| `raydb_style` | `closed_current_target` |  | no current V3 runtime blocker after Goal4513 clean-target audit | no immediate V3 build target; preserve scoped claim boundary |
| `librts_spatial_index` | `closed_current_target` |  | no current V3 runtime blocker after Goal4513 clean-target audit | no immediate V3 build target; preserve scoped claim boundary |

## Boundary

- No runtime was executed.
- No current route changed.
- No release, public speedup, broad RT-core, paper-reproduction, or automatic partner-selection wording is authorized.
