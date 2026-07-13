# Call For Review — Goal4820 Core Directed-Segment Point-Location and Overlay Midpoint Fix

Date: 2026-06-30

## Requested Verdict Labels

- `approve_goal4820_core_fix_and_author_public_sample_correctness_gate_passed`
- `approve_with_required_amendments`
- `fail_redo_goal4820`

## Context

Goal4817-Goal4819 showed that the released RTDL RayJoin bundled helper failed
byte equality against the RayJoin author's public County x Soil sample, while
the author binary reproduced the answer byte-for-byte.

The user then authorized product repair, with these boundaries:

- fix RTDL core/product defects when the RTDL semantics are wrong;
- do not add a RayJoin-only hidden native kernel;
- do not consider Embree;
- compare against the author's source and author-provided SoS clarification,
  not against guesses.

## Files To Review

- Product code:
  - `src/native/optix/rtdl_optix_core.cpp`
  - `src/rtdsl/rayjoin_overlay.py`
- Tests:
  - `tests/goal4373_rayjoin_cdb_point_location_route_test.py`
  - `tests/goal4374_rayjoin_exact_paper_suite_test.py`
- Evidence record:
  - `history/internal_docs/goal4820_core_directed_segment_point_location_sos_fix_2026-06-30.md`
  - `history/internal_docs/goal4820_core_sos_fix.patch`
  - `history/internal_docs/goal4820_author_pip_scalar_oracle.py`
  - `history/internal_docs/goal4820_rtdl_raw_chain_probe.py`
- POD artifacts:
  - `history/internal_docs/goal4820_artifacts_2026-06-30/after_midpoint_fix_summary.json`
  - `history/internal_docs/goal4820_artifacts_2026-06-30/author_pip_scalar_oracle_after_fix.json`

## What Changed

1. The OptiX directed-segment point-location kernel now encodes the
   author-clarified equal-depth SoS slope preference into reported hit distance.
   This prevents OptiX traversal pruning from bypassing equal-height
   tie-breaking.

2. The RayJoin overlay helper now stores midpoint point-location faces per
   directed map:
   - `mid_point_polygon_id_map0`
   - `mid_point_polygon_id_map1`

   The old single `mid_point_polygon_id` field was wrong because the same
   intersection object is reused in both map-sorted lists. Map 1 midpoint PIP
   assignment could overwrite map 0 midpoint PIP assignment.

## Key Evidence

Before the midpoint-face fix:

- raw chain 250 midpoint interval used `other=17`;
- the same midpoint's native RTDL point-location returned face `1113`;
- the scalar author-rule oracle also returned face `1113`;
- therefore the kernel was not wrong for this point; the batched overlay
  continuation assignment was wrong.

After the midpoint-face fix:

```json
{
  "answer_bytes": 16631243,
  "answer_sha256": "464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e",
  "byte_equal": true,
  "elapsed_sec": 6.219067253172398,
  "output_bytes": 16631243,
  "output_sha256": "464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e"
}
```

Local and POD focused tests passed:

```text
tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_overlay_midpoint_faces_are_stored_per_map
tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_overlay_output_chain_writer_is_not_legacy_seed
tests.goal4373_rayjoin_cdb_point_location_route_test.Goal4373RayjoinCdbPointLocationRouteTest
```

## Questions For Reviewer

1. Is the OptiX SoS reported-distance fix a valid RTDL directed-segment
   point-location contract repair, rather than a RayJoin-only shortcut?

2. Is the per-map midpoint face fix a valid product/data-model repair for
   directed overlay continuation, rather than a hidden RayJoin kernel?

3. Does the evidence justify saying the author public sample correctness gate
   now passes byte-for-byte?

4. Is it acceptable to retain the SoS core patch even though the public-sample
   byte-equality failure was ultimately repaired by the per-map midpoint face
   fix, given the author-provided non-determinism note?

5. Did the implementation avoid Embree and avoid public docs/tutorial/release
   surface changes?

6. Are the tests sufficient as focused regression coverage for the exposed
   defects, or is an additional unit/integration test required before moving to
   performance?

7. Should Goal4820 close and authorize the next goal: controlled performance
   comparison against the author binary on the same public sample, with no
   broad performance claim?

## Non-Authorization

This review request does not authorize:

- broad RayJoin paper reproduction claims;
- full Section 5.7 eight-pair claims;
- performance claims before controlled measurements;
- V3/V4 public release resurrection;
- Embree work;
- app-specific hidden native kernels.
