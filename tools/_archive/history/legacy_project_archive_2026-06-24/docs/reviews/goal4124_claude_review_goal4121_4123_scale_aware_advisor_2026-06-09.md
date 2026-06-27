# Claude Review — Goals 4121–4123: RT-DBSCAN Scale-Aware Route Advisor

**Date:** 2026-06-09
**Reviewer:** Claude Sonnet 4.6 (external read-only review)
**Verdict:** `accept-with-boundary`

---

## Scope

- Goal4121: `explain_rt_dbscan_explicit_route_choice` advisor function, CLI flags `--explain-route-choice` / `--repeated-component-signature`, report, and test
- Goal4122: 131,072-point scale probe (reuses Goal4117 runner), pod artifact, report, and test
- Goal4123: `current_benchmark_route_decisions.py` refresh to scale-aware guidance, report, and test

Prior context reviewed: Goal4119 Claude review and Goal4120 Gemini review of the Goals 4116–4118 chain (tuned direct-status).

No source files were edited. No tests were run. All findings are based on reading source, test, artifact, and report files.

---

## Question 1 — Does Goal4121's advisor remain advisory-only, with no hidden dispatch, no automatic partner selection, and no automatic factor selection?

**Yes, on every required dimension.**

`explain_rt_dbscan_explicit_route_choice` (app lines 103–180) returns a packet with:
- `status: "advisory_only_no_dispatch"` ✓
- `user_must_select_route: True` ✓
- `automatic_dispatch_authorized: False` ✓
- `automatic_partner_selection_authorized: False` ✓
- `automatic_partition_cell_factor_selection_authorized: False` ✓
- `hidden_dispatch_allowed: False` ✓

The function returns an `options` tuple but does not call any route executor. The CLI handler (app lines 2324–2336) checks `if args.explain_route_choice:`, calls the advisor, prints JSON, and returns 0 before reaching `run_rt_dbscan_benchmark`. The two code paths are mutually exclusive; the advisor branch cannot fall through to dispatch.

The test (`goal4121_rt_dbscan_explicit_route_choice_advisor_test.py`) asserts all six advisory flags explicitly, including the CLI test (`test_cli_explain_route_choice_prints_advisory_without_running`) which spawns the process, parses stdout, and confirms `status == "advisory_only_no_dispatch"` and `automatic_dispatch_authorized == False` without any GPU execution.

No hidden dispatch path was found. The advisor is structurally separated from the benchmark runner.

---

## Question 2 — Does the advisor correctly expose scale-aware NGSIM evidence: `0.5` at 65k from Goal4117 and `0.25` at 131k from Goal4122?

**Yes, both entries are present and the ranking is correctly scale-driven.**

`RT_DBSCAN_TESTED_DIRECT_STATUS_PARTITION_CELL_FACTOR_OPTIONS` (app lines 33–46) records:

```python
"ngsim_dense": (
    {"point_count": 65536, "factor": 0.5,  "replay_speedup": 1.312, "evidence_refs": ("Goal4117",)},
    {"point_count": 131072, "factor": 0.25, "replay_speedup": 1.399, "evidence_refs": ("Goal4122",)},
),
```

When `point_count` is supplied, the advisor sorts by `abs(tested_point_count - resolved_point_count)` (app line 128), so:
- At 65,536: 65k entry (factor 0.5) ranks first ✓
- At 131,072: 131k entry (factor 0.25) ranks first ✓

Test `test_ngsim_scale_aware_options_rank_closest_evidence_first` confirms both orderings and that `automatic_partition_cell_factor_selection_authorized` remains `False` throughout. Test `test_cli_explain_route_choice_prints_advisory_without_running` confirms the CLI at 131k returns factor 0.25 with `tested_point_count == 131072` and `Goal4122` in `evidence_refs`.

The Goal4121 report table shows `ngsim_dense` factor as `0.5` (the 65k representative value), which is technically accurate for the state before Goal4122 was probed. The dual-scale nature is implicit in the report but fully explicit in the code. Since Goal4123's report and route guidance carry the complete scale-aware representation, this is not a correctness gap.

---

## Question 3 — Does Goal4122 fairly reuse the Goal4117 runner for a 131,072-point scale probe, and are the key measured results correctly stated?

**Yes to both. All three speedup values verify exactly against the pod artifact.**

The pod carries `"schema": "rtdl.goal4117.partition_cell_factor_route_sweep.v1"`, confirming runner reuse. Setup matches Goal4117's protocol: `repeat: 4`, `warmup: 1`, clean worktree (`source_tracked_worktree_dirty: false`), commit-pinned to `c38d071b`.

Verifying stated speedups against `goal4122_tuned_direct_status_scale_probe_pod.json`:

| Profile | Report states | Pod raw value | Verified |
|---|---|---|---|
| `clustered3d` | factor `0.25`, `3.211x` | `best_replay_over_current_speedup: 3.2114175...` | ✓ |
| `road3d` | factor `0.25`, `1.545x` | `best_replay_over_current_speedup: 1.5453736...` | ✓ |
| `ngsim_dense` | factor `0.25`, `1.399x` | `best_replay_over_current_speedup: 1.3994543...` | ✓ |

Cross-check on `clustered3d`: `replay_sec: 0.107770 / current_route_replay_sec: 0.346095 = 3.211x` ✓. The same arithmetic holds for the other two profiles.

All factor rows across all three profiles report `same_signature: true` and `all_factors_match_current_signature: true`, confirming correctness preservation at 131k scale.

The test assertions (`assertGreater(..., 3.2)`, `assertGreater(..., 1.5)`, `assertGreater(..., 1.3)`) are conservative lower bounds that correctly fire given the measured values.

---

## Question 4 — Does Goal4123 correctly update current route guidance to scale-aware evidence without claiming a universal dense-profile factor?

**Yes. The guidance is explicitly scale-differentiated and auto-selection remains blocked.**

In `current_benchmark_route_decisions.py`, the `rt_dbscan` entry's `user_choice_guidance` (line 225) includes:

> "Use the route advisor or scale-specific evidence: 0.5 at 65k and 0.25 at 131k. Do not auto-select the factor."

The `current_reader_decision` (lines 171–213) now traces Goal4121 and Goal4122 explicitly and states their measured speedups (`3.211x`, `1.545x`, `1.399x`) and the ngsim factor flip. It ends: "This is still an explicit route choice, not automatic tuning."

`CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` is updated to `"rtdl.v2_10.current_benchmark_route_decisions.goal4123.v1"`. The `rejected_or_unpromoted_candidates` field (lines 229–241) continues to enumerate automatic partition-cell-factor tuning as explicitly rejected.

The `next_runtime_action` (lines 243–251) calls for keeping the "user-visible profile/reuse advisor scale-aware" and continuing with either "one-shot prepare-cost reduction or a larger representative-scale packet beyond 131k." No universal default promotion is introduced.

Test `goal4123_current_route_decision_after_scale_aware_advisor_test.py` asserts:
- version string `goal4123.v1` ✓
- `"0.5 at 65k"` and `"0.25 at 131k"` in `user_choice_guidance` ✓
- `"Do not auto-select"` in `user_choice_guidance` ✓
- `"scale-aware"` and `"beyond 131k"` in `next_runtime_action` ✓
- Both Goal4121 and Goal4122 in `evidence_refs` ✓
- `validate_current_benchmark_route_decisions()` returns `status="accept"` with zero errors ✓

The advisor cross-test (`test_advisor_ranks_ngsim_factor_by_supplied_scale`) confirms the advisor delivers factor 0.5 at 65k and factor 0.25 at 131k, with `automatic_partition_cell_factor_selection_authorized: False` in both packets.

---

## Question 5 — Are all claim boundaries intact?

**Yes. All prohibited claims are `False` throughout.**

| Claim | Status |
|---|---|
| Release authorized | `False` everywhere ✓ |
| Public speedup claim | `False` everywhere ✓ |
| Broad RT-core claim | `False` everywhere ✓ |
| Whole-app speedup claim | `False` everywhere ✓ |
| Paper reproduction claim | `False` everywhere ✓ |
| True zero-copy claim | `False` everywhere ✓ |
| Hidden dispatch | `False` + `hidden_dispatch_allowed: False` in advisor packet ✓ |
| Automatic partner selection | `False` everywhere ✓ |
| Automatic factor selection | Explicitly rejected in `rejected_or_unpromoted_candidates`; `automatic_partition_cell_factor_selection_authorized: False` in all advisor packets ✓ |
| Native ABI added | `False` everywhere ✓ |
| App-specific engine logic | `False` everywhere ✓ |
| `partition_convergence_hybrid` promoted | `False` everywhere ✓ |
| AMD performance claim | `False` everywhere (covered by `amd_performance_claim_authorized`) ✓ |

The `CurrentBenchmarkRouteDecision.__post_init__` (lines 87–99) raises `ValueError` at object-construction time if any of the nine authorization flags deviates from `False` or if `user_explicit_choice_required` deviates from `True`. This is a build-time-equivalent structural guard.

The pod's per-factor-row `claim_boundary` strings and the advisor's packet `claim_boundary` string are consistent with the dataclass enforcement. The Goal4123 `CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY` string enumerates all prohibited claims explicitly, including the new "route-choice advisor" and "131k scale probe" evidence in its description.

---

## Question 6 — Are there correctness, determinism, app-agnostic, or performance-risk issues that should block the next engineering step?

**No blocking issues found.** Four non-blocking observations follow.

### Non-blocking: Goal4121 report table shows only the 65k representative factor for ngsim_dense

The report table lists `ngsim_dense` factor as `0.5`. The code already encodes both scale entries. This makes the report's static table a partial view of the advisor's actual behavior. The Goal4123 report and route guidance fully correct for this. Not a correctness gap, but future goal reports introducing multi-scale evidence should document all scale entries explicitly rather than just the representative.

### Non-blocking: Closest-point-count tie-break is order-dependent

The advisor sorts by `abs(tested_point_count - resolved_point_count)`. If a future query lands equidistant between two evidence points (e.g., 98k between 65k and 131k), Python's stable sort preserves the original tuple order, meaning the 65k entry would rank first. This is not currently a problem with two well-separated scale points but becomes meaningful as more evidence is added. The advisor should document the tie-break semantics or switch to a deterministic tie-break (e.g., prefer the smaller tested point count when equidistant).

### Non-blocking: ngsim_dense replay speedup margin is the tightest at both scales

At 65k: `1.312x`. At 131k: `1.399x`. The 131k margin is modestly better, but both are materially weaker than clustered3d (`2.961x` / `3.211x`) and road3d (`1.866x` / `1.545x`). The ngsim_dense profile's sensitivity to factor choice (flipping from 0.5 to 0.25 as scale doubles) suggests the geometry-factor relationship continues to shift with scale. The stated next action ("larger representative-scale packet beyond 131k") is the correct response.

### Non-blocking: road3d replay speedup decreased from 65k to 131k

At 65k: `1.866x`. At 131k: `1.545x`. The speedup dropped by ~17% as scale doubled. Clustered3d went from `2.961x` to `3.211x` (improving). Road3d is the only profile showing a replay speedup regression across scale while remaining clearly positive. This is not alarming but suggests road3d should be included as a priority profile in any future larger-scale packet.

---

## Summary

| Goal | Finding |
|---|---|
| 4121 | Correct: advisor is structurally separated from the benchmark runner; no dispatch path exists; all advisory flags are `False`; CLI early-exit is clean; test coverage of both function and CLI surfaces is adequate. |
| 4121 scale awareness | Correct: both 65k and 131k ngsim_dense entries are present in `RT_DBSCAN_TESTED_DIRECT_STATUS_PARTITION_CELL_FACTOR_OPTIONS` and ranking is driven by supplied `point_count`; report's single-factor table is a partial view but not incorrect. |
| 4122 | Fair: reuses Goal4117 runner schema and protocol; commit-pinned to clean worktree; all three speedup values (`3.211x`, `1.545x`, `1.399x`) verify exactly against pod raw fields; all signature checks pass. |
| 4122 scale probe results | `clustered3d` 0.25/3.211x, `road3d` 0.25/1.545x, `ngsim_dense` 0.25/1.399x — all numerically verified. |
| 4123 | Correct: route guidance updated with explicit scale-aware language; ngsim factor flip from 0.5→0.25 is correctly documented without claiming a universal factor; `mixed_explicit_user_choice` policy preserved; all flags held by dataclass enforcement; validation returns `status="accept"` with zero errors. |
| Claim boundaries | All prohibited flags are `False` throughout. Structural enforcement via `__post_init__` is intact. |

**Verdict: `accept-with-boundary`**

The Goals 4121–4123 chain is internally consistent. The advisor is cleanly advisory-only with no dispatch surface. Goal4122's 131k scale probe fairly reuses the Goal4117 runner and the stated speedup values are exactly verified against the pod artifact. Goal4123 correctly encodes scale-aware guidance, explicitly presents the ngsim_dense factor as scale-dependent rather than universal, and structurally enforces all claim boundaries. The four non-blocking observations (report table completeness, tie-break semantics, ngsim margin, road3d regression) are all manageable by the stated next action of a larger-scale packet.

This review does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, automatic factor selection, native ABI additions, AMD performance claims, or true-zero-copy claims.
