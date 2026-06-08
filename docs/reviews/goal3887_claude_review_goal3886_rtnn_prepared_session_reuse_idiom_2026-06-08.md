# Claude Review: Goal3886 RTNN Prepared-Session Reuse Idiom

## Verdict: `accept-with-boundary`

This review is read-only and **does not authorize release action, public
speedup wording, broad RT-core wording, true-zero-copy wording, automatic
partner/backend selection, or app-specific native-engine logic**. It does not
authorize any wording beyond what `docs/learn/prepared_session_reuse.md`, the
`prepared_session_residency` contract (`src/rtdsl/prepared_session_residency.py`),
and the Goal3881/Goal3883/Goal3885 review boundaries already permit.

## Scope

Goal3886 adds a `prepared_session_reuse_idiom` mode to
`examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
(`rtnn_prepared_session_reuse_idiom_payload`, lines 339-452, plus CLI/dispatch
wiring at lines 619-626 and 647, 678-685), updates the RTNN README and the
`prepared_session_reuse` learner page to document it, and adds
`tests/goal3886_rtnn_prepared_session_reuse_idiom_test.py`. It responds to the
gap the Goal3881/Goal3883/Goal3885 reviews all named: `get_or_prepare_explicit_session`
and `ExplicitPreparedSessionCache` were emitted only as descriptive metadata,
never actually exercised by an app.

## 1. Does it actually call `get_or_prepare_explicit_session` twice and record a real `miss`/`put`/`hit` event log?

**Yes**, and the trace matches the live helper exactly
(`prepared_session_residency.py:408-446`):

- `first = rt.get_or_prepare_explicit_session(cache, session_key, prepare_session_descriptor, policy=session_policy)`
  (`rtdl_rtnn_benchmark_app.py:400-405`): the cache starts empty, so
  `cache.get(key)` logs `{"event": "miss", ...}` (`:306-311, :310`), the helper
  then calls `prepare_session_descriptor()` (appending one `"prepare"` entry to
  `prepare_calls`) and `cache.put(key, value)` logs `{"event": "put", ...}`
  (`:295-304`). `first.cache_hit` is `False`.
- `second = rt.get_or_prepare_explicit_session(cache, session_key, prepare_session_descriptor, policy=session_policy)`
  (`:406-411`): `cache.get(key)` now finds the entry and logs
  `{"event": "hit", ...}` (`:312-313`) without calling
  `prepare_session_descriptor` again. `second.cache_hit` is `True`.
- The payload returns `"cache_hit_sequence": (first.cache_hit, second.cache_hit)`
  → `(False, True)`, `"cache_event_log": second.cache_event_log` → the full
  three-entry log `("miss", "put", "hit")` (since `cache.event_log` accumulates
  across both calls, and `second.cache_event_log` is captured after the third
  append), and `"prepared_call_count": len(prepare_calls)` → `1`.

This is exactly what `tests/goal3886_rtnn_prepared_session_reuse_idiom_test.py:55-60`
asserts (`prepared_call_count == 1`, `cache_hit_sequence == [False, True]`,
event names `["miss", "put", "hit"]`), and the assertions are checked against a
live subprocess invocation of the CLI (`_run_app`, lines 17-25), not a mock —
the same "exercise the real helper" standard the Goal3885 review praised in the
Goal3884 tutorial test.

One small accuracy note for the report wording: the report (line 30) says the
mode "records `miss`, `put`, and `hit` events," and the README (lines 49-51)
calls the result "the visible `miss`/`put`/`hit` event log" — both phrasings
read naturally as "the log contains these three events," which is correct
(`second.cache_event_log` is exactly `(miss, put, hit)`). Neither claims each
`get_or_prepare_explicit_session` call independently produces all three, which
would be wrong (the first call produces `miss`+`put`, the second produces only
`hit`). No correction needed; flagging only because a future edit that changed
which event log is surfaced (e.g., returning `first.cache_event_log` instead of
`second.cache_event_log`) would silently break this claim and the test
simultaneously — worth keeping in mind if this payload is ever refactored.

## 2. Does the new mode avoid altering the promoted `prepared_optix_ranked_summary` benchmark path?

**Yes.** I diffed `a214374a~1..a214374a` for this file
(`git diff a214374a~1 a214374a -- examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`)
and the change is purely additive with respect to the promoted path:

- `rtnn_prepared_optix_ranked_summary_payload` (lines 217-336) is byte-for-byte
  unchanged; the diff shows zero lines touched inside its body.
- The only structural change to existing code is in `main` (lines 668-687):
  the prior single ternary expression
  (`payload = (rtnn_prepared_optix_ranked_summary_payload(...) if args.mode == "prepared_optix_ranked_summary" else run_app(...))`)
  was rewritten as an `if`/`elif`/`else` chain to add the new mode's branch.
  The `prepared_optix_ranked_summary` branch still calls
  `rtnn_prepared_optix_ranked_summary_payload` with the identical keyword
  arguments (`point_count=args.point_count or args.copies, radius=args.radius,
  k=args.k, repeat=args.repeat, query_batch_size=args.query_batch_size,
  distribution=args.distribution, seed=args.seed`), and the final `else` branch
  still calls `run_app` with the identical arguments — the refactor is
  behavior-preserving.
- `run_app`'s existing `"prepared_optix_ranked_summary"` dispatch
  (lines 609-618) is untouched; the new `"prepared_session_reuse_idiom"`
  dispatch (lines 619-626) is inserted as a new `if` block immediately after
  it, not interleaved with it.

The promoted OptiX benchmark path is therefore unmodified in both code paths
that can reach it (direct CLI dispatch and `run_app`).

## 3. Is it clear this is a non-performance teaching path rather than new OptiX evidence?

**Yes**, and it is over-determined — the boundary is stated at every layer:

- The payload itself sets `"live_helper_invoked": True`,
  `"native_runner_invoked": False`, `"performance_evidence": False`
  (`:422-424`), and the nested `claim_boundary` adds
  `"not_performance_evidence": True` (`:450`) on top of the inherited
  `CLAIM_BOUNDARY` false-flags (`native_engine_customization`,
  `full_rtnn_paper_reproduction`, `public_speedup_claim_authorized`,
  `broad_rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`,
  `automatic_partner_selection_authorized`, `amd_performance_claim_authorized`
  — lines 441-451).
- Crucially, the function never imports or calls
  `scripts.goal2348_rtnn_v2_2_external_runner` (contrast with
  `rtnn_prepared_optix_ranked_summary_payload`, which does at line 272 and 285)
  and never touches `tempfile`/the OptiX backend's `run_rtdl_batched_3d_neighbors`
  entry point — there is no code path here that could produce timing evidence
  even by accident. The `prepare_session_descriptor` callable
  (`:385-398`) returns a pure `dict` marked `"descriptor_only": True` and never
  runs native code.
- The README (lines 49-53) and the tutorial page (lines 78-92) both describe
  the mode as "non-performance teaching path" / "not the promoted OptiX
  benchmark path," and explicitly say it "does not run the OptiX benchmark
  path" / "is intentionally not the promoted OptiX benchmark path." The report
  states `native_runner_invoked = false` and `performance_evidence = false`
  verbatim (lines 32-33), matching what `tests/...:96-97` asserts against the
  rendered report text.
- `session_key`/`session_policy` use `backend="optix"` and `device="cuda:0"`
  (`:357-358, 373`) purely as descriptor-shape inputs to
  `make_prepared_session_cache_key`/`RtdlPreparedSessionResidencyPolicy` — the
  same generic key-shape convention `rtnn_prepared_optix_ranked_summary_payload`
  uses (`:247-248, 262`) — not as a live backend selection. Given
  `native_runner_invoked = False` sits right alongside it in the same payload,
  a reader cannot mistake this for a live OptiX run; if anything, pairing a
  `backend="optix"`/`device="cuda:0"` key with `native_runner_invoked: False`
  slightly emphasizes that the cache key is descriptor metadata, not evidence
  of execution on that backend.

## 4. Does it preserve app-agnostic native-engine boundaries and avoid app-shaped primitive names?

**Yes.** The cache key uses `primitive="fixed_radius_neighbors_3d_ranked_summary"`
(`:357`), which is the exact generic primitive name the Goal3885-reviewed
tutorial documents as RTNN's mapped shape
(`current_prepared_session_residency_profiles.py` per
`docs/reviews/goal3885_..._2026-06-08.md:68-69`) and is identical to the one
`rtnn_prepared_optix_ranked_summary_payload` already uses (`:246`) — no new
primitive vocabulary is introduced. I checked it against every entry in
`PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS`
(`prepared_session_residency.py:43-65`, which notably includes `"rtnn"` itself)
and confirmed no substring match; `RtdlPreparedSessionCacheKey.__post_init__`
would raise `ValueError` at construction time if it did
(`_validate_no_app_terms`, `:86-90, 111`), so this is also a live-enforced
guarantee, not just a naming convention. The descriptor dict returned by
`prepare_session_descriptor` (`:387-398`) likewise contains only generic
primitive/backend/partner/device/point/radius/k/distribution/seed fields —
nothing RTNN-paper-specific or native-symbol-shaped leaks into the
caller-owned prepared value either.

## 5. Are README/tutorial/report/test updates sufficient and claim-bounded?

**Yes.**

- **README** (`examples/v2_0/research_benchmarks/rtnn/README.md:29, 49-53`)
  adds the exact runnable command and a paragraph that names
  `get_or_prepare_explicit_session`, `ExplicitPreparedSessionCache`, the
  `miss`/`put`/`hit` log, and explicitly disclaims speedup/zero-copy/automatic
  selection claims — consistent with the rest of the file's `Engine Boundary`
  section (lines 59-64).
- **Tutorial page** (`docs/learn/prepared_session_reuse.md:76-92`, "Try A Live
  App Idiom") gives the same runnable command, frames the mode as
  "intentionally not the promoted OptiX benchmark path," and states
  `native_runner_invoked = false` / `performance_evidence = false` — language
  that mirrors and reinforces (rather than duplicates with drift risk) the
  payload's own flags.
- **Report** (`docs/reports/goal3886_rtnn_prepared_session_reuse_idiom_2026-06-08.md`)
  documents purpose, what changed, the new mode's behavior bullet-for-bullet
  matching the actual payload contents, an explicit non-goals "Boundary"
  section (lines 35-49) restating the same six forbidden claims plus
  "app-specific native-engine logic," and a "Validation" section naming the new
  test and what it checks.
- **Test** (`tests/goal3886_rtnn_prepared_session_reuse_idiom_test.py`)
  exercises the live CLI via subprocess (not a mock), asserts the help text
  exposes the mode, asserts every structural claim from the report (live
  helper invoked, native runner not invoked, not performance evidence, call
  count, hit sequence, exact event-log shape, residency metadata flags, and
  every `claim_boundary` false-flag including `not_performance_evidence`), and
  separately asserts that the README/tutorial/report all contain the required
  vocabulary (`prepared_session_reuse_idiom`, `get_or_prepare_explicit_session`,
  `miss`/`put`/`hit`, "not"/"performance") plus the report's two literal
  boundary lines. I traced every assertion back to a corresponding
  payload field or doc passage and found no mismatch.

I could not find any place where the new docs or report overstate what the
idiom demonstrates — they consistently describe it as a mechanics demo of an
*explicit, caller-owned* cache (the README even repeats "caller-owned
`ExplicitPreparedSessionCache`"), never as a recommendation to cache by
default or as evidence that caching helps performance.

## Validation

I was not able to execute
`tests/goal3886_rtnn_prepared_session_reuse_idiom_test.py` in this sandboxed
session — `python -m pytest ...` and related invocation forms require approval
I do not have, the same limitation the Goal3883/Goal3885 reviews hit. I instead
performed a full static review: read the app module's new function and its CLI
wiring end to end, diffed the commit against its parent to confirm the
promoted path is untouched, read the README/tutorial/report/test files, traced
every test assertion to the corresponding payload field or live helper/cache
behavior in `prepared_session_residency.py`, and checked the cache-key
primitive against the live forbidden-term validator. I found no mismatch
between the documented behavior, the test assertions, and the live code.

## Summary

Goal3886 closes the specific gap the Goal3881/Goal3883/Goal3885 reviews named:
`get_or_prepare_explicit_session` and `ExplicitPreparedSessionCache` are now
actually exercised, end to end, by a real app mode, with a real
`miss`→`put`→`hit` event-log trace returned in the JSON payload and asserted
against by a subprocess-level test. The new mode is additive only — it neither
touches nor reuses any code path that could produce OptiX timing evidence —
and is labeled `native_runner_invoked = false` / `performance_evidence = false`
at the payload, README, tutorial, and report layers consistently. The cache
key reuses the existing generic `fixed_radius_neighbors_3d_ranked_summary`
primitive name (which also passes the live `_validate_no_app_terms` check
against a forbidden-term list that includes `"rtnn"` itself), so no
app-shaped vocabulary leaks into the prepared-session surface.

`accept-with-boundary`: this idiom demo should ship as documented, carrying
forward the same non-authorizing claim-boundary language it already states,
and without being read as turning explicit prepared-session caching into a
*default* recommendation or as new performance evidence for the RTNN
benchmark — both of which the payload, README, tutorial, and report correctly
continue to disclaim.
