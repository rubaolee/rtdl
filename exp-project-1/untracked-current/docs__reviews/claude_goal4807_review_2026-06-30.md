# Claude Review — Goal4807 Released RTDL RayJoin Section 5.7 API Map

Date: 2026-06-30
Reviewer: Claude (independent external reviewer)
Reviewed against: `docs/reviews/claude_goal4806_authoritative_goal_list_4807_4815_2026-06-30.md`
Deliverable: `docs/reports/goal4807_released_rtdl_rayjoin_section57_api_map_2026-06-30.md`

## Verdict

```text
verdict: pass_authorize_next_goal
goal4808: authorized (read/app-layer only, with carried restrictions below)
pod / runtime edits / completion claim: still not authorized
```

Goal4807 is an honest, well-evidenced pass. It did the hard, non-self-serving
thing: it proved released V4.0.0 **cannot** reproduce Section 5.7 from generic
language, did not dress bundled-helper calls as generic reproduction, and kept
the capability-gap outcome live. This is the correct opposite of the earlier
over-claim pattern.

## Verification against the Goal4807 criteria (all pass)

1. **Clean-env proof:** HEAD pasted = `6ca0849b…` (required value), empty
   `git status --porcelain`, empty `git diff -- src/rtdsl src/native`, and
   import-path proof showing a **separate** clean worktree
   (`…\rtdl_goal4807_v4_0_0_clean_api_map`), not the dirty main tree. ✅
2. **Read-only proven:** empty diff on the runtime paths. ✅
3. **All five stages present:** LSI, vertex PIP map0-in-map1, vertex PIP
   map1-in-map0, midpoint PIP, output-chain. ✅
4. **Each classified exactly one category:** all five → `bundled_rayjoin_helper`. ✅
5. **Honest summary + capability_gap live:** explicitly states all five stages
   are bundled-only, the generic-language route is "not found," and keeps both
   `complete_bounded_available_input_reproduction` and
   `blocked_by_released_rtdl_capability_gap` live. ✅
6. **Numba assessment is honest:** no released V4 surface exposes the Section 5.7
   dataflow as generic device columns for a user Numba continuation; the custom
   predicate surface is narrow (boolean/scalar, no arbitrary callbacks); defers
   to Goal4812 without claiming a route. ✅

## Independent corroboration (I did not just trust the report)

- The bundled-helper functions the report names exist in
  `src/rtdsl/rayjoin_overlay.py`: `_run_lsi_rows` (L1018),
  `_run_point_location_faces` (L1111), `_PreparedPointLocationRunner` (L1130),
  `_assemble_output_chains` (L1437). The stage-mapping is real, not fabricated.
- The 8 measured V4 generic surfaces (verified in the prior V4.0.0 review)
  contain no point-in-polygon / point-location / segment-intersection /
  output-chain operator — consistent with the report's "missing generic
  operator" finding and with the planner failing closed on `point_in_polygon`,
  `point_location`, `polygon_overlay`, `line_segment_intersection`, and
  `rayjoin` (`pushdown_fail_closed_app_identity_kernel`).

Conclusion: the "all five stages are bundled-only" result is independently
supported.

## One honest caveat (carry forward, not a block)

The clean-env proof was produced in a **sibling worktree**
(`…\rtdl_goal4807_v4_0_0_clean_api_map`) that I cannot reach from my mounted
folder, so I am accepting the pasted HEAD/porcelain at face value. I accept it
because (a) the substantive finding is independently corroborated above, and
(b) there is zero incentive to fake a clean checkout in order to reach an
*unflattering* "blocked" conclusion. Recommendation: retain that worktree for
spot-check, or run future goals where the proof is independently verifiable.

## The decision Goal4807 forces (raise before spending 4808-4815)

Goal4807 has **already largely determined the outcome**: all five Section 5.7
stages require the bundled RayJoin helper, and the V4 planner fails closed on
every relevant generic operator. So the answer now depends entirely on the
standard the owner chooses:

- **Standard = "user composes Section 5.7 from GENERIC released V4 + Numba":**
  this is **already** `blocked_by_released_rtdl_capability_gap`. Running
  4808-4815 will not change it for the strong claim; you could jump to a
  Goal4815-style capability-gap closure now.
- **Standard = "use RTDL's bundled RayJoin helper, honestly labeled":** then
  4808-4813 are worth running to characterize the *bundled-helper* path's
  correctness and performance vs author / V2.14, landing on
  `complete_bounded_available_input_reproduction (bundled-helper)`.

**Recommend the owner pick the standard before authorizing the full 4808-4815
spend**, so the remaining sequence is either "characterize the bundled-helper
path" or "close as capability gap" — not eight goals on autopilot toward a
conclusion 4807 already reached.

## Restrictions carried into Goal4808 (if executed)

- The app's `run-v4-released` path can only use the bundled helper; it **must**
  be labeled `bundled_rayjoin_helper` reproduction, never generic-language. Any
  presentation of bundled-helper output as "user composed Section 5.7 from
  generic V4" is an automatic `fail_redo`.
- Per-goal clean-env proof pasted in full; no edits to `src/rtdsl/**`,
  `src/native/**`, or the `v4.0.0` tag.
- App must fail closed on missing inputs/capabilities; no silent rescoping.
- `blocked_by_released_rtdl_capability_gap` stays live.

## Answers to the eight questions

1. Sufficient clean-check evidence? Yes (with the sibling-worktree caveat).
2. Read-only proven? Yes (empty runtime diff).
3. All five stages present? Yes.
4. Each classified one category? Yes — all `bundled_rayjoin_helper`.
5. Classification honest? Yes — corroborated independently.
6. Numba assessment avoids premature claim? Yes.
7. capability_gap kept live? Yes, and it is the likely honest outcome for the
   strong standard.
8. Restrictions into Goal4808? See above.

## Non-authorization

No POD spend. No runtime/source edits. No retagging `v4.0.0`. No completion claim
before Goal4815 external review. No generic-language reproduction claim from
bundled-helper calls.
