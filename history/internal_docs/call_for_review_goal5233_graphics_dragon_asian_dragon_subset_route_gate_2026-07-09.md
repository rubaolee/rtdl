# Call For Review: Goal5233 Graphics Dragon -> AsianDragon Subset Route Gate

Please strictly review Goal5233.

## Files To Review

```text
history/internal_docs/goal5233_graphics_dragon_asian_dragon_subset_route_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5205_fast_ascii_ply_matrix_loader_test.py
tests/goal5178_xhd_priority_input_bridge_test.py
tests/goal5181_xhd_full_public_subset_scaling_gate_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5232_priority_input_bridge_graphics_dragon_asian_dragon_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5233_graphics_dragon_asian_dragon_scale_profile_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5233_graphics_dragon_asian_dragon_subset16_numpy_2026-07-09.json
```

Context:

```text
history/internal_docs/goal5232_graphics_dragon_asian_dragon_input_bridge_result_2026-07-09.md
history/internal_docs/call_for_review_goal5232_graphics_dragon_asian_dragon_input_bridge_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
```

## Review Questions

1. Does the bridge direction now come from `source_basename` /
   `target_basename` / `author_basename_order`, rather than hard-coded
   Dragon -> HappyBuddha paths?
2. Does the binary PLY loader correctly support Stanford
   `binary_big_endian 1.0` vertex coordinates while keeping mesh semantics
   app-owned and outside RTDL core?
3. Do the tests preserve the old ASCII-only loader fail-closed behavior while
   adding a generic PLY loader path for binary PLY?
4. Does the Dragon -> AsianDragon subset gate use the real full public
   candidates with point counts 437,645 and 3,609,600?
5. Is the 16-source exact oracle legitimate and bounded
   (`57,753,600` pair evaluations, no full pairwise materialization)?
6. Does the route result exactly match the subset oracle
   (`route_abs_diff = 0.0`)?
7. Does the report correctly avoid claiming all-source HDResult reproduction,
   Figure 6 reproduction, exact paper input identity, or author performance
   parity?
8. Does the report correctly disclose that the RTDL route is slower than the
   exact 16-source oracle in this run?
9. Are the tests and validations sufficient for a bounded route/input-loader
   gate?
10. Should Goal5233 close as
    `completed_graphics_dragon_asian_dragon_bounded_subset_route_gate__level_b_only`?

## Expected Answer Shape

```text
Verdict:
  approve_goal5233_graphics_dragon_asian_dragon_subset_route_gate
  or approve_with_required_amendments
  or block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 10 review questions:
  ...
```

## Claim Boundary To Enforce

Allowed:

```text
Dragon -> AsianDragon public same-source candidate files can feed a bounded
RTDL route, and the 16-source route matches an exact subset oracle.
```

Forbidden:

```text
Exact paper dataset identity is proved.
Dragon -> AsianDragon all-source HDResult is reproduced.
Figure 6 is reproduced.
RTDL is faster than exact or author code on this target.
Author-vs-RTDL performance parity is established.
Full X-HD paper reproduction is complete.
```
