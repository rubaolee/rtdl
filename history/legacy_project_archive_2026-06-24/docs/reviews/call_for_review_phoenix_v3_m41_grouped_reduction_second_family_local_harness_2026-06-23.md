# Call For Review: Phoenix V3 M41 Grouped-Reduction Second-Family Local Harness

Requested reviewer: external AI reviewer

Requested verdict labels:

- `accept_m41_grouped_reduction_second_family_local_continue`
- `accept_with_caveats_before_cuda_smoke`
- `block_m41_wrong_family`
- `block_m41_harness_not_generic`

## Context

M40 produced one accepted-with-caveats, then locally fixed, focused Step-1 probe
for `fixed_radius_graph_component_union`.

M41 selects grouped reduction as the second Step-2 local family and implements a
local focused harness. This is not a POD result and not performance evidence.

Review these files:

- `docs/reports/phoenix_v3_m41_grouped_reduction_second_family_local_harness_2026-06-23.md`
- `scripts/v3_phoenix_grouped_reduction_m41_local_harness.py`
- `tests/v3_phoenix_m41_grouped_reduction_harness_test.py`
- `docs/reviews/codex_claude_phoenix_v3_m40_component_union_focused_pod_intake_2ai_consensus_2026-06-23.md`
- `docs/reports/phoenix_v3_m36_grouped_vector_sum_prepared_session_core_node_2026-06-23.md`

## Claims To Check

1. Grouped reduction is a valid second family after component-union because it
   exercises a different generic continuation primitive.
2. The harness is generic and app-agnostic.
3. The harness uses the productized prepared-execution runner path for the
   runner variant.
4. The harness exposes hot and wall comparisons separately.
5. The harness does not authorize POD, release, all-app, public speedup, V4,
   C ABI, embedding, or true-zero-copy claims.

## Questions

1. Is grouped reduction the right M41 second-family local target, or should
   RTNN/Triangle/Hausdorff/RayJoin be prioritized instead?
2. Is the CPU/legacy/productized-runner variant structure sufficient for a
   local Step-2 review packet?
3. Does the harness remain generic, or does it accidentally smuggle in app
   semantics?
4. Are the machine-readable metrics sufficient before a CUDA smoke or future
   focused POD request?
5. Should a free local Linux CUDA smoke be required before asking for any paid
   POD?
6. Are the claim boundaries strict enough?
7. What P0/P1 changes are required before M41 can proceed?

## Non-Authorization

This review request does not authorize release, all-app POD spend, additional
focused POD spend, public speedup wording, V4/embedding/C-ABI work, true-zero-copy
claims, or broad V3-over-V2 claims.
