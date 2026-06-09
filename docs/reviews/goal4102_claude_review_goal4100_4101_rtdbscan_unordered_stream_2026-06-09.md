The review has been written to `docs/reviews/goal4102_claude_review_goal4100_4101_rtdbscan_unordered_stream_2026-06-09.md`. Here is the full review for your reference:

---

# External Review: Goal4100-4101 RT-DBSCAN Unordered Non-Skip Partition Stream

**Reviewer:** Claude (claude-sonnet-4-6)  
**Date:** 2026-06-09  
**Verdict:** accept-with-boundary

---

## Q1 — Is Goal4100 a genuine generic runtime/contract improvement?

**Yes.** The new mode `device_count_then_emit_non_skip_unordered` is a single sorting-suppression switch (`sort_pairs=pair_enumeration != "device_count_then_emit_non_skip_unordered"`) in `v2_8_fixed_radius_graph_component_front_door.py:1336`. No DBSCAN-specific logic is embedded. The benchmark app exposes it as an explicit CLI argument with no default promotion. The engine does not learn clustering; order-contract choice is entirely the caller's responsibility.

## Q2 — Is the contract correctly separated via `pair_order = device_atomic_append_unordered`?

**Yes.** The two modes share `pair_stream_filter = "non_skip_actionable_pairs"` and `safe_skip_pairs_elided = true` but differ by `sort_pairs` flag and the resulting `pair_order` metadata tag. The tag propagates correctly through `_partition_summary_digest` and `_skipped_partition_summary_prepare_validation`.

**Minor note:** The three pod files carry `"goal"` fields from their schema-origin goals (`Goal4085`, `Goal4087`, `Goal4095`) rather than `Goal4100`. This is harmless — `source_commit: 9e11c058` correctly ties them to Goal4100 — but can mislead a reader skimming the top-level `goal` field.

## Q3 — Do the pod artifacts support the reported improvements?

**Yes — all figures verified against raw pod data:**

| Profile | Goal4096 build median | Goal4100 build median | Speedup |
|---|---:|---:|---:|
| clustered3d | 0.076903s | 0.065708s | 1.170x ✓ |
| road3d | 0.067624s | 0.057619s | 1.174x ✓ |
| ngsim_dense | 0.136991s | 0.121038s | 1.132x ✓ |

Emit speedups (2.319x, 1.967x, 1.375x) verified from phase pod raw values. `pair_status_count_probe_sec > 0` for all profiles confirms the two-pass structure persists — the report characterizes this correctly. Prepared reuse values (0.851x / 6.941 runs clustered; 0.605x / no break-even road) confirmed from reuse pod raw data.

**ngsim_dense variance note:** Build pod run_index=1 was 0.1558s vs. median 0.1210s (~29% above). The median comparison is valid but this spread warrants monitoring in future cross-pod evidence.

## Q4 — Is Goal4101 correct to hold the current route?

**Yes.** Version bumps cleanly to `goal4101.v1`. Primary route unchanged. Goal4100 recorded as explicitly unpromoted. The decision is backed by quantitative reuse evidence below 1.0x for both profiles. `__post_init__` structural invariant enforces no flag promotion.

## Q5 — Are all claim boundaries intact?

**Yes.** All prohibited flags (`release_authorized`, `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `native_abi_added`, `app_specific_engine_logic_allowed`, `automatic_partner_selection_authorized`, `hidden_dispatch_allowed`, `default_route_promoted`, `partition_convergence_hybrid_promoted`, `broad_rt_core_claim_authorized`, `paper_reproduction_claim_authorized`, `amd_performance_claim_authorized`) are `false` across all layers. Boundary enforcement is structural (dataclass `__post_init__` raises `ValueError`) not purely documentary.

## Q6 — Is the next engineering target correct?

**Yes.** The phase pod confirms that `pair_status_count_probe_sec` (~10ms–40ms across profiles) and `build_uninstrumented_sec` (~39–40ms for all profiles) remain non-trivial even after the sort elimination. Road prepared reuse at 0.605x after 5 runs has no break-even point, making the materialization cost intrinsic to the current architecture. A fused/native fixed-radius grouped-union primitive that avoids the double pass and full pair-table materialization correctly targets all three remaining costs simultaneously.

## Test Quality

Tests are thorough and correctly structured. The functional correctness test (`test_unordered_non_skip_preserves_component_signature_when_cupy_available`) validates order-insensitivity of the component-signature algorithm against the sorted variant; the graceful CuPy skip is appropriate. All non-functional boundary tests run without CuPy.

---

**Verdict: accept-with-boundary.** Accepted as internal evidence of a localized, correct, well-bounded runtime-contract improvement. No release, public speedup, whole-app, RT-core, paper-reproduction, or any other prohibited claim is authorized. Next target: fused/native fixed-radius grouped-union primitive.
100 phase pod (clustered3d: ~10.5ms, road3d: ~9.1ms, ngsim_dense: ~39.9ms), confirming the
two-pass count+emit shape persists. The unordered optimization attacks only the emit/sort path,
not the count pass. The report correctly characterizes this.

**ngsim_dense variance note:** In the Goal4100 build pod, ngsim_dense run_index=1 recorded
0.155821s (~29% above the median of 0.121038s). The warmup=1 configuration reduces but does not
eliminate this variance. This does not invalidate the median comparison, but future cross-pod
evidence for ngsim_dense should monitor this spread.

### Prepared reuse (reuse pod)

| Profile | prepare_sec | 5-run speedup vs. current | Break-even | Reported | Verified |
|---|---:|---:|---:|---|---|
| clustered3d | 0.292903 | 0.8507 | 6.941 runs | 0.851x / 6.941 runs | Yes |
| road3d | 0.087760 | 0.6055 | null | 0.605x / none | Yes |

Values confirmed from reuse pod raw data. `default_route_promoted: false` and
`partition_convergence_hybrid_promoted: false` confirmed in prepared metadata for both profiles.
The `pair_order: "device_atomic_append_unordered"` is recorded in `partition_summary_digest` for
both profiles.

---

## Question 4: Is Goal4101 correct to keep the RT-DBSCAN route at RTDL/OptiX grouped stream plus Numba continuation?

**Finding: Yes.**

The route-decision logic in `current_benchmark_route_decisions.py` is correct:

1. The route version bumps to `rtdl.v2_10.current_benchmark_route_decisions.goal4101.v1`, a clean
   registry increment.
2. The primary route remains `RTDL/OptiX fixed-radius grouped stream with Numba component/signature
   continuation`.
3. Goal4100's unordered stream is explicitly recorded as an unpromoted candidate with the string
   `"partition_convergence_hybrid unordered non-skip default promotion after Goal4100
   order-insensitive stream evidence"` in `rejected_or_unpromoted_candidates`.
4. The promotion blockade is justified by quantitative evidence: clustered five-run reuse at
   0.851x and road at 0.605x — both below 1.0x, road with no break-even point.
5. The `CurrentBenchmarkRouteDecision.__post_init__` invariant raises `ValueError` if any boundary
   flag is set to `True`, providing structural enforcement of the non-promotion decision.

The evidence chain (Goal4074→Goal4088→Goal4093→Goal4096→Goal4100) is correctly described in
`current_reader_decision`. Goal4100 is included in `evidence_refs`.

---

## Question 5: Are all claim boundaries intact?

**Finding: Yes. All prohibited claims are correctly blocked.**

Verified across all artifacts:

| Claim type | Pod boundary | Source metadata | Route decision |
|---|---|---|---|
| `release_authorized` | false | false | false |
| `public_speedup_claim_authorized` | false | false | false |
| `rt_core_speedup_claim_authorized` | false | false | n/a |
| `whole_app_speedup_claim_authorized` | false | false | false |
| `true_zero_copy_claim_authorized` | false | false | false |
| `native_abi_added` | false | false | n/a |
| `app_specific_engine_logic_allowed` | n/a | false | false |
| `automatic_partner_selection_authorized` | n/a | false | false |
| `hidden_dispatch_allowed` | n/a | false | n/a |
| `default_route_promoted` | n/a | false | n/a |
| `partition_convergence_hybrid_promoted` | n/a | false | n/a |
| `broad_rt_core_claim_authorized` | n/a | n/a | false |
| `paper_reproduction_claim_authorized` | n/a | n/a | false |
| `amd_performance_claim_authorized` | n/a | n/a | false |

The `V28FixedRadiusGraphComponentPlan.__post_init__` raises `ValueError` if any boundary flag is
set to `True`, making boundary enforcement structural rather than purely documentary. The
route-decision `__post_init__` provides equivalent structural enforcement. The report's boundary
paragraph correctly enumerates all prohibited claim categories. No wording in the report, source,
or route decision implies promotion, public speedup, release readiness, or broader RT-core claims.

---

## Question 6: Is the stated next engineering target correct?

**Finding: Yes, and the phase pod data supports it.**

The stated target — a fused/native fixed-radius grouped-union primitive that avoids the double pass
and full partition-pair materialization — is the correct conclusion from the evidence:

- `pair_status_count_probe_sec` remains non-trivial in Goal4100 for all profiles (clustered:
  ~10.5ms, road: ~9.1ms, ngsim_dense: ~39.9ms), confirming the count pass is not free.
- `build_uninstrumented_sec` (non-instrumented build overhead) remains ~39-40ms for clustered, road,
  and ngsim_dense, indicating residual work beyond the two explicit phases.
- Prepared reuse does not break even for road (0.605x after 5 runs), meaning the
  partition-summary materialization cost is intrinsic to the current architecture.

Eliminating the double pass and avoiding full pair-table materialization addresses all three of
these remaining costs simultaneously. The current chain (Goal4088→Goal4093→Goal4096→Goal4100) has
cleanly exhausted incremental sort/filter improvements; the next gain requires a structurally
different primitive.

---

## Test Quality Assessment

| Test | Coverage | Assessment |
|---|---|---|
| `test_unordered_non_skip_mode_is_explicit_and_labeled` | Source + app text check | Good — confirms both the sort bypass and the metadata tag exist in code |
| `test_unordered_non_skip_preserves_component_signature_when_cupy_available` | Functional correctness | Good — validates order-insensitivity claim against the sorted variant; skips gracefully if CuPy absent |
| `test_pod_artifacts_are_commit_pinned_and_boundary_blocked` | Pod metadata integrity | Good — pins commit hash and checks all boundary flags |
| `test_unordered_build_is_faster_than_goal4096_sorted_non_skip` | Speedup claim backing | Good — asserts ratios from live pod files (>1.15x clustered/road, >1.10x ngsim) |
| `test_unordered_phase_improves_emit_path_but_not_underlying_two_pass_shape` | Mechanism validation | Good — confirms emit speedup and that count probe remains nonzero |
| `test_prepared_reuse_improves_prepare_but_remains_unpromoted` | Non-promotion gate | Good — checks `pair_order` tag, speedup < 1.0, road break-even null, clustered > 6.0 |
| `test_report_records_evidence_and_non_promotion_boundary` | Report completeness | Good |
| Goal4101 route decision tests | Route registry | Good — checks version, numeric claims in prose, unpromoted candidate string, boundary flags |

`test_unordered_non_skip_preserves_component_signature_when_cupy_available` is the primary
functional correctness test for the new mode. Since the sorted and unordered paths share the same
`emit_status_filter="non_skip"` logic and differ only in `sort_pairs`, this single test is
sufficient to verify sort-removal correctness — but only when CuPy is available. The graceful skip
is appropriate and the boundary test (`test_pod_artifacts_are_commit_pinned_and_boundary_blocked`)
remains runnable without CuPy.

---

## Summary

| Question | Finding |
|---|---|
| 1. Generic runtime/contract improvement | Yes — no app-specific logic; sorting suppression is a generic order-contract choice |
| 2. Contract correctly separated from sorted stream | Yes — `sort_pairs` flag, `pair_order` tag, and metadata propagation are all correct |
| 3. Pod artifacts support reported improvements | Yes — all figures verified against raw pod data |
| 4. Route correctly held at grouped-stream Numba | Yes — unordered stream unpromoted for documented quantitative reasons |
| 5. Claim boundaries intact | Yes — all prohibited flags structurally enforced and verified |
| 6. Next target correctly identified | Yes — phase pod data confirms the two-pass count+emit plus materialization shape is the remaining bottleneck |

**Verdict: accept-with-boundary.**

The chain is accepted as internal evidence of a localized, correct, well-bounded runtime-contract
improvement. The boundary holds: no release, public speedup, whole-app, broad RT-core,
paper-reproduction, hidden-dispatch, automatic-partner, app-specific-engine, native-ABI, or
true-zero-copy claims are authorized. The next engineering target is correctly identified as a
fused/native fixed-radius grouped-union primitive.
