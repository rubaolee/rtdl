# Goal4241 Claude Review: Goal4239–4240 RayJoin Long-Repeat Evidence Chain

Date: 2026-06-09
Reviewer: Claude (Sonnet 4.6, independent read-only)
Verdict: **accept-with-boundary**
Evidence status: **internal-only**

---

## 1. Does Goal4239 legitimately close the RayJoin dedicated long-repeat evidence gap?

**Yes, with one minor threshold note.**

The payload (`rayjoin_long_repeat.stdout.json`) satisfies every criterion for a clean, representative long-repeat run:

| Criterion | Required | Observed | Pass |
| --- | --- | --- | --- |
| Clean pod | `git_status_short == ""` | `""` | ✓ |
| Source commit | matches report | `048d940c86ffa6f7dd39db6c7bb16666cd0c9e21` | ✓ |
| GPU | RTX 4000 Ada, current driver | `NVIDIA RTX 4000 Ada Generation, 550.127.08` | ✓ |
| Wrapper elapsed | > 10 s (report claims 20+ s) | `20.758 s` | ✓ |
| Repeat count | large (report says 200) | `200` | ✓ |
| Warmup count | present | `20` | ✓ |
| All counts match | `true` | `true` | ✓ |
| Data source | bounded public-CDB slices | county/soil `start256_count512` | ✓ |
| Mixed-route | four contracts covered | pip, pip-batch, lsi, overlay | ✓ |
| Schema | recognized | `rtdl.goal3866.rayjoin_representative_scale_profile.v1` | ✓ |

**Minor threshold note:** The test asserts `wrapper_elapsed_sec > 10.0`, but the report claims a "20+ second" run. A future regression to, say, 15 seconds would still pass the test while failing the stated standard. Tightening the floor to `> 20.0` would close this gap and make the test self-consistent with the report.

The run clearly supersedes the Goal4230 representative row by providing a dedicated, per-contract long-repeat profile at a 200-repeat depth, which the earlier closure lacked.

---

## 2. Does the report preserve the four-way contract split?

**Yes, cleanly.**

All four contracts are present and correctly attributed:

| Contract | Recommended route | Key metric | Direction |
| --- | --- | --- | --- |
| PIP one-shot | `numba_cuda_jit_scalar_count` | RTDL/OptiX `0.245x` vs Numba | Numba wins; RTDL/OptiX slower at this bounded one-shot slice |
| PIP repeated requests | `rtdl_optix_prepared_batch_executor` | per-request speedup `1.234x` vs single | throughput evidence, not one-shot latency |
| LSI scalar count | `rtdl_optix_prepared_segment_pair_count` | `262.8x` faster than Numba | RTDL/OptiX wins strongly |
| Overlay active count | `rtdl_optix_prepared_shape_pair_active_count` | `213.3x` faster than Numba | RTDL/OptiX wins strongly |

The JSON explicitly records:
- `"automatic_dispatch": false`
- `"user_route_choice_visible": true`
- `"throughput_evidence_not_one_shot_latency": true` on the batch executor entry

The route split is internally consistent between the JSON, the markdown report, and the `current_major_performance_targets.py` entry for `rayjoin_contract_split_route_policy`.

One observation: the PIP repeated-requests speedup of `1.234x` per-request vs single-request is modest. The JSON correctly labels it throughput evidence rather than a one-shot latency win, and the test only asserts `> 1.0`. This is appropriate framing. A future profile with a larger batch request count could either strengthen or weaken this ratio, and that would be informative rather than problematic given the current honest labeling.

---

## 3. Does Goal4240 update the target map honestly without authorizing premature claims?

**Yes. The boundary is tight.**

Checked all nine prohibited wording categories against both the markdown report and the `current_major_performance_targets.py` dataclass:

| Prohibited category | Report | Python flags | Status |
| --- | --- | --- | --- |
| Release action | "does not authorize release action" | `release_authorized=False` enforced by `__post_init__` | ✓ blocked |
| Public speedup wording | not present | `public_speedup_claim_authorized=False` | ✓ blocked |
| Whole-app acceleration | not present | `whole_app_speedup_claim_authorized=False` | ✓ blocked |
| Broad RT-core wording | not present | `broad_rt_core_claim_authorized=False` | ✓ blocked |
| RayJoin paper-reproduction | not present | `paper_reproduction_claim_authorized=False` | ✓ blocked |
| RTDL-beats-RayJoin | not present | *(no such flag in Python, banned by label)* | ✓ blocked in JSON |
| True-zero-copy | not present | `true_zero_copy_claim_authorized=False` | ✓ blocked |
| Automatic partner selection | not present | `automatic_partner_selection_authorized=False` | ✓ blocked |
| AMD performance wording | not present | `amd_hardware_needed=True` only on the AMD target | ✓ blocked |
| App-specific native-engine logic | not present | `app_specific_native_engine_logic_allowed=False` | ✓ blocked |

The `__post_init__` validator in `CurrentMajorPerformanceTarget` raises `ValueError` if any of these flags is set to `True`, making boundary enforcement structural rather than documentary. The `validate_current_major_performance_targets` function propagates this at the map level.

The two targets that matter most for release gating both carry the correct non-authorizing statuses:
- `release_grade_long_run_packet`: `needs_broader_evidence`
- `major_release_candidate_packet`: `pending_user_release_decision`

The Goal4239 citation in `rayjoin_contract_split_route_policy` and `release_grade_long_run_packet` is accurate and does not overstate its contribution.

---

## 4. Are the tests sufficient to catch route collapse, claim-boundary leakage, and stale provenance?

**Largely yes, with two minor gaps.**

**Coverage that works:**

- `test_long_repeat_payload_has_clean_provenance_and_counts`: verifies schema string, 8-char commit prefix, clean `git_status_short`, GPU substring, repeat/warmup counts, elapsed floor, and `all_counts_match`. Correctly treats wrapper elapsed as a quality gate, not a hot-path metric.
- `test_route_split_remains_visible_and_stable`: asserts `automatic_dispatch == False`, `user_route_choice_visible == True`, exact lists of Numba and RTDL/OptiX contracts, `pip_one_shot.rtdl_optix_speedup_vs_numba < 1.0` (catches a route collapse where RTDL/OptiX wrongly wins the one-shot), and `> 100x` floors on LSI and overlay (catches a regression where the speedup drops to a single digit).
- `test_claim_boundaries_remain_closed`: JSON-wide recursive scan for any of 17 named flags set to `True`. Also checks four required text phrases in the markdown report. This is the strongest leakage guard in the suite.
- `goal4219` `test_no_target_authorizes_release_or_hidden_dispatch`: redundant flag check across the entire target map Python API, which catches any regression introduced through the module's `to_metadata()` path.

**Gap 1 — elapsed floor:** `wrapper_elapsed_sec > 10.0` in `test_long_repeat_payload_has_clean_provenance_and_counts` is weaker than the report's "20+ second" claim. This should be `> 20.0`.

**Gap 2 — `rtdl_beats_rayjoin` missing from Python flag set:** The JSON `claim_boundary` object carries `"rtdl_beats_rayjoin_claim_authorized": false` and the test's `FORBIDDEN_TRUE_FLAGS` set includes `"rtdl_beats_rayjoin_claim_authorized"`. However, the `CurrentMajorPerformanceTarget` dataclass does not include a `rtdl_beats_rayjoin_claim_authorized` field with structural enforcement. The protection currently rests on the JSON-scan test alone. If a future target map entry were constructed directly via the Python API (bypassing JSON), this specific flag would have no structural guard. Low risk in the current codebase, but worth noting.

Both gaps are minor; neither enables a false pass that would admit an actual boundary violation through the current artifacts.

---

## 5. What should be the next major target before any formal release packet?

The target map correctly identifies two remaining hard gates:

**Immediate internal gate:** Assemble the `release_grade_long_run_packet`. This requires:
1. Exact public claim wording drafted and reviewed (not just directional reading),
2. Docs audit confirming no claim-boundary language has leaked into user-facing documentation,
3. Fresh multi-AI consensus over the exact release claims (not this internal evidence chain),
4. Hardware table: the current evidence covers RTX 4000 Ada only. A formal public release table requires either a statement that NVIDIA OptiX is the only supported backend, or additional GPU rows.

**Parallel hardware gate:** AMD/HIPRT functional parity (`blocked_pending_hardware`). This cannot be unblocked without real AMD hardware. It need not block an NVIDIA-scoped release, but the release packet must explicitly scope claims to NVIDIA hardware and not imply AMD equivalence.

The `major_release_candidate_packet` target (`pending_user_release_decision`) is correctly positioned as the final gate requiring explicit user request. No evidence in this chain advances toward that gate on its own.

---

## Summary

Goal4239 cleanly closes the long-repeat evidence gap with a 20.76-second, 200-repeat, clean-source mixed-route run. The four-way contract split is preserved with appropriate framing. Goal4240 refreshes the target map honestly, all boundary flags remain structurally locked to false, and the map correctly reads as a planning artifact, not a release authorization. The tests are solid with two small improvements recommended (elapsed floor tightening, structural `rtdl_beats_rayjoin` guard). The evidence chain remains **internal-only**; the formal release packet is the correct next step before any public claims.
