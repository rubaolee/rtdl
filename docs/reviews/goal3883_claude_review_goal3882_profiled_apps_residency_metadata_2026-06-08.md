# Claude Review: Goal3882 Profiled-App Residency Metadata (Hausdorff/X-HD, LibRTS, Triangle-Counting)

## Verdict: `accept-with-boundary`

This review is read-only and **does not authorize release action, public
speedup wording, broad RT-core wording, true-zero-copy wording, automatic
partner/backend selection, or app-specific native-engine logic**. It also does
not authorize any wording beyond what the `prepared_session_residency`
contract (`src/rtdsl/prepared_session_residency.py`) and each app's existing
`claim_boundary` already permit.

## Scope

Goal3882 extends the Goal3880 RTNN pattern — emitting a descriptive,
non-authorizing `prepared_session_residency` block from prepared-session
payloads — to the three remaining current profiled prepared-session apps:

- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`

## 1. Do the patched apps emit metadata without changing computation paths?

**Yes.** In all three apps the new code is additive and sits after the
existing compute/timing logic, immediately before payload construction:

- Hausdorff (`rtdl_hausdorff_distance_app.py:901-918`): `session_key` and
  `session_policy` are built from values (`points_a`/`points_b` counts,
  `copies`, `hausdorff_threshold`, `backend`) that were already computed for
  the `directed_threshold_prepared` payload; the existing `directed_ab` /
  `directed_ba` calls and oracle validation are untouched.
- LibRTS (`rtdl_librts_spatial_index_benchmark_app.py:550-568`): the key/policy
  block is constructed in the `finally`-guarded cleanup region, after
  `prepared_query_cache` and `prepared` have already been closed, using only
  already-known counts (`fixture.boxes`, `point_queries`, `box_queries`,
  `operation`, `prepared_queries`).
- Triangle-counting (`rtdl_triangle_counting_benchmark_app.py:818-835`): the
  block is built from `primitive_count`, `ray_count`, `fixture`,
  `rt_graph_copies`, `detail`, and `summary_result is not None`, all already
  computed for `v2_4_phase_timing`/`v2_4_session`.

In each case the new `"prepared_session_residency"` key is simply added to the
returned dict alongside the pre-existing keys; no existing key's value is
recomputed or altered. `git show 8fcbd352` confirms each diff is a pure
addition (37/34/32 inserted lines, 0 removed) for the three app files.

## 2. Are the primitive names generic and app-agnostic?

**Yes**, and this is enforced structurally, not just by convention.
`RtdlPreparedSessionCacheKey.__post_init__` calls `_validate_no_app_terms` on
`primitive` (`prepared_session_residency.py:111`), which raises if any of the
forbidden terms in `PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS`
(`prepared_session_residency.py:43-65` — including `hausdorff`, `hausdorff_xhd`,
`librts`, `triangle_counting`, `rtnn`, etc.) appear, case-insensitively, in the
primitive string. The three primitives used —

- `fixed_radius_threshold_2d`
- `aabb_index_query_2d`
- `ray_triangle_weighted_any_hit_sum_3d`

— describe geometric query shapes (radius threshold, AABB index query,
weighted any-hit ray/triangle sum), not app names, and pass that validation
(if they didn't, `make_prepared_session_cache_key` would raise at call time —
confirmed the code paths reach `RtdlPreparedSessionCacheKey.__post_init__`).
Note `ray_triangle_weighted_any_hit_sum_3d` contains the substring `triangle`
but not the forbidden `triangle_counting`, which is consistent with the
pattern's intent (the primitive names a generic ray/triangle geometry
operation, not the benchmark).

App-identifying strings (e.g. `fixture="degree_oriented_two_triangles"`,
`"copies"`) are only ever passed into `input_fingerprints`/`parameters`, which
`make_prepared_session_cache_key` runs through `_stable_digest`
(SHA-256-truncated) before they reach `to_metadata()` — so no app-specific
vocabulary leaks into the emitted cache-key metadata even indirectly.

## 3. Does the A5000 artifact prove all four rows pass with false flags?

**Yes**, with one nuance worth recording for future readers.
`docs/reports/goal3882_profiled_apps_residency_metadata_a5000/summary.json`
shows `"all_pass": true`,
`"selected_prepared_session_residency_profile_count": 4`, and
`"json_pass_count": 4`, with `returncode: 0` and
`"prepared_session_residency_profiled": true` for all four rows
(`hausdorff_xhd`, `librts_spatial_index`, `rtnn`, `triangle_counting`). Each
row's captured live-app `stdout_tail` contains a `prepared_session_residency`
block whose `cache_key.primitive` matches the table in the report
(`fixed_radius_threshold_2d`, `aabb_index_query_2d`,
`fixed_radius_neighbors_3d_ranked_summary`,
`ray_triangle_weighted_any_hit_sum_3d`), and every flag visible in those
blocks (`automatic_partner_selection_authorized`,
`true_zero_copy_claim_authorized`, `public_speedup_claim_authorized`) is
`false`.

The nuance: the **registry-level** `prepared_session_residency_profile` rows
embedded in this artifact (the `cache_key.input_fingerprints` blocks under
e.g. `rows[0].prepared_session_residency_profile.cache_key`, fingerprint names
`boxes`/`queries`) come from the separate Goal3874 profile registry and use
older/coarser fingerprint-name groupings than the **live app payload** emitted
by the Goal3882 code (fingerprint names `boxes`/`point_queries`/`box_queries`,
matching `rtdl_librts_spatial_index_benchmark_app.py:553-557`). The test file
(`tests/.../goal3882_..._test.py:160-180`) correctly checks the **live**
`stdout_path` payload rather than the registry profile, so this discrepancy
does not affect the pass/fail result — but a reader skimming only the embedded
registry blocks could mistake the older fingerprint grouping for what the
patched code now emits. Worth a one-line note in a future revision of the
report distinguishing "registry profile (Goal3874, prior shape)" from "live
payload (Goal3882, current shape)".

## 4. Did the triangle-counting boundary-key refresh improve checkability without authorizing new claims?

**Yes.** `git show 8fcbd352` shows the only non-residency change to
`rtdl_triangle_counting_benchmark_app.py` is three new keys added to the
shared module-level `CLAIM_BOUNDARY` dict
(`rtdl_triangle_counting_benchmark_app.py:63-65`):

```
"true_zero_copy_claim_authorized": False,
"automatic_partner_selection_authorized": False,
"app_specific_native_engine_logic_allowed": False,
```

All three are `False`, matching every other false flag already in
`CLAIM_BOUNDARY`. Because `CLAIM_BOUNDARY` is a single shared dict referenced
by `"claim_boundary": CLAIM_BOUNDARY` (and `**CLAIM_BOUNDARY`) from at least
nine payload sites in the file (lines 115, 137, 225, 281, 366, 645, 703, 908,
1083), this single addition propagates the same three explicit `false` flags
to every payload mode the app can emit — not just the new
`rt_graph_2a1_generic_rt_payload` path — giving any downstream scanner (e.g.
`scripts/goal1906_public_v2_claim_boundary_scan.py`) a uniform, explicit
signal across the whole app rather than only the newly touched function. This
is a pure key-set widening with constant `False` values; it does not change,
weaken, or newly authorize any claim.

## 5. What remains before this pattern should become a tutorial / default idiom?

The same gap identified in the sibling Goal3880/RTNN review
(`docs/reviews/goal3881_claude_review_goal3880_rtnn_residency_metadata_2026-06-08.md`,
"What remains before learner-facing docs should teach this as a default
idiom") still applies, and Goal3882 does not close it — it simply repeats the
same descriptive-metadata-only pattern three more times:

- **No live exercise of the helper.** A repo-wide search confirms
  `get_or_prepare_explicit_session(` and `ExplicitPreparedSessionCache(` are
  never actually called from any example app — the string
  `"explicit_reuse_helper": "get_or_prepare_explicit_session"` is emitted as a
  metadata label only. None of the four profiled apps (RTNN, Hausdorff/X-HD,
  LibRTS, triangle-counting) demonstrates a real `cache_event_log` with
  `miss`/`put`/`hit` transitions driven from app code.
- **No worked guidance on when reuse pays off.** The A5000 artifact shows
  `prepare_to_hot_query_ratio` values ranging from ~13.6:1 (LibRTS) to
  ~12,758:1 (RTNN) across the four rows — a strong internal signal that
  prepare-once/query-many is sometimes very advantageous and sometimes only
  modestly so — but per the claim boundary none of this can yet be surfaced as
  a public speedup or "when to cache" recommendation.
- Until at least one app shows the helper/cache exercised end to end with a
  visible hit/miss cycle, and a separately authorized way exists to discuss
  *when* reuse is worthwhile without crossing the speedup-claim boundary, this
  remains internal ergonomics scaffolding rather than something ready to teach
  as a default user idiom.

## Validation

I was unable to execute the requested unittest commands in this sandboxed
session (the harness blocked invocation of the `py` launcher / `PYTHONPATH`
environment changes regardless of approach). I instead reviewed the test file
(`tests/goal3882_prepared_session_residency_metadata_remaining_profiled_apps_test.py`)
directly:

- It mocks all native/expensive calls (`_FakePreparedAabb`, `_FakePreparedQuery`,
  `_FakeTriangleScene`, `_run_prepared_directed_threshold`,
  `expected_tiled_hausdorff`) and asserts the metadata shape via a shared
  `_assert_metadata` helper that checks the same false-flag set the report
  claims (`automatic_partner_selection_authorized`,
  `true_zero_copy_claim_authorized`, `public_speedup_claim_authorized`,
  policy-level flags) plus `cache_key.primitive` per app.
- It separately asserts the report text contains the documented phrases and
  that the A5000 artifact's `all_pass`/row set/per-row metadata match what the
  report table claims, reading from the **live** `stdout_path` payload (not
  the registry profile), which is the correct comparison point per my note in
  §3.

The test logic is consistent with the report's claims; readers who can run
`PYTHONPATH='src;.' py -3 -m unittest ...` should do so to confirm green.

## Summary

This is a narrow, additive, metadata-only extension of an already-reviewed
pattern (Goal3880/RTNN) to three more apps, with structural enforcement
(`_validate_no_app_terms`, frozen-dataclass `False` properties) backing the
genericity and non-authorization claims, and a passing A5000 artifact backing
the "all four rows emit the metadata with false flags" claim. The boundary-key
addition to `CLAIM_BOUNDARY` is a pure widening of explicit `False` flags that
improves uniform machine-checkability across the whole triangle-counting app.
Recommend `accept-with-boundary`: accept the change as reviewed, with the
boundary that (a) the report should eventually clarify the registry-profile
vs. live-payload fingerprint-shape difference noted in §3, and (b) none of
this — including the "reuse_recommended" framing inherited from the Goal3874
registry — authorizes release action, public speedup wording, broad RT-core
wording, true-zero-copy wording, automatic partner/backend selection, or
app-specific native-engine logic, exactly as each emitted `claim_boundary`
already states.
