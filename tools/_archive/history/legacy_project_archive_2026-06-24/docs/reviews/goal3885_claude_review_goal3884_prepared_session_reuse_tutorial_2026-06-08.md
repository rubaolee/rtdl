# Claude Review: Goal3884 Prepared-Session Reuse Tutorial

## Verdict: `accept-with-boundary`

This review is read-only and **does not authorize release action, public
speedup wording, broad RT-core wording, true-zero-copy wording, automatic
partner/backend selection, or app-specific native-engine logic**. It also does
not authorize any wording beyond what `docs/learn/prepared_session_reuse.md`,
the `prepared_session_residency` contract
(`src/rtdsl/prepared_session_residency.py`), and the Goal3881/Goal3883 review
boundary already permit.

## Scope

Goal3884 adds a new learner page,
`docs/learn/prepared_session_reuse.md`, that teaches the explicit
prepare-once/query-many cache idiom built in Goals 3872-3882, and links it
into both learner indexes (`docs/tutorials/README.md` step 8 and
`docs/learn/README.md` step 8). It also adds
`tests/goal3884_prepared_session_reuse_tutorial_test.py` and a scope report,
`docs/reports/goal3884_prepared_session_reuse_tutorial_2026-06-08.md`.

## 1. Does the page correctly explain the explicit cache pattern using the real API?

**Yes.** I cross-checked every API element the page teaches against
`src/rtdsl/prepared_session_residency.py` and the `rtdsl` package re-exports
(`src/rtdsl/__init__.py:143-159`):

- `make_prepared_session_cache_key(primitive=..., backend=..., input_fingerprints=...,
  parameters=..., partner=..., device=...)` (`prepared_session_residency.py:449-470`)
  matches the page's example call (`prepared_session_reuse.md:40-47`) argument
  for argument, and the claim "the input and parameter fingerprints define the
  cache key" (line 71) matches how `input_fingerprints`/`parameter_fingerprint`
  are built (`:461-467`).
- `ExplicitPreparedSessionCache(max_entries=4)` and
  `get_or_prepare_explicit_session(cache, key, prepare_session)`
  (`prepared_session_reuse.md:38, 56-57`) match the live constructor and helper
  signatures (`:288-291`, `:408-419`); the helper's miss → `prepare_session()` →
  `cache.put` → result, and hit → `cache.get` → result flow
  (`:427-446`) is exactly the "make a stable key -> prepare once on a miss ->
  reuse the prepared handle -> invalidate visibly" summary on line 9.
- The asserted `cache_hit` values (line 59-60), `to_metadata()` flags (line
  63-64), invalidation calls `cache.invalidate(key, event=...)` /
  `cache.clear(event=...)` (line 81-82), the documented invalidation event list
  (line 87-93), and the `close()`-on-eviction/invalidate/clear behavior (line
  95-96) all match `ExplicitPreparedSessionCache.invalidate/clear/_close_value`
  (`:316-338, 360-364`) and `RtdlPreparedSessionReuseResult.to_metadata`
  (`:391-405`).
- The "Reading App Metadata" table (`prepared_session_reuse.md:104-112`) lists
  `cache_key`, `policy`, `cache_enabled_by_default`,
  `cold_hot_phase_split_required`, `automatic_partner_selection_authorized`,
  `true_zero_copy_claim_authorized`, and `public_speedup_claim_authorized`. I
  confirmed these are the exact keys the four profiled apps actually emit under
  `"prepared_session_residency"` — e.g.
  `rtdl_hausdorff_distance_app.py:961-971`,
  `rtdl_librts_spatial_index_benchmark_app.py:600-605`, and
  `rtdl_triangle_counting_benchmark_app.py:899-904` all use
  `"cold_hot_phase_split_required"` verbatim. (Note this app-level field name
  differs slightly from the *internal* contract helper field names
  `cold_hot_split_required`/`requires_cold_hot_phase_split` in
  `prepared_session_residency.py:273, 482`; the page correctly documents what a
  learner will actually see in app JSON, not the internal helper's field
  names — this is the right choice, not an inconsistency to fix.)
- The "Current measured examples" table (`prepared_session_reuse.md:21-28`)
  maps each app family to a generic primitive shape. I verified this mapping
  is exactly the one in `CURRENT_PREPARED_SESSION_RESIDENCY_PROFILES`
  (`current_prepared_session_residency_profiles.py:148-211`): Hausdorff/X-HD →
  `fixed_radius_threshold_2d`, LibRTS → `aabb_index_query_2d`, RTNN →
  `fixed_radius_neighbors_3d_ranked_summary`, triangle-counting →
  `ray_triangle_weighted_any_hit_sum_3d`. No app-shaped name leaks into the
  "Generic primitive shape" column.

## 2. Does it preserve the v2.10 single-surface learner-doc rule?

**Yes.** The page opens with a single, present-tense "RTDL v2.10 supports..."
statement (line 3) and contains no version-history table, no "as of vX.Y this
changed" narrative, and no references to superseded surfaces. Both index
updates (`docs/tutorials/README.md:28, 43` and `docs/learn/README.md:14`) slot
the new page into the existing current-surface ladder without touching the
"Tutorial Archive" section or any other historical material — consistent with
the existing single-surface rule stated at `docs/tutorials/README.md:12-15`.

## 3. Does it avoid overclaiming?

**Yes**, on every axis the review questions name:

- *Release action / public speedup*: line 12-14 states explicitly "RTDL does
  not... turn the pattern into a public speedup or true-zero-copy claim," and
  the "Claim Boundary" section (lines 114-126) lists exactly the six forbidden
  claims from the Goal3884 report and the `prepared_session_residency`
  contract's `claim_boundary` string (`prepared_session_residency.py:13-18`).
- *Broad RT-core acceleration*: "broad RT-core speedup wording" is explicitly
  named as not authorized (line 120); no RT-core performance claim appears
  anywhere in the page.
- *True zero-copy*: only appears as a forbidden-claim label and as an asserted
  `False` metadata flag (lines 64, 111, 121) — never asserted as true.
- *Hidden automatic partner/backend selection*: line 12-13 ("RTDL does not
  choose a backend, does not choose a partner") and lines 70, 122 reinforce
  that backend/partner stay caller-chosen; the example hard-codes
  `backend="optix"`/`partner="numba"` as caller-supplied arguments.
- *App-specific native-engine behavior*: line 123 names this as not authorized,
  and line 125-126 ("The native engine stays app-agnostic... the application
  still decides what the result means") matches the
  `app_specific_native_engine_logic_allowed: False` flags asserted throughout
  `prepared_session_residency.py`.

I grepped the rendered text for the forbidden phrases the test checks
(`guarantees speedup`, `automatic backend selection`, `true zero-copy is
authorized`, `app-specific native engine`) and found none, matching
`test_tutorial_claim_boundary_is_non_authorizing`.

## 4. Is the wording consistent with the Goal3881/Goal3883 idiom-vs-default-recommendation boundary?

**Yes, and the page goes further than its predecessors in a way that is
itself bounded correctly.** The Goal3881 and Goal3883 reviews
(`docs/reviews/goal3881_claude_review_goal3880_rtnn_residency_metadata_2026-06-08.md:113-119`
and
`docs/reviews/goal3883_claude_review_goal3882_profiled_apps_residency_metadata_2026-06-08.md:134-159`)
both flagged the same gap: `get_or_prepare_explicit_session` and
`ExplicitPreparedSessionCache` were never actually exercised anywhere — only
emitted as descriptive metadata labels — so the pattern was "internal
ergonomics scaffolding rather than something ready to teach as a default user
idiom."

Goal3884's minimal example is the first place in the tree that actually
*calls* the live helper end to end and asserts a real `cache_event_log` of
`("miss", "put", "hit")` (verified directly against
`test_minimal_cache_example_matches_live_contract`, which exercises the exact
same call sequence against the live `rtdsl` import). This closes the "no live
exercise of the helper" half of the prior gap.

Critically, the page does **not** overstate what this closes: it frames the
material as "When To Use It" / "Minimal Pattern" / mechanics-and-invalidation,
never as "you should always do this" or "this is the default," and it
explicitly keeps "Current measured examples include..." scoped to naming which
generic primitive shapes have prepared-session profiles today — it does not
attach a ratio, a recommendation threshold, or "you will see N× speedup" to
any of them (contrast with the internal
`prepared_session_reuse_recommended` flag and `prepare_to_hot_query_ratio`
values visible in
`current_prepared_session_residency_profiles.py:132-134`, neither of which the
page surfaces or claims). The "What remains before this becomes a default
idiom" half of the prior gap — worked guidance on *when* reuse pays off — thus
correctly remains untaught here, and the page does not pretend otherwise.

## 5. Is the test sufficient?

**Mostly yes, with one minor observation.** Reading
`tests/goal3884_prepared_session_reuse_tutorial_test.py`:

- `test_indexes_link_to_prepared_session_reuse_page` guards both index links
  and titles — sufficient and matches what I confirmed by reading both READMEs.
- `test_tutorial_teaches_live_api_and_metadata_surface` and
  `test_tutorial_claim_boundary_is_non_authorizing` guard the required API
  names, metadata field names, and both required and forbidden claim-boundary
  phrases — I confirmed every required phrase is present and every forbidden
  phrase absent by reading the rendered page directly.
- `test_minimal_cache_example_matches_live_contract` is the strongest test
  here: it runs the *exact* sequence shown in the tutorial against the live
  `rtdsl` import (not a mock) and asserts `cache_hit`, identity reuse
  (`second.value is first.value`), the `("miss", "put", "hit")` event-log
  shape, and three `to_metadata()` false-flags. This directly guards the part
  of the page most likely to silently rot (a renamed kwarg, a changed event
  name, or a flipped default flag would fail this test immediately).
- `test_report_documents_goal3884_scope` guards the scope report's required
  phrases; I confirmed all six phrases are present in
  `docs/reports/goal3884_prepared_session_reuse_tutorial_2026-06-08.md`.

One minor gap: the test does not assert that the example's
`primitive="fixed_radius_threshold_summary_3d"` string passes
`_validate_no_app_terms` for a *reason* — i.e., there's no test that would fail
loudly if a future edit introduced an app-shaped primitive name into the
tutorial's code block (today it would only fail because the live call would
raise `ValueError` inside `test_minimal_cache_example_matches_live_contract`,
which is an acceptable indirect guard, just not a self-documenting one). I
manually checked `fixed_radius_threshold_summary_3d` against every entry in
`PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS`
(`prepared_session_residency.py:43-65`) and confirmed no substring match, so
the example is valid as written; this is a documentation observation, not a
defect requiring a fix before acceptance.

## Validation

I was not able to execute
`tests/goal3884_prepared_session_reuse_tutorial_test.py` in this sandboxed
session — every invocation form (`pytest`, `python -m pytest`, `set
PYTHONPATH=...`, `$env:PYTHONPATH=...`) was blocked pending approval I do not
have, the same limitation the Goal3883 review hit
(`docs/reviews/goal3883_claude_review_goal3882_profiled_apps_residency_metadata_2026-06-08.md:163-165`).
I instead performed a full static cross-check: read the tutorial page, both
index files, the scope report, the test file, the live
`prepared_session_residency.py` module, the `rtdsl` package re-exports, and
the four profiled-app payload sites that emit `prepared_session_residency`
metadata, and traced every phrase/name/flag the test asserts back to its
source. I found no mismatch between the documented API/metadata surface and
the live code, and no claim-boundary violation in the rendered page text.

## Summary

The new page is an accurate, correctly-bounded, and now *executable* (via its
guarding test) explanation of the explicit prepared-session reuse idiom. It
matches the live API and the actual `prepared_session_residency` JSON shape
emitted by the four profiled apps, preserves the v2.10 single-surface rule,
and stays inside the Goal3881/Goal3883 boundary — including by *not*
overreaching into "default recommendation" or "measured speedup" territory
even though it is now the first place in the tree to exercise the helper live.
`accept-with-boundary`: the page should ship as current v2.10 learner
guidance, carrying forward the same non-authorizing claim-boundary language it
already states, and without being read as closing the broader "ready to teach
as a default idiom" gap that Goal3881/Goal3883 left open (worked
when-to-cache guidance still does not exist and is correctly not claimed
here).
