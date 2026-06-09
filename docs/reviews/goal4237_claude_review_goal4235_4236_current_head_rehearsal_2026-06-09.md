# Goal4237 Claude Review: Goal4235–4236 Current-Head Rehearsal

Date: 2026-06-09

Reviewer: Claude (Sonnet 4.6), independent read-only review

Verdict: **accept-with-boundary**

This review does not authorize release action, public speedup wording,
whole-app acceleration wording, broad RT-core wording, paper-reproduction
wording, true-zero-copy wording, automatic partner selection, AMD/HIPRT
performance wording, or app-specific native-engine logic. Those boundaries
remain open and are noted below.

---

## Scope

Files reviewed:

- `docs/reports/goal4235_current_head_rehearsal_after_measurement_closure_2026-06-09.md`
- `docs/reports/goal4235_current_head_rehearsal_rtx4000ada/current_scale_profile_packet.json`
- `docs/reports/goal4235_current_head_rehearsal_rtx4000ada/outputs/*.stdout.json` (all 10)
- `docs/reports/goal4236_major_performance_target_map_after_current_head_rehearsal_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`
- `tests/goal4235_current_head_rehearsal_after_measurement_closure_test.py`
- `tests/goal4219_major_performance_target_map_test.py`

---

## Question 1: Does Goal4235 legitimately prove 10/10 clean execution at `72690687`?

**Finding: Yes, with strong machine-readable provenance.**

The packet carries the following fields, all consistent with the narrative claim:

| Field | Value |
| --- | --- |
| `runtime_environment.source_commit` | `726906872628a68716a76603feb7f71ce3c9a966` |
| `runtime_environment.source_commit_short` | `72690687` |
| `runtime_environment.working_tree_clean` | `true` |
| `runtime_environment.git_status_short` | `[]` |
| `runtime_environment.nvidia_smi` | `NVIDIA RTX 4000 Ada Generation, 550.127.08, 20475 MiB` |
| `all_pass` | `true` |
| `json_pass_count` | `10` |
| `summary.row_count` | `10` |
| `summary.app_count` | `10` |
| `validation.status` | `accept` |
| `validation.errors` | `[]` |

All 10 rows carry `status: "pass"`, `returncode: 0`, `stdout_json_parseable: true`,
`claim_flag_violations: []`, and a non-empty file-backed stdout path. All 10 stdout
files exist as confirmed by direct file listing. The `working_tree_clean: true` and
`git_status_short: []` combination anchors the execution to a known, unmodified
source tree at the stated commit.

No internal inconsistencies were found between the packet summary, per-row fields,
and the individual stdout payload tails.

**One limitation to note:** this review verifies the internal consistency of the
artifacts as presented. It does not independently re-execute the benchmarks or
independently verify the commit hash against a remote. The provenance chain is
coherent; the chain is not independently re-derived here.

---

## Question 2: Does the packet preserve the three-tier distinction?

**Finding: Yes, the distinction is consistently preserved at every layer.**

The three tiers — (1) current-head route health, (2) measurement adequacy, and
(3) formal release/performance claims — are kept separate across the packet,
report, and test suite.

**Route health tier (Goal4235):** The report explicitly states "This is not a
release packet. It is not a public performance table." The packet summary carries
`status: "internal_scale_profile_registry_not_release_authorization"`. The timing
metric scope field is labeled `"wrapper_elapsed_sec_is_pod_budget_not_hot_path_metric"`,
distinguishing wall-clock budget from claimed hot-path performance. Short rows are
explicitly called out as `"safe_but_short"` runtime class — not public timing claims.

**Measurement adequacy tier (Goal4230):** Referenced explicitly in the Goal4236
target map as a separate closed target. The packet does not collapse
measurement-adequacy evidence into the rehearsal rows.

**Formal release tier:** The Remaining Release Gates section of the Goal4235 report
names five distinct open gates: exact public claim wording, docs audit, multi-AI
consensus, AMD/HIPRT evidence, and optional long timing. The packet does not
conflate closing the measurement floor with satisfying these gates.

The claim boundary strings are reproduced consistently and verbatim at the packet
level, per-row level, per-payload level, prepared-session residency level, and
policy sub-object level. The depth of boundary propagation into nested structures
is a structural strength of the artifact format.

---

## Question 3: Does Goal4236 update the target map honestly?

**Finding: Yes. The update is minimal, accurate, and structurally enforced.**

The `ten_app_current_route_health` target evidence_refs are updated from prior
evidence to include `Goal4235` as the last entry. The status `"done_internal_evidence"`
is correct for this tier. No other targets changed status.

The following boundaries remain explicitly unauthorized in both the Python source
and the Markdown report:

| Boundary | Enforcement |
| --- | --- |
| Release action | `release_authorized: False` on every target; `__post_init__` raises `ValueError` if set |
| Public speedup wording | `public_speedup_claim_authorized: False`; same enforcement |
| Whole-app acceleration wording | `whole_app_speedup_claim_authorized: False`; same enforcement |
| Broad RT-core wording | `broad_rt_core_claim_authorized: False`; same enforcement |
| Paper-reproduction wording | `paper_reproduction_claim_authorized: False`; same enforcement |
| True-zero-copy wording | `true_zero_copy_claim_authorized: False`; same enforcement |
| Automatic partner selection | `automatic_partner_selection_authorized: False`; same enforcement |
| AMD/HIPRT evidence | `amd_hiprt_functional_parity` target status: `"blocked_pending_hardware"` |
| App-specific engine logic | `app_specific_native_engine_logic_allowed: False`; same enforcement |

The structural enforcement in `CurrentMajorPerformanceTarget.__post_init__` is
particularly valuable: any future commit that attempts to set a claim flag true will
raise a `ValueError` at module import time, making it impossible to silently introduce
a claim-authorized target.

The `validate_current_major_performance_targets` function redundantly checks all
flags at runtime, so tests that call it will catch drift even if the dataclass
constraint were somehow bypassed.

One minor observation: `barnes_hut` uses `rt_core_accelerated: false` in partner
mode — correctly counted in `numba_required_rows` and not in `optix_required_rows`.
This is honest representation of a row that exercises Numba force computation
without RT-core acceleration in the current front-door route.

---

## Question 4: Are the tests strong enough?

**Finding: Strong for the stated concerns, with one minor coverage observation.**

**Stale commit provenance:** `test_current_head_rehearsal_is_clean_and_passes_all_rows`
checks `source_commit_short == "72690687"`, `working_tree_clean == True`, and
`git_status_short == []`. All three together make a stale-commit false pass
improbable.

**Failed rows:** The same test checks `{row["status"] for row in rows} == {"pass"}`
(all-pass set equality) and `json_pass_count == 10`, so a single failed row breaks
the test.

**Claim-boundary leakage:** `test_claim_boundaries_remain_false_in_packet_and_payloads`
uses `_forbidden_true_paths`, a recursive JSON walker that checks every key at every
nesting depth in both the packet and all 10 stdout payloads. This is the strongest
component of the test suite — it catches boundary leakage in embedded sub-objects
that per-row surface checks would miss.

**Route-policy drift:** `test_rehearsal_preserves_current_route_policy_boundaries`
checks the `numba_required_rows` set with exact equality, verifies the RayJoin
contract split explicitly (`pip_one_shot` → numba, `overlay_active_count` in
`rtdl_optix_contracts`), and checks RT-DBSCAN's `boundary_assignment_canonical_policy`
and `grouped_stream_continuation_pass_count`. These are meaningful regression guards
against route-policy drift.

**Target map:** `goal4219_major_performance_target_map_test.py` verifies the version
string, all five required statuses, evidence_refs for specific targets, and that no
target authorizes release or hidden dispatch. The check of `target_count == 8` would
catch silent removal of a target.

**Coverage observation:** There is no test that explicitly checks `returncode == 0`
for each row individually; however, `status == "pass"` in the runner protocol
encapsulates a zero return code, and the test verifies all-pass at the set level.
This is acceptable given the runner design.

A second minor observation: the test that loads stdout payloads via
`_load(ROOT / row["stdout_path"])` implicitly checks file existence for all 10
stdout files. If a stdout file were missing, the load would raise `FileNotFoundError`
and fail the test. This implicit check is sufficient but could be made explicit
for clarity.

Overall, the test suite covers the four stated concerns adequately for an internal
rehearsal packet.

---

## Question 5: What should be the next major target before a formal release packet?

**Finding: Assemble a formal release packet with exact claim wording and docs audit.**

The five open gates identified in the Goal4235 report are the correct next targets.
In priority order for a NVIDIA-only path (no new hardware required):

1. **Exact public claim wording** — no sentence in the current artifacts has been
   formally reviewed for external publication. All claim-boundary flags being false
   is a necessary condition, not a sufficient one. Specific language for speedup,
   RT-core acceleration scope, and partner dependencies needs human editorial review
   before any public surface.

2. **User-facing docs audit** — the benchmark apps produce detailed JSON output with
   internal field names and boundary strings. A docs audit would verify that no
   user-facing documentation inadvertently promotes internal status strings as
   external claims.

3. **Fresh multi-AI consensus over the exact release packet** — the current chain
   has internal reviews but the Goal4236 target map explicitly identifies this as
   required for the `major_release_candidate_packet` target. This review does not
   substitute for that consensus.

4. **AMD/HIPRT functional parity** — blocked on hardware, but must be resolved before
   any claim of multi-hardware support.

5. **Optional additional long timing** — only if a public performance table is included
   in the release. The current rehearsal timing is wrapper-wall-clock budget, not
   publication-grade hot-path evidence.

The `release_grade_long_run_packet` target (currently `needs_broader_evidence`) is
the correct entry point. Nothing in the Goal4235–4236 chain should be treated as
having advanced that target to `done_internal_evidence`.

---

## Summary

| Question | Finding |
| --- | --- |
| 1. Provenance and 10/10 execution | Accept — commit hash, clean tree, GPU identity, and row results are internally consistent |
| 2. Three-tier distinction preserved | Accept — route health, measurement adequacy, and formal release are kept separate at every layer |
| 3. Target map updated honestly | Accept — minimal correct update; all forbidden boundaries remain structurally enforced |
| 4. Test coverage | Accept — strong recursive claim scanner, explicit commit provenance checks, route-policy assertions |
| 5. Next major target | Formal release packet with exact claim wording, docs audit, and multi-AI consensus |

**Verdict: accept-with-boundary**

Goal4235 is a credible internal current-head rehearsal. Goal4236 is an honest minimal
update to the direction map. Neither goal authorizes, implies, or advances any formal
release action, public performance claim, or external publication decision. That
boundary is explicit, structurally enforced, and confirmed by this review.
