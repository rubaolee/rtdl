# Goal3881 Claude Review: Goal3880 RTNN Prepared-Session Residency Metadata

## Scope

Read-only review of Goal3880, which adds `prepared_session_residency` metadata
to the RTNN benchmark app's `prepared_optix_ranked_summary` payload, wiring in
the Goal3873/Goal3877 explicit prepared-session contract
(`src/rtdsl/prepared_session_residency.py`).

This review does not authorize release action, public speedup wording, broad
RT-core wording, true-zero-copy wording, automatic partner/backend selection,
or app-specific native-engine logic.

## Verdict: accept

## Findings

### 1. Generic cache key/policy without runner path or timing changes — confirmed

The diff against `325916fa` (`git show 325916fa -- .../rtdl_rtnn_benchmark_app.py`)
is purely additive: it inserts a `session_key` /
`session_policy` construction (`rtdl_rtnn_benchmark_app.py:245-270`) before the
existing `tempfile.TemporaryDirectory` / `rtnn_runner.run_rtdl_batched_3d_neighbors`
call, and appends a `prepared_session_residency` block to the returned payload
dict (`rtdl_rtnn_benchmark_app.py:315-325`). No existing line that builds the
`Namespace` passed to the runner, selects `result_mode`, or governs `repeat`/
`warmup`/timing was touched. The CLI dispatch (`run_app` at line 493 and `main`
at line 543) is unchanged in its call shape for `prepared_optix_ranked_summary`.

The cache key is built through the generic
`rt.make_prepared_session_cache_key` / `RtdlPreparedSessionResidencyPolicy`
helpers (imported via `rtdsl` and exported from
`src/rtdsl/prepared_session_residency.py`), using the app's actual arguments
(`point_count`, `distribution`, `seed`, `query_batch_size`, `radius`, `k`) as
input/parameter fingerprints, `backend="optix"`, `partner="none"`,
`device="cuda:0"`. `cache_enabled=False` is passed explicitly, so the policy
documents reuse without enabling a hidden cache. The primitive name
`fixed_radius_neighbors_3d_ranked_summary` passes
`_validate_no_app_terms` in `prepared_session_residency.py:86-90` — it contains
none of the forbidden app-shaped terms (notably not `rtnn`, `knn`, or any
other entry in `PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS`), so the
contract's own generic-name guard is satisfied by construction, not just by
convention.

**Answer: yes** — the payload exposes a generic prepared-session cache key and
policy for the app's real arguments without altering the runner path or timing
behavior.

### 2. A5000 artifact proves the live payload shape — confirmed

`docs/reports/goal3880_rtnn_prepared_session_residency_a5000/summary.json`
shows `all_pass: true`,
`selected_prepared_session_residency_profile_count: 1`, one row
(`rtnn_prepared_optix_scale_default_65536`, `status: "pass"`,
`prepared_session_residency_profiled: true`), with
`semantic_stdout_check.claim_flag_violations: []`.

The companion stdout artifact
(`outputs/rtnn_prepared_optix_scale_default_65536.stdout.json`) contains the
live app payload with `mode: "prepared_optix_ranked_summary"` and a
`prepared_session_residency` block whose `explicit_reuse_helper` is
`"get_or_prepare_explicit_session"`, `cache_enabled_by_default: false`, and
`cache_key.primitive: "fixed_radius_neighbors_3d_ranked_summary"`
(stable_id `4a185ec5efbe5660797c051c`, `backend: "optix"`, `partner: "none"`,
`device: "cuda:0"`). This matches what
`tests/goal3880_rtnn_prepared_session_residency_metadata_test.py::test_a5000_artifact_confirms_live_payload_metadata`
asserts.

**Answer: yes** — the artifact is consistent with the claimed live payload
shape end to end (summary row → stdout JSON → metadata fields).

### 3. Claim-boundary flags — all false, as required

Across both the app payload (`claim_boundary` at
`rtdl_rtnn_benchmark_app.py:326-335`) and the embedded
`prepared_session_residency` block, every relevant flag is `false`:
`automatic_partner_selection_authorized`, `true_zero_copy_claim_authorized`,
`public_speedup_claim_authorized`, `broad_rt_core_speedup_claim_authorized`,
`native_engine_customization`, `full_rtnn_paper_reproduction`,
`amd_performance_claim_authorized`, `ann_index_claim_authorized`. The
underlying `RtdlPreparedSessionCacheKey.to_metadata` and
`RtdlPreparedSessionResidencyPolicy.to_metadata` (`prepared_session_residency.py:144-157`,
`209-227`) hard-code these as read-only `False` properties (`release_authorized`,
`public_speedup_claim_authorized`, `broad_rt_core_claim_authorized`,
`true_zero_copy_claim_authorized`, `automatic_partner_selection_authorized`,
`app_specific_native_engine_logic_allowed`), so the app cannot accidentally
flip them — they are not plain dict literals a future edit could silently
change. The A5000 artifact's nested profile/policy/timing blocks repeat the
same `false` values consistently.

**Answer: yes** — all claim-boundary flags remain false, including the two
named explicitly (automatic partner/backend selection, true-zero-copy), and
the contract's own dataclasses make these flags structurally hard to
misrepresent.

### 4. Is this a safe first app-level ergonomics step, and what remains?

Yes, this is a safe, narrow step:

- It is purely additive metadata — the runner invocation, `Namespace` fields,
  `repeat`/`warmup`, and timing capture are byte-for-byte unchanged from the
  prior commit, so no benchmark numbers or behavior shift as a side effect of
  this change.
- The cache stays opt-in and caller-owned: `cache_enabled=False` is explicit
  in the policy construction, and `ExplicitPreparedSessionCache` /
  `get_or_prepare_explicit_session` (`prepared_session_residency.py:280-446`)
  require the caller to supply the cache, key, and `prepare_session` callable —
  there is no global or implicit cache anywhere in this change.
- The primitive name and cache key construction are generic and pass the
  module's own forbidden-term validation, keeping the boundary against
  app-specific native-engine logic intact.

What remains before learner-facing docs should teach this as a default idiom:

- **No live demonstration of the helper actually being invoked from an app.**
  This change only emits the *descriptive* `cache_key`/`policy` metadata; it
  does not call `get_or_prepare_explicit_session` or exercise
  `ExplicitPreparedSessionCache` end to end inside the RTNN app (or any other
  app). Before teaching this as an idiom, there should be at least one
  artifact showing a real cache hit/miss cycle (`cache_event_log` with
  `miss`/`put`/`hit`) driven from an example app, not just the static
  key/policy description.
- **No worked guidance on when reuse actually pays off.** The A5000 artifact's
  `prepare_to_hot_query_ratio` is ~12,758:1 for this row, which is a strong
  *internal* signal that prepare-once/query-many is worth doing here — but
  per the claim boundary this cannot yet be surfaced as a public speedup or
  performance recommendation. Any learner-facing doc would need a separately
  authorized, non-claim-boundary-violating way to explain *why* a user might
  want to opt into the cache.
- **Single-row evidence.** Only one scale profile
  (`rtnn_prepared_optix_scale_default_65536`) was profiled. Broader rollout
  to other RTNN modes/scales (or other benchmark apps) would need their own
  evidence before the pattern is presented as general.

## Validation

I was not able to execute the requested unittest run
(`tests.goal3880_rtnn_prepared_session_residency_metadata_test`,
`tests.goal3877_explicit_prepared_session_reuse_helper_test`,
`tests.goal3820_rtnn_prepared_optix_ranked_summary_app_mode_test`,
`tests.goal2585_rtnn_benchmark_front_door_test`) — the sandboxed shell in this
review session rejected all `python`/`py` invocations as requiring approval
that did not resolve. I instead reviewed the test source directly:
`tests/goal3880_rtnn_prepared_session_residency_metadata_test.py` asserts
exactly the metadata shape, helper name, claim-boundary flags, cache-key
fields, and A5000 artifact contents described above, and its assertions match
what is present in both the app source and the artifact files I read. This is
static-analysis confirmation, not a fresh test run — a maintainer with shell
access should still execute the listed `unittest` invocation before merging
any follow-on work that builds on this metadata.

## Conclusion

**accept.** The change is a narrow, additive, generic metadata exposure that
does not alter runner behavior, keeps the cache explicit/opt-in/caller-owned,
and keeps every claim-boundary flag (including automatic partner/backend
selection and true-zero-copy) hard-coded to `false` at the dataclass level.
The A5000 evidence is internally consistent with the source. This review does
not authorize release action, public speedup wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, or app-specific
native-engine logic — those remain gated behind separate, future authorization
and additional live-usage evidence as noted above.
