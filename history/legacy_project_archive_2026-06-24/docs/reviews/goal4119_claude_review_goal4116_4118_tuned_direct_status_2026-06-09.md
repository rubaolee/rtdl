# Claude Review — Goals 4116–4118: RT-DBSCAN Tuned Direct-Status Chain

**Date:** 2026-06-09
**Reviewer:** Claude Sonnet 4.6 (external read-only review)
**Verdict:** `accept-with-boundary`

---

## Scope

- Goal4116: `partition_cell_factor` app-surface change and test
- Goal4117: partition cell-factor route sweep script, POD artifact, report, and test
- Goal4118: `current_benchmark_route_decisions.py` refresh, route report, and test

Prior context reviewed: Goal4114 repeated-route timing report, Goal4115 route decision refresh, Goal4111/4112 prior chain reviews.

No source files were edited. No tests were run. All findings are based on reading source, test, and artifact files.

---

## Question 1 — Goal4116: Does it expose `partition_cell_factor` as an explicit user-selected control, without hidden dispatch or automatic tuning?

**Yes, cleanly.**

The function signature at `rtdl_rt_dbscan_benchmark_app.py:963` adds `partition_cell_factor: float = 0.125` as a named parameter to `run_rt_dbscan_benchmark`. It is validated immediately at line 985–987 (`if resolved_partition_cell_factor <= 0.0: raise ValueError`), before any CuPy work. This early-reject pattern is consistent with the existing `include_rows` guard and is the correct approach.

The CLI argument at lines 2206–2213 is spelled `--partition-cell-factor` with help text that explicitly states "This is advisory/user-controlled and does not authorize hidden auto-tuning." The arg value is forwarded unchanged to the function call at line 2238.

In the `partner_cupy_prepared_direct_status_union_component_signature_3d` mode (lines 1362–1467), the resolved factor is passed directly to `rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d` (line 1365), recorded in metadata as `partition_cell_factor_user_selection` (line 1419), and also verified in the handle metadata through `prepared_direct_status_union_handle_metadata["cell_factor"]`.

The source test (`goal4116_rt_dbscan_explicit_partition_cell_factor_test.py`) checks:
- text presence of `"partition_cell_factor: float = 0.125"`, `"--partition-cell-factor"`, `"partition_cell_factor_user_selection"`, and `"does not authorize hidden auto-tuning"`;
- text absence of `"auto_partition_cell_factor"` and `"autotune_partition_cell_factor"`.

The runtime test (CuPy-guarded) confirms that setting `partition_cell_factor=0.5` produces `metadata["partition_cell_factor_user_selection"] == 0.5`, `metadata["cell_factor"] == 0.5`, and `metadata["prepared_direct_status_union_handle_metadata"]["cell_factor"] == 0.5`, with all claim boundaries `False`.

No hidden dispatch path was found. The factor flows from the CLI surface, through the function parameter, to the `prepare` call and into handle/run metadata without any conditional re-assignment or automatic tuning logic.

---

## Question 2 — Goal4117: Does it fairly compare the explicit prepared direct-status route against the current grouped-stream Numba route for the same repeated component-signature contract?

**Yes, on all relevant fairness dimensions.**

`_run_current_route` (`goal4117_partition_cell_factor_route_sweep.py:68–89`) uses `mode="optix_rt_core_grouped_stream_numba_column_signature_3d"` with `repeat=4`, `warmup=1`, and the profile's canonical `radius` and `min_neighbors` from `DEFAULT_DATASET_CONFIG`.

`_run_direct_status` (lines 92–115) uses `mode="partner_cupy_prepared_direct_status_union_component_signature_3d"` with the same `dataset`, `point_count`, `seed`, `radius`, `min_neighbors`, `repeat`, and `warmup`.

Both are column-signature modes: neither materializes Python row dicts. The comparison is therefore on the same output contract. Signature equality is verified via `_component_size_signature` in `_summarize_direct` (line 133), and the POD records `same_signature: true` for every factor row of every profile. `all_factors_match_current_signature: true` is also set at the profile level, confirmed by the test at line 51.

The `replay_sec` comparison uses `float(payload["elapsed_sec"])`, which is the median elapsed time across measured runs for the direct-status path (from the `prepared_direct_status_repeat_protocol.elapsed_sec_median`), and `current_replay_sec = float(current["elapsed_sec"])`, which is likewise the median elapsed of the current route. Median-vs-median comparison is the correct protocol here.

The amortization formula at line 131–132 includes prepare cost: `(prepare_sec + elapsed_total) / measured`. The same model is applied symmetrically to the current route via `_current_prepare_sec` (lines 59–65), which reads `benchmark_timing_breakdown.host_observed_sec.prepare_sec`. The POD confirms non-zero `current_route_prepare_sec` values for all profiles (1.014s, 0.127s, 0.173s), so the current route's prepare cost is captured. The comparison is symmetric.

---

## Question 3 — Are the key Goal4117 measured results correctly stated?

**Yes. All three are verified exactly against the POD artifact.**

From `goal4117_partition_cell_factor_route_sweep_pod.json`:

| Profile | Factor | `replay_over_current_speedup` (raw) | Report states |
|---|---|---|---|
| `clustered3d` | `0.25` | `2.9605682321797486` | `2.961x` ✓ |
| `road3d` | `0.25` | `1.8656475819899945` | `1.866x` ✓ |
| `ngsim_dense` | `0.5` | `1.3124404682247919` | `1.312x` ✓ |

The corresponding `replay_sec` values (`0.031992s`, `0.021178s`, `0.011358s`) and current-route replay values (`0.094716s`, `0.039510s`, `0.014906s`) are consistent with the stated speedup ratios to within rounding. The test assertions (`assertGreater(..., 2.9)`, `assertGreater(..., 1.8)`, `assertGreater(..., 1.3)`) are conservative lower bounds that correctly fire given the measured data.

The `best_replay_partition_cell_factor` fields in the POD also match the report table: `0.25` for both clustered3d and road3d, `0.5` for ngsim_dense.

The source commit recorded in the artifact (`493bccf5...`) matches the test's pinned assertion (`self.assertEqual("493bccf5", payload["source_commit"][:8])`), and `source_tracked_worktree_dirty: false`. The run is clean and commit-pinned.

---

## Question 4 — Does the `ngsim_dense` interpretation hold: the Goal4114 loss was caused by the tested default partition granularity, and the larger explicit factor repairs it while preserving signature equality?

**Yes, and the POD data supports the mechanistic explanation.**

Goal4114 used the default `partition_cell_factor=0.125`. Goal4117's factor-0.125 row for `ngsim_dense` shows `replay_over_current_speedup: 0.1757` (consistent with Goal4114's `0.178x`, the small variance attributable to different source commits and run conditions). The mechanism is:

- Factor `0.125`: `partition_count: 60,094`, `max_neighbor_offset: 9` → many small partitions, large AABB overlap window, high overhead.
- Factor `0.5`: `partition_count: 6,124`, `max_neighbor_offset: 3` → fewer, larger partitions, smaller window, `replay_over_current_speedup: 1.312x`.

The `ngsim_dense` geometry (compact grid with small radius `0.012`) means cell-factor `0.125` creates cells barely larger than the radius, resulting in partitions that are too small and too numerous to be efficient. The larger factor `0.5` coarsens the grid enough to avoid this overhead while keeping `pair_count` manageable (321,278 vs 11,585,223 at 0.125), and `same_signature: true` confirms correctness is preserved.

Notably, factor `0.25` for ngsim_dense is marginal (`replay_over_current_speedup: 0.935x`) — slightly below breakeven — confirming the sweet spot is sensitive for this profile. This supports the report's specific recommendation of `0.5` rather than a generic "anything above default" claim.

The test explicitly asserts `ngsim[0.125]["replay_over_current_speedup"] < 0.2` and `ngsim[0.5]["replay_over_current_speedup"] > 1.3`, along with the partition count and offset values. These assertions are tight and correctly fire.

---

## Question 5 — Does Goal4118 correctly change RT-DBSCAN route guidance to `mixed_explicit_user_choice` without authorizing automatic factor selection or universal default promotion?

**Yes, on every required dimension.**

In `current_benchmark_route_decisions.py`, the `rt_dbscan` entry now has:
- `decision_kind="mixed_explicit"` and `partner_policy="mixed_explicit_user_choice"` ✓
- `user_choice_guidance` explicitly includes "Do not auto-select the factor." ✓
- `rejected_or_unpromoted_candidates` includes `"automatic partition-cell-factor tuning after Goal4117 explicit factor sweep"` ✓
- `next_runtime_action` calls for "a user-visible profile/reuse advisor that explains the explicit repeated-route cell-factor choice without hidden dispatch" ✓
- `CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` is `"rtdl.v2_10.current_benchmark_route_decisions.goal4118.v1"` ✓

The one-shot default route (grouped-stream Numba) is preserved in `primary_route` alongside the new explicit repeated-route guidance. This is not a universal promotion. The `current_reader_decision` text is long but accurately traces the full chain from Goal4074 through Goal4117, ending with: "This is still an explicit route choice, not automatic tuning."

The `__post_init__` enforcement on `CurrentBenchmarkRouteDecision` (lines 65–98) raises `ValueError` at object-construction time if any of the nine authorization flags deviates from `False` or if `user_explicit_choice_required` deviates from `True`. This is a compile-time-equivalent guard. The test confirms `validate_current_benchmark_route_decisions()` returns `status="accept"` with zero errors for all 10 apps.

The Goal4118 report itself correctly states "not automatic dispatch and not automatic tuning" and explicitly prohibits automatic factor selection in its boundary section.

---

## Question 6 — Are all claim boundaries intact?

**Yes. All prohibited claims are `False` throughout.**

Reviewed across: app payloads, sweep script top-level and per-factor-row fields, the `CurrentBenchmarkRouteDecision` dataclass with `__post_init__` enforcement, and the route-decision test.

| Claim | Status |
|---|---|
| Release authorized | `False` everywhere ✓ |
| Public speedup claim | `False` everywhere ✓ |
| Broad RT-core claim | `False` everywhere ✓ |
| Whole-app speedup claim | `False` everywhere ✓ |
| Paper reproduction claim | `False` everywhere ✓ |
| True zero-copy claim | `False` everywhere ✓ |
| Hidden dispatch | `False` everywhere; metadata carries `"not_hidden_dispatcher": True` ✓ |
| Automatic partner selection | `False` everywhere ✓ |
| Automatic factor selection | Explicitly rejected in `rejected_or_unpromoted_candidates` and user guidance ✓ |
| Native ABI added | `False` everywhere ✓ |
| App-specific engine logic | `False` everywhere ✓ |
| `partition_convergence_hybrid` promoted | `False` everywhere ✓ |
| AMD performance claim | `False` everywhere (covered by `amd_performance_claim_authorized`) ✓ |

The sweep script's per-factor-row `claim_boundary` string and the top-level payload `claim_boundary` string both enumerate the full list of excluded claims. These are consistent with the dataclass constraint enforcement.

---

## Question 7 — Are there correctness, determinism, app-agnostic, or performance-risk issues that should block the next engineering step?

**No blocking issues found.** Three non-blocking observations follow.

### Non-blocking: ngsim_dense replay speedup margin is thin

The `ngsim_dense` replay speedup at factor `0.5` is `1.312x`, the weakest winning margin of the three profiles. The amortized speedup (`2.484x`) is stronger because the prepare cost amortizes well, but the replay comparison on its own has less buffer against run-to-run GPU variance than clustered3d (`2.961x`) or road3d (`1.866x`). The guidance correctly presents this as a profile-specific explicit choice rather than a universal win. This is not a blocker but reviewers of future scale-up packets should include `ngsim_dense` at factor `0.5` as a continued validation target.

### Non-blocking: factor sensitivity is high for ngsim_dense

For `ngsim_dense`, factor `0.25` is marginal (`0.935x` replay speedup, slightly below breakeven), and factor `0.5` is the only clearly winning choice in the tested set. This makes the ngsim_dense recommendation more brittle than clustered3d/road3d, where factor `0.25` is the best of multiple profitable options. Users who deviate from the tested guidance could land in a losing configuration. The advisory guidance should make this sensitivity visible. The current `user_choice_guidance` text is appropriate but the future profile/reuse advisor (the stated next action) should highlight this explicitly.

### Non-blocking: `_current_prepare_sec` fallback

If the grouped-stream Numba `benchmark_timing_breakdown` metadata does not contain `host_observed_sec.prepare_sec`, `_current_prepare_sec` returns `0.0` and the current route's amortized cost is understated. The POD shows non-zero values (`1.014s`, `0.127s`, `0.173s`), so the fallback did not fire for these runs. This is worth noting for any future refactor of the timing-breakdown metadata format.

---

## Summary

| Goal | Finding |
|---|---|
| 4116 | Correct: `partition_cell_factor` is an explicit user-selected control with CLI surface, metadata recording, early validation, and test guards confirming no hidden auto-tuning. |
| 4117 | Fair comparison using same profile configs, same repeat/warmup, same column-signature output contract; POD results match all three stated speedup values exactly. |
| 4117 results | `clustered3d` 0.25/2.961x, `road3d` 0.25/1.866x, `ngsim_dense` 0.5/1.312x — all verified against the POD artifact. |
| ngsim_dense interpretation | Correct: Goal4114 loss was caused by default partition granularity; factor 0.5 reduces partition count from 60k to 6k and repairs the regression with signature equality preserved. |
| 4118 | Correct: `mixed_explicit_user_choice` policy set; automatic factor selection explicitly rejected; one-shot default preserved; all claim boundaries held by dataclass enforcement. |
| Claim boundaries | All prohibited flags are `False` throughout. Structural enforcement via `__post_init__` is intact. |

**Verdict: `accept-with-boundary`**

The chain is internally consistent. Goal4116's explicit factor surface is clean. Goal4117's sweep evidence is fairly constructed, commit-pinned to a clean worktree, and the stated speedup results are numerically verified. The ngsim_dense regression repair is mechanistically explained and confirmed. Goal4118's route guidance update correctly records the explicit user choice without authorizing automatic selection or universal default promotion. Claim boundaries are structurally enforced and universally `False`. No issues block the next engineering step.

This review does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, automatic factor selection, native ABI additions, AMD performance claims, or true-zero-copy claims.
