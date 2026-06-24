# Goal4246 Claude Review: Goal4243-4245 Short-Row Refresh Chain

Date: 2026-06-09
Reviewer: Claude (independent read-only review)
Verdict: **accept-with-boundary**
Internal-only: **yes — this evidence chain does not authorize release or public claims**

---

## Scope

This review covers Goals 4243, 4244, and 4245 as a unit: the short-row
long-repeat refresh, the updated major performance target map, and the two
minor hardening items carried forward from the Goal4241 review of the RayJoin
long-repeat packet.

---

## Question 1: Does Goal4243 legitimately refresh the former short rows?

**Yes.**

The summary artifact (`goal4243_short_row_long_repeat_refresh_rtx4000ada/summary.json`) records:

| Field | Value |
| --- | --- |
| `source_commit_short` | `9a40f7f5` |
| `pre_artifact_worktree_clean` | `true` |
| `pre_artifact_git_status_short` | `""` (empty) |
| GPU | `NVIDIA RTX 4000 Ada Generation, 550.127.08, 20475 MiB` |

All three short rows now have second-level aggregate timing independent of the older
Goal4185/4186 stress artifacts:

| App | Metric | Repeat | Aggregate | Correctness |
| --- | --- | ---: | ---: | --- |
| `hausdorff_xhd` | `repeat_protocol.measured_query_total_sec` | 1500 | 13.05 s | `matches_oracle: true`, RT-core active |
| `contact_manifold` | `native_collect_total_sec` | 50000 | 10.33 s | `matches_cpu_reference: true`, `overflowed: false` |
| `triangle_counting` | `timing_ms.run_backend / 1000` | 10000 | 2.10 s | `triangle_count_matches_oracle: true`, RT-core active |

Cross-checking the individual stdout files confirms the summary is consistent:
- `goal4243_hausdorff.stdout.json`: `repeat_protocol.measured_query_total_sec = 13.046773...`, `rt_core_accelerated: true`, `matches_oracle: true`
- `goal4243_contact_manifold.stdout.json`: `native_collect_total_sec = 10.326223...`, `matches_cpu_reference: true`, `overflowed: false`
- `goal4243_triangle_counting.stdout.json`: `timing_ms.run_backend = 2100.0807...`, `triangle_count_matches_oracle: true`, `rt_core_accelerated: true`

The test file (`tests/goal4243_short_row_long_repeat_refresh_test.py`) asserts clean provenance
(`source_commit_short == "9a40f7f5"`, clean worktree), presence of all three stdout files,
second-level aggregate thresholds (Hausdorff and contact > 10 s, triangle > 1 s), and a full
forbidden-true scan over summary and all three stdout files. All assertions are tightly matched
to the actual artifact values. **No issues found.**

---

## Question 2: Do the three rows preserve their scoped meanings?

**Yes, no overclaiming detected.**

**Hausdorff.** The stdout shows `optix_summary_mode: "directed_threshold_prepared"` and the
`rtdl_role` field explicitly states: "RTDL/optix uses prepared fixed-radius threshold traversal
to answer the Hausdorff decision subproblem: every source point has at least one target within
the threshold." The mode is a threshold decision (is Hausdorff ≤ radius?), not a universal
exact-distance computation. `broad_rt_core_speedup_claim_authorized: false` is present in the
claim_boundary object. The report's boundary section correctly states "not a universal exact
Hausdorff speedup claim."

**Contact manifold.** The stdout's claim_boundary string reads: "Native mode validates only the
generic app-name-free COLLECT_K_BOUNDED i64 collector over Python oracle rows; it is not native
collision/contact logic." The 50k-repeat run exercises bounded collect-k candidate output,
not full physics integration. No `public_speedup_claim_authorized` key appears in the file at all.

**Triangle counting.** The stdout has `paper_reproduction: false`, `authors_code_reproduction:
false`, `generic_ray_triangle_rt_core_subpath_authorized: true` in the claim_boundary object.
The contract field is `"rt_graph_2a1_mapped_to_generic_ray_triangle_any_hit"` and the mode is
`"rt_graph_2a1_generic_rt"` — scoped to the generic RT-Graph 2A1 summary route, not the full
paper system. `whole_app_speedup_claim_authorized: false` and `public_speedup_claim_authorized:
false` are both present and false.

The Goal4243 report's Boundary section enumerates all prohibited claim types explicitly. **No
scope creep detected.**

---

## Question 3: Does Goal4244 update the target map honestly?

**Yes.**

`src/rtdsl/current_major_performance_targets.py` shows:

- Version string: `rtdl.v2_10.current_major_performance_targets.goal4244.v1`
- Module-level status constant: `internal_direction_map_not_release_authorization`
- `CurrentMajorPerformanceTarget.__post_init__` enforces that all nine authorization flags
  (`release_authorized`, `public_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`,
  `broad_rt_core_claim_authorized`, `paper_reproduction_claim_authorized`,
  `rtdl_beats_rayjoin_claim_authorized`, `true_zero_copy_claim_authorized`,
  `automatic_partner_selection_authorized`, `app_specific_native_engine_logic_allowed`) remain
  false at construction time — any True value raises `ValueError`.
- `summarize_current_major_performance_targets` hard-codes all nine flags False in its return dict.
- `validate_current_major_performance_targets` performs a per-row check for each flag.

The `release_grade_long_run_packet` target retains `status: "needs_broader_evidence"` and its
`current_reading` explicitly states "This is still not a formal public release matrix across
claim wording, docs, consensus, and hardware classes." This is honest.

Goal4243 is incorporated into `ten_app_measurement_adequacy_closure` and
`release_grade_long_run_packet` evidence_refs. Goal4239 is included in
`rayjoin_contract_split_route_policy` and `release_grade_long_run_packet`.

The test file (`tests/goal4219_major_performance_target_map_test.py`) asserts:
- `rt.CURRENT_MAJOR_PERFORMANCE_TARGET_VERSION == "rtdl.v2_10.current_major_performance_targets.goal4244.v1"`
- `target_count == 8`
- All five required status values present
- `Goal4243` in measurement closure evidence refs
- No target authorizes release or hidden dispatch (iterating all rows, checking all nine flags)

**No release authorization leak found.**

---

## Question 4: Does Goal4245 correctly resolve the two Goal4241 findings?

**Yes, both findings are fully resolved.**

**Finding 1 — `wrapper_elapsed_sec > 20.0` for RayJoin.**
`tests/goal4239_rayjoin_dedicated_long_repeat_profile_test.py` line 67:
```python
self.assertGreater(payload["wrapper_elapsed_sec"], 20.0)
```
This was previously `> 10.0`. The RayJoin long-repeat artifact recorded 20.76 s, so the test
threshold is now tightly matched to the actual evidence. The test also separately verifies that
`scale_runner_elapsed_sec_is_not_hot_path_metric: true` and
`metric_scope == "per_contract_hot_medians_not_wrapper_wall_time"`, preventing the wrapper
wall-time from being misread as a hot-path speed figure.

**Finding 2 — `rtdl_beats_rayjoin_claim_authorized` structural guard.**
`src/rtdsl/current_major_performance_targets.py`:
- Field present in the frozen dataclass (line 44): `rtdl_beats_rayjoin_claim_authorized: bool = False`
- In the `__post_init__` rejection loop (enforces `False` at construction)
- In `to_metadata()` output (line 89)
- In `summarize_current_major_performance_targets` hard-coded False (line 270)
- In `validate_current_major_performance_targets` per-row check (line 309)

The test asserts it per row at line 66:
```python
self.assertFalse(row["rtdl_beats_rayjoin_claim_authorized"], row["target_id"])
```

Both findings are structurally locked out, not merely documented. **Fully resolved.**

The validation run reported in Goal4245 (`Ran 19 tests ... OK` across five test modules) is
consistent with the test code reviewed here.

---

## Question 5: What remains before a formal release packet?

The target map documents three open gates, none of which this chain attempts to close:

1. **`release_grade_long_run_packet` (`needs_broader_evidence`)** — requires exact public claim
   wording, docs audit, and multi-AI release consensus over the specific claims. Current NVIDIA
   evidence is stronger after Goal4243, but this is a quality gate on what is said publicly, not
   just on what runs.

2. **`amd_hiprt_functional_parity` (`blocked_pending_hardware`)** — AMD/HIPRT functional and
   timing evidence still requires actual AMD GPU hardware. No emulation or proxy is available.

3. **`major_release_candidate_packet` (`pending_user_release_decision`)** — a formal major release
   needs a user-requested release packet, cleaned docs, and multi-AI consensus over the exact
   release claims. This is gated by user intent, not just evidence state.

Additionally, the contact manifold stdout file (1.3 MB) contains a large
`candidate_id_rows` array. This is an artifact of the 50k-repeat design storing per-run
candidate IDs and inflates the file substantially. It does not affect correctness or
claim boundary; the key timing and correctness fields were verified by targeted grep. However,
for future packets it may be worth suppressing verbose intermediate rows to keep artifact
sizes manageable.

---

## Summary of Findings

| Finding | Severity | Notes |
| --- | --- | --- |
| Provenance clean (correct commit, clean worktree) | pass | Confirmed in summary.json |
| All three rows above one-second floor | pass | Hausdorff 13.05 s, contact 10.33 s, triangle 2.10 s |
| Hausdorff scoped to threshold decision, not exact speedup | pass | stdout confirms directed_threshold_prepared mode |
| Contact manifold scoped to COLLECT_K_BOUNDED, not full physics | pass | claim_boundary string confirmed |
| Triangle counting scoped to RT-Graph 2A1 generic route, not paper | pass | paper_reproduction: false confirmed |
| Goal4244 target map: no release or claim authorization leak | pass | Enforced structurally in dataclass and validate fn |
| Goal4245 Fix 1: wrapper_elapsed_sec > 20.0 | pass | Line 67 of goal4239 test confirmed |
| Goal4245 Fix 2: rtdl_beats_rayjoin_claim_authorized structural guard | pass | Field, __post_init__, metadata, summarize, validate all updated |
| Three release gates still open | noted | Expected; not the scope of this chain |
| Large contact_manifold artifact (1.3 MB) | minor | Does not affect correctness; cosmetic suggestion only |

---

## Verdict

**accept-with-boundary**

The Goal4243-4245 chain legitimately refreshes the three former short rows at the correct
source commit with dedicated long-repeat evidence, preserves all claim scope limitations, and
structurally resolves both Goal4241 hardening findings. The target map update is honest and
does not advance any release gate. All evidence in this chain is **internal-only** and does
not authorize release, public speedup claims, whole-app acceleration claims, RayJoin
paper-reproduction claims, RTDL-beats-RayJoin claims, or AMD performance claims.
