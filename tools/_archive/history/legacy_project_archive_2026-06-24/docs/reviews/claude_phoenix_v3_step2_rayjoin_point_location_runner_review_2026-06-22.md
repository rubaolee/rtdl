# Claude External Review: Phoenix V3 Step 2 RayJoin Point-Location Runner

Date: 2026-06-22
Reviewer: Claude
Status: recorded external review; non-authorizing

## Verdict

`step2_rayjoin_runner_executes_structural_only_not_material_not_release`

The packet produces clean structural evidence that a second Set-A family can be routed through the productized runner. It does not produce material performance evidence. The status label in the report, `step2_rayjoin_runner_executes_but_not_material_not_release`, is correct.

## No-Go Interpretation

The no-go interpretation is correct and should not be softened.

Structural integrity checks pass: `runner_runtime_trunk_executes_all_samples: true`, `runner_internal_device_residency_all_samples: true`, `runner_hot_path_host_materialization_absent: true`, `same_output_contract_all_samples: true`, and `validation_exact_matches_all_samples: true`.

The performance verdict is also correct: median per-call is `0.001109093s` for the runner versus `0.001079664s` for legacy, ratio `0.9735x`. Median total-repeat is `0.055501s` versus `0.054044s`, ratio `0.9738x`. These are slightly regressive results, not a V3 performance win.

Claude's sharpening: the runner's internal device residency is real, but in this workload it is vacuous as a performance lever because the legacy path already has `candidate_download: 0.0` and native scalar-count production. There is no host-download phase for the runner to eliminate.

## Incumbent Comparison

The incumbent comparison is correct: runner versus `legacy_optix_relation_status_corrected_executor`, not Embree.

Both sides reach the same native executor through different accounting wrappers. This isolates the right question: whether the productized runner, session management, cache-key construction, and residency contracts produce a material gain on top of an already optimized executor. The answer is no.

## Disposition For RayJoin PIP Wrapper

In this PIP scalar-count wrapper form, RayJoin point-location topology stream should be stopped as a material Set-A candidate.

Reasons:

- Both routes call the same native executor: `reusable_native_executor_used: true`, `relation_status_corrected_scalar_count_executor_run`.
- The legacy path already has zero candidate download, so the runner's residency advantage has no elimination target.
- The runner's `steady_state_stream` still records `seconds: 0.0` with `no_separate_stream_phase_recorded_by_minimal_runner`; Phase 3 measured accounting is not complete.
- Process-wall overhead is material: about `2.12s` runner median versus `1.68s` legacy median. This is cold-prepare overhead rather than the hot-path metric, but it is still real deployment cost.

Correct disposition: mark this PIP scalar-count form as `structural_only`, do not count it as a Set-A performance win, and do not use it to justify moving toward all-app.

## Recommended Next Step-2 Family

Recommended next family: Barnes-Hut frontier/vector accumulation.

Reason: the next probe must exercise a workload where the runner can compress or fuse something the incumbent cannot, such as repeated host-device transfer between phases, repeated planning overhead between phases, or a continuation layer with enough work that fusing it into the runner produces measurable savings.

Precondition before pod spend: audit the Barnes-Hut incumbent path's phase timing and confirm a non-zero download, host roundtrip, materialization phase, or repeated-planning phase exists for the runner to eliminate. If the incumbent is already native-device on the dominant phase, stop before running the focused A/B.

Alternative: a redesigned RayJoin full LSI -> PIP -> overlay multi-phase pipeline could be valid, but it is more engineering work than a Barnes-Hut probe and should not reuse this single PIP scalar-count wrapper as the material candidate.

## All-App Authorization

No all-app pod run is authorized.

The current state after RTDBSCAN and RayJoin PIP is zero Set-A probes with material per-probe gain sourced from the runner. Running all-app now would likely reconfirm the blended near-parity failure and create pressure to rationalize it.

## Return Items Before Release Consideration

1. Pre-audit protocol before each Step-2 probe: confirm the incumbent has a non-zero phase the runner can eliminate.
2. At least one Set-A probe with material runner-sourced gain through the productized path.
3. A second Set-A probe with material runner-sourced gain.
4. Phase accounting upgraded from asserted to measured.
5. Residency at parity or above on control rows.
6. Set-A / Set-B classification committed before all-app.
7. Serious same-hardware all-app paired run clearing the frozen two-number bar.
8. External review of the all-app result.

## Codex Intake Note

Claude's return-item text mentions `>=1.05x` for a material focused probe in one paragraph, but the controlling Phoenix V3 release bar remains the already recorded Set-A `>=1.20x` bar in `docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`. This review does not lower the release bar.

## Explicit Non-Authorization

This review authorizes none of the following:

- Release of Phoenix V3 in any form.
- Public performance claims.
- Broad V3-over-V2.x claims.
- True zero-copy wording.
- All-app benchmark run.
- Counting the RayJoin PIP runner execution as a Set-A performance win.
- V4/embedding work under the V3 banner.
- Any softening of the `redo_required` gate based on this packet.

## Summary Judgment

The packet is well-constructed and the self-diagnosis is accurate. The no-go is correctly declared and correctly interpreted. The right move now is a pre-audit of Barnes-Hut's incumbent phase structure, followed by a Barnes-Hut focused A/B only if the pre-audit confirms a non-zero dominant phase the runner can compress. Two consecutive structural-only probes, RTDBSCAN and RayJoin PIP, signal that the runner must be pointed at workloads where the incumbent has not already eliminated the dominant phase.
