# Goal4524 / V3 M128 Benchmark Implementation Queue

## Conclusion

M128 turns the post-clean-target app status into a concrete implementation queue. Goal4527 later moves Barnes-Hut into a design-blocker lane because a naive all-node OptiX any-hit mapping cannot preserve aggregate-subtree skip semantics. The next runtime build target is now RT-DBSCAN prepared graph capture, followed by Triangle Counting chunked unique/count payload merge. RTNN and Spatial RayJoin remain claim/evidence packaging blockers rather than missing current primitives, and the other five apps have no immediate V3 runtime blocker.

## Summary

- Next runtime build target: `rt_dbscan`
- Runtime queue: `rt_dbscan, triangle_counting`
- Design blocker queue: `barnes_hut`
- Claim/evidence queue: `rtnn, spatial_rayjoin`
- Closed current targets: `hausdorff_xhd, robot_collision, contact_manifold, raydb_style, librts_spatial_index`

## Queue

| App | Class | Priority | Remaining gap | Next build target |
| --- | --- | ---: | --- | --- |
| `barnes_hut` | `design_blocker` | 1 | Goal4527 blocks a naive node-AABB OptiX implementation: Barnes-Hut opening accepts a parent aggregate and must suppress its descendants, while a single custom-primitive GAS reports node AABBs independently and cannot enforce subtree-skip semantics without a reviewed generic hierarchical traversal design | do not replace the fail-closed ABI with a direct all-node any-hit route; future work must first design and review a generic hierarchical traversal lowering that proves no double counting, keeps force math outside app-specific native engine code, and then beats fused CPU/Numba and fused Numba CUDA force-summary baselines |
| `rt_dbscan` | `runtime_blocker` | 2 | chunk-local prepared direct-status handles are live-smoke validated, but prepared graph capture/replay for the chunked continuation is not | add a generic prepared graph capture/replay path for chunk-local direct-status handles and same-stream partner continuation, preserving no-hidden-upload and no pair-row materialization gates |
| `triangle_counting` | `runtime_blocker` | 3 | scalar per-chunk unique counts are not associative when duplicate keys cross chunk boundaries; an M113-safe path needs key/count payload merge or proven disjoint key ranges plus graph capture | build a generic chunked key/count payload merge primitive or disjoint-key-range plan, then validate a coarser prepared continuation with fewer per-segment launches |
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
