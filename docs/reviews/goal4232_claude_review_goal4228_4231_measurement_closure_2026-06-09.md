# Goal4232 Claude Review: Goal4228–4231 Measurement Closure

Date: 2026-06-09
Reviewer: Claude (independent, not the Codex author for this chain)
Verdict: **accept-with-boundary**

---

## Scope Covered

- `docs/reports/goal4228_rtdbscan_long_repeat_measurement_2026-06-09.md` and `summary.json`
- `docs/reports/goal4229_barnes_hut_force_summary_aggregate_timing_2026-06-09.md` and `summary.json`
- `docs/reports/goal4230_ten_app_measurement_adequacy_closure_2026-06-09.md`
- `docs/reports/goal4231_major_performance_target_map_after_measurement_closure_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`
- `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py`
- All four associated test files

---

## Question-by-Question Findings

### 1. Goal4228 — RT-DBSCAN hot-path measurement-floor gap

**Finding: closed legitimately, no route policy change, no overclaim.**

The run used `optix_rt_core_grouped_stream_numba_column_signature_3d` with
`boundary_assignment_canonical_policy = single_pass_candidate_root_rebased`,
`repeat = 20`, `warmup = 2`, dataset `clustered3d`, 65 536 points. The
`elapsed_sec_total = 1.743 s` clears the 1.0 s floor with margin. The canonical
policy field is identical to Goal4225: no policy drift occurred.

The `summary.json` has every authorization flag set `false`. The route-policy
claim string explicitly says "measurement-adequacy evidence only." The report
text says "not a new route promotion and not a public performance claim."

Minor observation: the Goal4228 test does not verify that the payload contains
individual per-run timing arrays and that their sum equals `elapsed_sec_total`
(the check Goal4229 performs). The current test only verifies `repeat = 20` and
`elapsed_sec_total > 1.0`. This is acceptable for a grouping-stream route where
the pod timing may be a single wall-clock segment rather than a per-iteration
array, but it is a weaker guarantee than Goal4229 provides. No action required
for internal adequacy closure; this gap should be noted if the evidence ever
supports a public timing claim.

### 2. Goal4229 — Barnes-Hut force-summary aggregate timing hardening

**Finding: correctly exposes real aggregate timing, not a proxy.**

The app at `_run_partner_exact_force_summary` now accumulates
`measured_elapsed_sec` as a tuple of `len(measured)` individual wall-clock
readings and stores:

- `prepared_force_repeat_protocol.force_kernel_runs_sec` — individual run array
- `prepared_force_repeat_protocol.force_kernel_total_sec` — exact sum
- `median_force_kernel_sec` — median of the array

The Goal4229 test verifies `sum(protocol["force_kernel_runs_sec"]) ≈ force_kernel_total_sec`
(using `assertAlmostEqual`), which is the critical anti-proxy check. The
`force_kernel_runs_sec_count = 200` and `measured_iterations = 200` are
consistent. Total is 1.729 s above the floor.

`materializes_python_force_rows = false` is correctly recorded; the summary path
avoids the Python-row materialization overhead that would distort a timing number
intended to characterize the force kernel.

The boundary string in the app ("Exact all-pairs force-vector reference path
only; this is not Barnes-Hut tree opening acceleration and not an RT-core
claim") is present in both the `full` and `force_summary` output paths.

### 3. Goal4230 — Ten-app measurement adequacy closure

**Finding: all ten promoted apps correctly show aggregate evidence above the
1.0 s floor; the table is accurately labeled and honestly hedged.**

The test reads from actual pod artifact files (not from the report text) and
asserts `> 1.0` for each app. The evidence sources span multiple prior goals and
multiple artifact structures — not all drawn from a single run or a single timing
field — which is appropriate for a closure reconciliation.

One entry warrants a note: `spatial_rayjoin` uses `wrapper_elapsed_sec` from a
representative mixed-route profile wall time rather than a dedicated
long-repeat aggregate field. The report acknowledges this explicitly ("adequate
representative mixed-route profile; contract split remains visible"). This is the
weakest entry in the table but not a defect: the profile ran 9.25 s of wall
time, far above the floor, and the report does not claim it as long-repeat
evidence. For internal measurement-adequacy closure the entry is acceptable;
a formal public performance table would need a dedicated long-repeat RayJoin
row.

The report correctly names the remaining unfinished work: docs audit, exact
public claim wording, multi-AI consensus, and AMD/HIPRT hardware evidence.

### 4. Goal4231 — Major performance target map update

**Finding: the map is honest; measurement adequacy is marked `done_internal_evidence`
while all release-gating and hardware targets are marked pending or blocked.**

The eight targets and their statuses:

| Target | Status |
| --- | --- |
| ten_app_current_route_health | `done_internal_evidence` |
| ten_app_measurement_adequacy_closure | `done_internal_evidence` |
| rayjoin_contract_split_route_policy | `done_internal_evidence` |
| rtdbscan_profile_aware_boundary_policy | `done_internal_evidence` |
| prepared_session_residency_surface | `available_explicit_not_default` |
| release_grade_long_run_packet | `needs_broader_evidence` |
| amd_hiprt_functional_parity | `blocked_pending_hardware` |
| major_release_candidate_packet | `pending_user_release_decision` |

All five required status categories are present. The `CurrentMajorPerformanceTarget`
dataclass enforces boundary flags at construction time: it raises `ValueError` if
any authorization flag is `True`. This is an unusually strong structural
guarantee; a careless edit that sets any auth flag to `True` will fail at
import time. The validator confirms the same at runtime. The test
`test_no_target_authorizes_release_or_hidden_dispatch` sweeps all eight rows
against all eight boundary flags.

The evidence refs for `ten_app_measurement_adequacy_closure` correctly include
`Goal4228` and `Goal4229` among the seven cited goals.

### 5. Test adequacy for measurement-floor regressions and claim-boundary leakage

**Finding: tests are solid; one minor structural gap noted.**

Strengths:
- Goal4228 test checks the canonical policy string, repeat/warmup counts, the
  `hot_path_duration_target_met` flag, total time `> 1.0`, all eight auth flags
  `False`, and the report text phrase.
- Goal4229 test verifies the per-run array length, the sum-equals-total
  invariant, the `materializes_python_force_rows = false` flag, all auth flags,
  and the report text phrase.
- Goal4230 test reads from the actual pod artifacts (not report prose), verifying
  every app has evidence `> 1.0 s`, and checks four specific boundary phrases in
  the report.
- Goal4219/4231 test validates the structured API, checks all five required
  status categories, checks specific `evidence_refs` values, and asserts all
  eight boundary flags are `False` across all eight rows.

Gap: Goal4228 has no per-run array sum check. If future runs of RT-DBSCAN
expose individual iteration timings, the test should be extended to mirror
Goal4229's `assertAlmostEqual(total, sum(runs))` pattern.

### 6. Next major engineering target before any user-requested formal release packet

The target map is clear on this. The most critical next step is assembling a
formal release packet if the user decides to proceed toward release. That packet
requires:

1. **Exact public claim wording** — no public speedup, whole-app, broad RT-core,
   paper-reproduction, or AMD performance wording is authorized yet.
2. **Docs audit** — all user-facing documentation must be reviewed against the
   claim boundary before any release.
3. **Fresh multi-AI release consensus** — the current evidence is strong for
   internal readiness; a formal release requires a separate consensus pass over
   the exact release claims.
4. **AMD/HIPRT functional and timing evidence** — blocked on AMD hardware; no
   AMD performance wording may appear before this gate clears.

The `release_grade_long_run_packet` target has `pod_needed_next = True` and
`needs_broader_evidence` status. Additional long timing rows (if needed for a
public performance table) belong there, not in the current measurement-adequacy
chain.

---

## Summary Assessment

The Goal4228–4231 chain correctly closes the internal measurement-adequacy floor
for all ten promoted benchmark apps, hardens the Barnes-Hut aggregate timing
contract with real per-iteration arrays, and updates the major performance target
map to reflect exactly what is and is not closed. No route policy was changed,
no authorization flag was set, and the structural enforcement in
`CurrentMajorPerformanceTarget` makes boundary drift detectable at import time.

The tests are well-targeted with one minor gap (Goal4228 lacks the per-run sum
check that Goal4229 applies). The `spatial_rayjoin` entry in Goal4230 uses a
profile wall time rather than a dedicated long-repeat aggregate, which is
acceptable for internal closure but noted for the record.

No defect requires rejection or an additional evidence round. The remaining
unfinished gates (release wording, docs audit, multi-AI consensus, AMD hardware)
are all explicitly captured in the target map with correct statuses.

**Verdict: accept-with-boundary**

This review authorizes the Goal4228–4231 chain as internal measurement-readiness
evidence only. It does not authorize release action, public speedup wording,
whole-app acceleration wording, broad RT-core wording, paper-reproduction
wording, true-zero-copy wording, automatic partner selection, AMD performance
wording, or app-specific native-engine logic.
