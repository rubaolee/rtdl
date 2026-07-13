# Call For Review — Goal4973 Exact LSI Producer And Downstream Floor Cost Decomposition

Please review:

`history/internal_docs/goal4973_exact_lsi_producer_cost_decomposition_goal_2026-07-04.md`

## Requested Verdict

`approve_goal4973_exact_lsi_and_downstream_floor_cost_decomposition`

## Review Questions

1. Is Goal4973 the correct next step after Goal4972 showed the count pass is not the bottleneck?
2. Does the amended goal correctly incorporate the review finding that LSI setup is likely
   amortizable while the `~2.56s` downstream floor is persistent?
3. Does the goal correctly focus on both:
   - the unaccounted gap between Python LSI phase time and native traversal timing
   - the prepared-replay downstream floor?
4. Are the proposed LSI timing phases sufficient to distinguish compile/setup/workspace/traversal/copy?
5. Are the proposed downstream phases sufficient to identify the persistent steady-state floor?
6. Does the goal preserve generic planar-map LSI boundaries and avoid RayJoin-specific core work?
7. Should implementation be limited to timing instrumentation until the phase table identifies the
   bottleneck?
8. Are the exit labels sharp enough to determine the next optimization goal, including the possibility
   that the next target should be downstream rather than LSI?
