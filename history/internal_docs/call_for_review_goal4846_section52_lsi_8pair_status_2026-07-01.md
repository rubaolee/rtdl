# Call For Review - Goal4846 RayJoin Section 5.2 LSI 8-Pair Status

Date: 2026-07-01

## Requested Verdict Labels

- `approve_goal4846_available_pairs_pass_missing_inputs_recorded`
- `approve_with_required_amendments`
- `block_goal4846_due_to_overclaim_or_insufficient_evidence`

## Files To Review

- `history/internal_docs/goal4846_section52_lsi_8pair_completion_plan_2026-07-01.md`
- `history/internal_docs/goal4846_section52_lsi_dataset_inventory_2026-07-01.md`
- `history/internal_docs/goal4846_section52_lsi_results_2026-07-01.md`
- `history/internal_docs/goal4845_section52_lsi_county_zipcode_status_2026-07-01.md`
- `history/internal_docs/antigravity_goal4845_section52_lsi_collapsed_ray_fix_review_2026-07-01.md`

Remote artifacts:

- `/workspace/goal4846_lsi_block_water_rtdl_optix.json`

## Claim Under Review

Goal4846 should be accepted as:

```text
available Section 5.2 LSI pairs completed on the current POD:
  County x Zipcode: AuthorPatch 961165, RTDL 961165
  Block x Water:    AuthorPatch 649605, RTDL 649605

remaining six lakes/parks pairs:
  missing exact CDB inputs on the current POD
```

This is **not** a full 8/8 exact-paper-input claim.

## Evidence Summary

### County x Zipcode

Goal4845 result:

| Route | Count |
|---|---:|
| AuthorPatch | 961165 |
| RTDL OptiX | 961165 |
| Delta | 0 |

Goal4845 also repaired a generic collapsed-float candidate-ray defect and added a synthetic regression test.

### Block x Water

AuthorPatch command had to use relative CDB paths from `/workspace/rtdl_goal4806_fast_min` to hit the existing `/dev/shm` serialized cache. Absolute `/workspace/...` paths missed that cache and timed out in `read_pgraph/load_from`; that was a harness/cache-key issue, not an LSI algorithm issue.

AuthorPatch result:

```text
Intersections: 649605
Query: 22.6271 ms
```

RTDL result:

```text
count: 649605
native_traversal_median_sec: 0.008402552
elapsed_sec: 20.367579385638237
```

Interpretation:

- correctness passes;
- performance is bounded and not yet a broad speedup claim because RTDL wrapper elapsed time and native traversal time differ greatly.

### Six Missing Pairs

The current POD lacks:

- `lakes/Africa` x `parks/Africa`
- `lakes/Asia` x `parks/Asia`
- `lakes/Australia` x `parks/Australia`
- `lakes/Europe` x `parks/Europe`
- `lakes/North_America` x `parks/North_America`
- `lakes/South_America` x `parks/South_America`

An all-`/workspace` search for `lakes_*_Point.cdb` and `parks_*_Point.cdb` returned no matches.

## Questions For Reviewer

1. Is it correct to accept County x Zipcode and Block x Water as Section 5.2 LSI correctness passes under the current AuthorPatch-vs-RTDL standard?
2. Is the Block x Water cache-key diagnosis credible and properly bounded as an execution-harness issue?
3. Does the report correctly avoid claiming full 8/8 exact-paper-input reproduction?
4. Does the report correctly classify the six lakes/parks pairs as `missing_exact_input` on the current POD?
5. Is the performance interpretation honest: correctness passes, but no broad performance win is authorized?
6. Are any additional pair-diff or synthetic tests required for Block x Water given `delta = 0`?
7. Should Goal4846 close as `available_pairs_pass_missing_inputs_recorded`, or should more work be required first?

## Non-Authorization

This review must not authorize:

- V3/V4 claims;
- Embree claims;
- full RayJoin paper reproduction;
- full 8/8 Section 5.2 completion without missing inputs;
- Section 5.7 overlay correctness;
- broad RTDL speedup wording;
- regenerated data being called exact paper input.
