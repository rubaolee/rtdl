# Call For Review: Goal5232 Graphics Dragon -> AsianDragon Input Bridge

Please strictly review Goal5232.

## Files To Review

```text
history/internal_docs/goal5232_graphics_dragon_asian_dragon_input_bridge_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py
tests/goal5178_xhd_priority_input_bridge_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5232_priority_input_bridge_graphics_dragon_asian_dragon_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/data/external/stanford/README.md
```

Context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
history/internal_docs/goal5177_paper_target_log_mapping_result_2026-07-08.md
```

## Review Questions

1. Does the new bridge correctly target `graphics_dragon_asian_dragon` and not
   disturb the existing Dragon -> HappyBuddha bridge?
2. Does the bridge correctly identify the author paper-branch run_all records
   for `dragon.ply -> asian_dragon.ply`?
3. Do the public Stanford candidate point counts match the author logs?
4. Are archive/PLY hashes and PLY headers recorded sufficiently for Level-B
   same-source provenance?
5. Does the binary-safe PLY header reader fix a real issue for
   `binary_big_endian 1.0` AsianDragon PLY files?
6. Does the report correctly avoid claiming exact paper input identity?
7. Does the report correctly avoid claiming author/RTDL HDResult reproduction,
   Figure 6 reproduction, or performance parity?
8. Is it acceptable that Goal5232 performs acquisition/provenance only and
   leaves execution to a later capacity/route gate?
9. Are the tests sufficient for the bridge-level change?
10. Should Goal5232 close as
   `completed_graphics_dragon_asian_dragon_public_stanford_candidate_bridge__level_b_only`?

## Expected Answer Shape

```text
Verdict:
  approve_goal5232_graphics_dragon_asian_dragon_input_bridge
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
Dragon -> AsianDragon now has a public Stanford same-source candidate bridge
with point counts matching the author paper-branch logs.
```

Forbidden:

```text
Exact paper dataset identity is proved.
Dragon -> AsianDragon HDResult has been reproduced.
Figure 6 has been reproduced.
Author-vs-RTDL performance parity is established.
Full X-HD paper reproduction is complete.
```
