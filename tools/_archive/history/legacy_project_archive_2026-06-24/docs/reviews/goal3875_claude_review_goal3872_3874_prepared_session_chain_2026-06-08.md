# Claude Review: Goal3872-3874 Prepared-Session Chain

Date: 2026-06-08

Reviewer: Claude (independent read-only review)

Verdict: **accept-with-boundary**

## Summary

Goal3872 measured cold scene/payload preparation versus hot prepared-query
execution for four scene-heavy benchmark rows on an A5000
(Hausdorff/X-HD, LibRTS spatial index, RTNN, triangle counting). Goal3873
turned that observation into a generic, app-agnostic prepared-session
residency contract (cache key, lifetime/invalidation policy, explicit cache,
cold/hot timing record). Goal3874 connected the contract to the four measured
rows as an internal profile registry. I independently inspected the probe
script, the A5000 `summary.json` artifact, both new `src/rtdsl` modules, both
reports, both test files, `rtdsl/__init__.py` exports, the
`current_benchmark_scale_profiles` registry the profiles reference, and the
`future_version_to_do_list.md` entry. I could not execute the test suite in
this sandboxed session (the harness blocked every form of `PYTHONPATH=...
py -3 -m unittest ...` invocation, including via a helper script), so the
findings below are from static cross-checking of the artifacts and code rather
than a live test run — this is noted as a residual verification gap, not a
defect in the work itself.

## Findings (ordered by severity)

No correctness or honesty issues found. Notes below are confirmations and one
minor robustness observation.

1. **(Info) Goal3872's numbers are bit-for-bit consistent end to end.** I
   re-extracted `prepare_sec`, `hot_query_per_request_sec`, and
   `prepare_to_single_query_ratio` directly from
   `docs/reports/goal3872_prepared_session_amortization_a5000/summary.json`
   and compared them against (a) the Goal3872 report table, (b) the Goal3873
   report's bullet list, and (c) every `prepare_sec`/`hot_query_sec` field in
   `CURRENT_PREPARED_SESSION_RESIDENCY_PROFILES`
   (`src/rtdsl/current_prepared_session_residency_profiles.py:148-211`). All
   four rows match to full float precision (e.g. RTNN
   `1.7026465376839042` / `0.00013345852494239807` →
   `12757.870195394278x`; triangle counting `0.39183870516717434` /
   `0.00015036482363939285` → `2605.9200262615127x`). Nothing was rounded,
   re-derived, or re-estimated between goals — the chain reuses one
   measurement.

2. **(Info) Goal3872 stays a triage probe, not a claim.** The probe
   (`scripts/goal3872_prepared_session_amortization_probe.py:24-71,283-331`)
   recursively scans every probed app's JSON payload for eleven forbidden
   `*_authorized`/`*_allowed` flags being `true` (a superset of the nine flags
   it self-asserts as `false`), marks any hit as `status=fail`, and the report
   explicitly states "This goal does not change the native engine" and "is not
   release evidence and not a public speedup claim"
   (`docs/reports/goal3872_..._2026-06-08.md:14-16,82-85`). I independently
   grepped the artifact and found `claim_flag_violations: []` on all four rows
   and `all_claim_boundaries_clean: true` in the summary — the self-reported
   cleanliness is corroborated by the scan, not merely asserted.

3. **(Info) `prepared_session_residency.py` is app-agnostic by both
   denylist and structural means.** `_validate_no_app_terms`
   (`prepared_session_residency.py:73-77`) rejects any cache-key primitive
   containing one of `hausdorff, rayjoin, dbscan, barnes, database, pip,
   polygon, knn` (`PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS:43-52`), and
   `Goal3873PreparedSessionResidencyContractTest.
   test_cache_key_is_stable_and_rejects_app_shaped_primitives` exercises the
   rejection path with `"hausdorff_threshold_path"`. Independently of the
   denylist, every claim-authorization property on
   `RtdlPreparedSessionResidencyPolicy` (`release_authorized`,
   `public_speedup_claim_authorized`, `broad_rt_core_claim_authorized`,
   `true_zero_copy_claim_authorized`, `automatic_partner_selection_authorized`,
   `app_specific_native_engine_logic_allowed`, lines 173-194) is a hardcoded
   `return False` — not a settable field — so no caller can construct a policy
   that asserts any of these true. The module exposes exactly the contract
   asked for: `RtdlPreparedSessionCacheKey` (explicit primitive/backend/
   partner/device/input+parameter fingerprints with a stable digest),
   `RtdlPreparedSessionResidencyPolicy` (lifetime state, reuse scope,
   invalidation events, cold/hot phase names),
   `RtdlPreparedSessionTimingRecord` (prepare/hot-query timing and ratio), and
   `ExplicitPreparedSessionCache` (an explicit, caller-owned, non-global cache
   that records hit/miss/evict/invalidate events and closes evicted/
   invalidated handles via `_close_value`).

   *Minor robustness note:* `PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS`
   is a curated list rather than one derived from
   `V2_8_PROMOTED_BENCHMARK_APPS` (`v2_8_benchmark_runtime_gap.py:12-23`).
   Several promoted app names would not be caught by substring matching —
   e.g. `robot_collision`, `contact_manifold`, `raydb_style`,
   `librts_spatial_index` → `librts`, `rtnn`, `triangle_counting` →
   `triangle`. This is not a live problem (the four chosen primitive names —
   `fixed_radius_threshold_2d`, `aabb_index_query_2d`,
   `fixed_radius_neighbors_3d_ranked_summary`,
   `ray_triangle_weighted_any_hit_sum_3d` — are already generic and contain
   none of these), but the denylist is hand-maintained and could miss a future
   app-shaped term that isn't on the historical list. Worth widening or
   deriving it from the promoted-app registry in a later goal.

4. **(Info) Goal3874 connects rows to the contract honestly, without
   pretending to be an implemented cache or a release packet.** Every
   `CurrentPreparedSessionResidencyProfile.__post_init__`
   (`current_prepared_session_residency_profiles.py:56-80`) raises
   `ValueError` if the app is not in `V2_8_PROMOTED_BENCHMARK_APPS`, if
   `prepare_sec`/`hot_query_sec`/`repeat` are non-positive, if `evidence_refs`
   is empty, or if **any** of the six claim-authorization fields is `True` —
   this is a structural, fail-closed guarantee at construction time, not a
   hand-curated assertion. All four entries set `cache_enabled_by_default`
   to its default of `False` and `evidence_refs=("Goal3872",)`. I confirmed
   each `scale_profile_row_id` (`hausdorff_xhd_scale_default_optix_threshold`,
   `librts_spatial_index_optix_scale_default_32768`,
   `rtnn_prepared_optix_scale_default_65536`,
   `triangle_counting_optix_rt_graph_2a1_scale_default_2048`) resolves to a
   real row in `current_benchmark_scale_profiles.py` (lines 96, 286, 314,
   341). The report states plainly: "This registry is not a benchmark release
   packet. It is an internal current-row profile registry"
   (`docs/reports/goal3874_..._2026-06-08.md:41-44`), and
   `prepared_session_reuse_recommended` is a derived `>= 10x` boolean, not an
   amortization or speedup claim.

5. **(Info) Claim-boundary checks are layered and machine-checkable.**
   Three independent layers all assert and verify the same six/nine flags:
   the probe's `FORBIDDEN_TRUE_FLAGS` payload scan (script, defends against
   probed apps lying), the contract's hardcoded `False` properties plus
   `validate_prepared_session_residency_contract`
   (`prepared_session_residency.py:399-429`, checks contract version, status
   string, six flags, and the three `requires_*` booleans), and the profile
   registry's `__post_init__` raise-on-True plus
   `validate_current_prepared_session_residency_profiles`
   (`current_prepared_session_residency_profiles.py:256-296`, additionally
   checks row-id uniqueness, row count `>= 4`, ratio `>= 10x`, scale-profile
   linkage, contract-version match, and primitive denylist). All three
   `validate_*` functions return a structured `{status, errors, ...}` dict
   that the corresponding test suites assert is `"accept"` with `errors ==
   ()`. This is the same fail-closed pattern used in the Goal3828/Goal3844
   chain (`docs/reviews/goal3845_..._2026-06-08.md`), reused consistently
   here.

## What Remains Before User-Facing Runtime Ergonomics

This chain is, by its own and the report's framing, evidence and contract —
not an implemented feature. Concretely, before any of this becomes
user-facing:

- **No wiring exists yet.** A repo-wide search for
  `ExplicitPreparedSessionCache`, `RtdlPreparedSessionResidencyPolicy`, and
  `make_prepared_session_cache_key` shows they are referenced only inside
  `prepared_session_residency.py`,
  `current_prepared_session_residency_profiles.py`, and `rtdsl/__init__.py` —
  no benchmark app, example, or tutorial constructs a cache key or uses the
  explicit cache yet, and `cache_enabled_by_default=False` on every profile
  row underscores that this is metadata, not behavior.
- **User-facing ergonomics work remains**: example/tutorial code that shows
  "prepare once, issue many queries" with an explicit, visible cache key in
  user code; benchmark-report changes that surface cold/hot phase splits by
  default (rather than only in an internal probe); and a decision on what
  lifetime/eviction defaults make sense for a real session (today the policy
  exists only as a contract object, with no app wiring to validate it under
  load).
- **A release packet would still be required** before any prepare/query ratio
  could become public amortization or speedup wording — every layer in this
  chain currently hardcodes that authorization to `false`, and that should
  stay true until such a packet exists.

## Boundary (if accepted)

This review covers Goal3872 (prepared-session amortization probe and A5000
evidence), Goal3873 (prepared-session residency contract), and Goal3874
(current prepared-session residency profile registry) only. It does **not**
authorize: release action, public speedup wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, or app-specific
native-engine logic. All three goals' own claim-boundary strings already say
the same thing, and every machine-checkable flag I inspected is hardcoded or
validated to `false`/rejected — this review simply confirms that framing is
accurate and internally consistent, not that any of those wordings are now
permitted.

## Note on Validation

I was unable to run
`tests.goal3874_current_prepared_session_residency_profiles_test`,
`tests.goal3873_prepared_session_residency_contract_test`,
`tests.goal3872_prepared_session_amortization_test`, or
`tests.goal3828_current_benchmark_scale_profile_registry_test` in this
session — every invocation of `py -3 -m unittest ...` (directly, via `cmd`,
via a `.ps1` helper script, and via `export`/`$env:` to set `PYTHONPATH`) was
blocked by the sandbox before it could run. Static review of the test source
shows the assertions match the code and artifacts I inspected (e.g. ratio
thresholds, claim-flag-false assertions, report-phrase checks), so I have no
reason to expect a failure, but a live run by a reviewer with an unsandboxed
shell would close this gap.
