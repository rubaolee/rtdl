# Review: Goal2907–2912 Scaled v2.5 Performance Packet

Date: 2026-06-01
Reviewer: Claude (independent read-only)
Verdict: `accept-with-boundary`
Handoff: `docs/handoff/HANDOFF_CLAUDE_GOAL2912_SCALED_V2_5_PACKET_REVIEW_2026-05-31.md`

## Scope

This review covers the performance hardening chain from Goal2907 through Goal2912 and answers the five questions in the handoff. Files reviewed: six chain reports, two key pod artifact directories, two harness scripts, the triage script, `v2_5_internal_readiness.py`, and four test modules.

---

## Fact Verification

All facts stated in the handoff were verified against the raw artifacts.

| Fact | Verified | Source |
| --- | --- | --- |
| Packet commit `cf3a479d...` | pass | `goal2855_summary.json` `source_commit` field and all 7 per-app artifacts |
| `all_pass: true`, `artifact_count: 7` | pass | `goal2855_summary.json` |
| `source_dirty: []` | pass | `goal2855_summary.json` `runner_metadata.source_dirty` and each artifact |
| `claim_boundary_violations: {}` | pass | `goal2855_summary.json` and triage |
| Triage `performance_targets: []`, `top_priority: null` | pass | `goal2912_current_packet_scaled_defaults_triage_2026-05-31.json` |
| RTNN defaults: 65,536 points, repeat 9 | pass | `goal2800_rtnn_v25_live_ranked_summary_harness.py` `DEFAULT_POINT_COUNT` / `DEFAULT_REPEAT` |
| Hausdorff defaults: 8,192 × 8,192, repeat 9 | pass | `goal2801_hausdorff_xhd_v25_canonical_entrypoint.py` `DEFAULT_POINTS_A/B` / `DEFAULT_REPEAT` |
| RTNN ratios: uniform 1.150x, clustered 2.522x, shell 7.640x | pass | Triage `min_cupy_over_rtdl_ratio: 1.15`, `max: 7.64`; packet report text exact match |
| Hausdorff RTDL/CuPy ratio 0.940x | pass | Triage `rtdl_over_cupy_ratio: 0.94`; computed from `rtdl_median_sec: 0.007801 / cupy_median_sec: 0.008301` |
| RT-DBSCAN 4.166x–4.857x vs prepared CuPy grid | pass | Triage `min_speedup_vs_prepared_cupy_grid: 4.166`, `max: 4.857` |
| Barnes-Hut Torch selected, Triton unpromoted, OptiX 154.306x | pass | Triage `selected_vector_sum_partner: torch`, `triton_over_torch_vector_sum_ratio: 4.265`, `max_optix_membership_speedup_vs_embree: 154.306` |
| Chain does not claim release/public/broad-RT/whole-app/zero-copy/package/Triton-auto/paper | pass | Every report Boundary section; `v2_5_internal_readiness.py` `claim_authorization` all-False; `CLAIM_BOUNDARY` dicts in both harnesses |

One secondary observation: the Goal2911 scale-probe artifact records harness version `v6.repeat9_stability`, while the current harness file is `v7.scale65536_repeat9`. This reflects the expected sequence: probe at an intermediate commit establishes the concept; the v7 harness encodes the validated defaults in the final commit. Not a correctness issue.

---

## Review Question 1: Is the Scale Move Benchmark Stabilization or Metric Gaming?

**Finding: stabilization, not gaming.**

The justification is technically coherent on three independent grounds.

First, absolute timing at the old defaults was too short for a 3-run median to be reliable. At 4K×4K, Hausdorff ran in roughly 4.5 ms; one outlier sample in a 3-run set could shift the reported ratio by 30–40%. At 32K points, the RTNN uniform row ran in roughly 80–100 microseconds; a single warm-up artifact could dominate. The 9-sample run vectors in `hausdorff_8192_repeat9.json` show exactly this: the first run is 0.009358 s while the stable runs cluster at 0.007668–0.008716 s. Without a larger repeat count the first-run cost contaminates the median.

Second, the new ratios are not flattering to RTDL. Hausdorff at 8K×8K runs at 0.9995x RTDL/CuPy in the Goal2911 probe and 0.940x in the Goal2912 packet — RTDL is slightly faster, but near parity. If gaming were the intent a scale that produced a more decisive RTDL win would have been chosen. The RTNN uniform row at 65K produces only 1.030x (probe) to 1.150x (packet) CuPy/RTDL — still marginal, still susceptible to jitter. A gaming choice would have been a clustered or shell workload at a size where RTDL dominates clearly.

Third, the changes are generic harness parameters (point counts and repeat counts), not algorithm-specific adaptations. No workload type was changed, no input distribution was replaced, and no sampling strategy was modified to favor RTDL.

Residual concern: the RTNN uniform row at 65K still runs in approximately 136 microseconds median. Even with 9 repeats this remains a very short measurement. The 1.030–1.150x run-to-run spread between the probe and the packet confirms that this row still carries non-trivial relative uncertainty. It passes the green threshold but is not a stable point estimate.

---

## Review Question 2: Does the Evidence Support "No Active Performance Targets"?

**Finding: yes, with the near-parity classification rule understood.**

The triage script (`goal2902_v2_5_current_packet_perf_triage.py`) classifies RTNN rows with `0.95 <= cupy_over_rtdl < 1.0` as `current_path_acceptable_near_parity_distribution_dependent`, not as `performance_target`. Rows below 0.95 remain `performance_target`. This gate is conservative: a sub-5% distribution-dependent wobble is recorded but not promoted to a design blocker, while any material same-contract regression still triggers a target. The threshold is hard-coded at 0.95 and is not app-specific.

In the Goal2912 packet, the RTNN triage entry shows `near_parity_distributions: []` and `weak_distributions: []`. All three distributions clear the near-parity floor with margin: minimum ratio is 1.15x. The claim of zero active targets is accurate at the packet scale and the stated threshold.

The progression from Goal2906 through Goal2912 provides a clean audit trail. The two targets that appeared — Hausdorff at 1.401x (Goal2906, repeat-3 artifact) and RTNN clustered at 0.945x (Goal2908, repeat-3 artifact) — were each falsified by targeted repeat-9 re-probes at the same source commit and same input, not by changing the algorithm or the input size first. Only after the repeat-9 probes confirmed that both were measurement artifacts did the scale change follow. This ordering is important: stabilization preceded the scale move; it was not used to explain away a genuine regression.

---

## Review Question 3: Do Code Changes Add App-Specific Native Engine Logic?

**Finding: no.**

All four source files reviewed show only two categories of change:

1. **Harness parameter defaults** (`DEFAULT_POINT_COUNT`, `DEFAULT_POINTS_A/B`, `DEFAULT_REPEAT`): numeric constants in the benchmark harnesses, not engine code.
2. **Triage classification logic** (near-parity band in `_rtnn()`): a reporting rule applied generically across distributions; no app-specific branching.

Both harnesses maintain `"native_engine_customization": False` in their `CLAIM_BOUNDARY` dicts. The `goal2855_summary.json` artifact confirms `"native_engine_customization": false` for all seven apps in the packet. No import of new native modules, no addition of RTDL-internal dispatch paths, no app-facing bypass of the generic front-door layer.

The `v2_5_internal_readiness.py` file adds references to Goal2907–2912 in the required reports list and the allowed-next-actions list. These are index entries only; no engine logic changed.

All four reviewed test modules test harness defaults, pod artifact pass/fail status, and report text for boundary markers. No test was written to skip or soften an engine constraint.

---

## Review Question 4: Does Report Language Avoid Overclaiming?

**Finding: yes, consistently.**

Every report in the chain (Goal2906 through Goal2912) carries an identical "Boundary" section that denies: release consensus, v2.5 release authorization, public speedup claims, broad RT-core claims, whole-app speedup claims, true-zero-copy claims, automatic Triton selection, package-install claims, and paper-reproduction claims.

The machine-readable artifacts reinforce this:

- `goal2855_summary.json`: `"v2_5_release_authorized": false`, `"public_speedup_claim_authorized": false`, `"whole_app_speedup_claim_authorized": false`, `"true_zero_copy_claim_authorized": false`, `"broad_rt_core_speedup_claim_authorized": false`, `"paper_reproduction_claim_authorized": false`
- `goal2912_current_packet_scaled_defaults_triage_2026-05-31.json`: `"release_authorized": false`, `"public_speedup_claim_authorized": false`, `"whole_app_speedup_claim_authorized": false`, `"true_zero_copy_claim_authorized": false`, `"paper_reproduction_claim_authorized": false`
- Per-app artifact boundaries: every artifact shows `"native_engine_customization": false`

The `v2_5_internal_readiness.py` module hardcodes `V2_5_INTERNAL_READINESS_STATUS = "internal_evidence_packet_coherent_not_release_ready"` and the `claim_authorization` block has nine keys, all `False`. The validate function checks each of these programmatically and would reject the packet if any flipped to `True`.

No report in the chain uses the phrases "beats," "superior," or "ready for release." The language consistently uses "near parity," "current path acceptable," and "internal evidence."

---

## Review Question 5: Residual Risks Before Any v2.5 Release Packet or Public Claim

The following items are open as of Goal2912.

**1. RTNN uniform row absolute timing too short for a stable public benchmark.**
At 65K points and repeat-9, the uniform RTNN row runs in roughly 136 microseconds. The 1.030x result in the Goal2911 probe vs. 1.150x in the Goal2912 packet illustrates that run-to-run variation is still on the order of 10%. This is acceptable for an internal gate but would require a larger workload or a qualification note for any public performance claim.

**2. Hausdorff near-parity band margin is thin.**
At 0.940x RTDL/CuPy the current result is inside the 1.10x near-parity limit with 16% margin. Any GPU driver update, kernel recompile, or workload size change that shifts the ratio past 1.10x would reopen a performance target. This does not need to be fixed now, but the near-parity gate must be re-run before any public claim.

**3. RayJoin row/overlay continuation explicitly deferred.**
The spatial RayJoin entry carries status `current_path_acceptable_but_rows_overlay_deferred`. The packet passes only the count/parity route. Row and overlay device continuation is noted as future work. This is not suitable as a release claim boundary for the full RayJoin problem.

**4. Contact manifold and robot collision are Tier C only.**
These two apps are not in the seven-app packet. They carry `tier_c_no_regression` status. No partner performance characterization has been done for them.

**5. Barnes-Hut Triton vector sum is 4.265x slower than Torch.**
Triton remains a visible preview path, not an auto-selected partner. Until Triton wins on the same-contract timing test, Torch must remain the selected partner. The `triton_vector_sum_auto_selection_authorized: false` boundary must remain in place.

**6. Multi-vendor and second-architecture coverage not yet completed.**
The `v2_5_internal_readiness.py` `allowed_next_actions` list includes `track_goal2897_multivendor_or_second_arch_perf_check_before_release_packet`. No evidence of multi-vendor results appears in this chain.

**7. Compiler flag alignment pre-release check.**
Similarly, `track_goal2897_compiler_flag_alignment_before_release_packet` is listed as an open item.

**8. Fresh 3AI external review required for any release packet.**
The `allowed_next_actions` list specifies `request_fresh_3ai_release_review_only_if_user_requests_release`. The current chain is an internal hardening chain. A release packet would require its own external review cycle.

---

## Code-Level Observations

No bugs were found. A few minor observations:

- The `_median_or_elapsed` helper in the RTNN harness correctly implements a sorted-rank median for both even and odd run counts. This is correct.
- The `_median_by_elapsed` helper in the Hausdorff entrypoint uses `ordered[len(ordered) // 2]` which picks the upper-middle element for even counts. For `repeat=9` (odd count) this is exact. For even repeat counts it would select the upper median rather than averaging, a minor asymmetry that does not affect the current runs.
- The Hausdorff entrypoint records `median_elapsed_sec` separately from `elapsed_sec` (which is the actual median-selected run's elapsed time). Both are consistent in the artifacts reviewed.
- The triage script's `_rtnn` function correctly handles the case where `near_parity` is populated but `weak` is empty: it returns `current_path_acceptable_near_parity_distribution_dependent`. In the Goal2912 packet, neither list is populated, so the function returns `current_path_acceptable`. Logic is correct.

---

## Summary

The Goal2907–2912 chain is internally coherent. The move from repeat-3 short-row measurements to repeat-9 measurements at larger canonical sizes is technically justified as benchmark stabilization. The evidence that both the Hausdorff and RTNN targets were measurement artifacts (not primitive regressions) is present and adequately documented through targeted re-probes at identical source commits and inputs. No app-specific native engine logic was added. Report language consistently maintains all claim boundaries. The packet commit is clean, all seven artifacts pass, and the triage shows no active performance targets.

**Verdict: `accept-with-boundary`**

The packet is accepted as the current internal v2.5 performance posture. The boundary is that this is not a release authorization and not a public-speedup-claim authorization. The items listed under Review Question 5 must be addressed before any release packet or public claim is prepared.
