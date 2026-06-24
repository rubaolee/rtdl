# Claude Review: Phoenix V3 Grouped-Reduction M7 Feasibility Packet

Date: 2026-06-20

Reviewer: Claude (claude-sonnet-4-6)

Packet: `docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.md`
JSON: `docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.json`
Script: `scripts/v3_phoenix_grouped_reduction_m7_feasibility.py`
Tests: `tests/v3_phoenix_grouped_reduction_m7_feasibility_test.py`

## Verdict

```text
approve-with-required-fixes
P0 issues: 0
P1 issues: 5
2ai_consensus_authorized: true (after P1 fixes)
```

The packet is mathematically correct, refuses M7 promotion for the right reasons, and blocks the false 158x end-to-end overclaim explicitly. No finding requires blocking consensus. P1 items must be fixed before Codex writes the 2-AI consensus record.

## Review Question Answers

### 1. Is the repeat-aware amortization math correct?

Yes. Independently verified all four cases against the source evidence JSONs.

Formula: `embree_total = embree_cold + n * embree_query`, `optix_total = optix_cold + n * optix_query`, `speedup = embree_total / optix_total`.

Break-even derivation: `n = (optix_cold - embree_cold) / (embree_query - optix_query)` when that result is positive; 1.0 when optix is already cheaper cold (cold_penalty ≤ 0); inf when hot saving ≤ 0.

Verification results (independent Python computation against source JSON values):

| Scale | Mode | hot speedup | break-even | ceiling | r=1 | r=100 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 262,144 | count | 9.863861 | 1.000000 | 1 | 18.080719x | 16.458010x |
| 262,144 | sum | 202.773996 | 1.000000 | 1 | 1.624894x | 3.114570x |
| 524,288 | count | 8.751652 | 17.175676 | 18 | 0.592304x | 2.579191x |
| 524,288 | sum | 158.010302 | 1.000000 | 1 | 1.019809x | 1.972766x |

All values match the committed packet exactly to the precision shown. The math is correct.

The break-even function correctly handles all three branches:
- `cold_penalty <= 0`: optix already wins cold → return 1.0 (262k/count, 262k/sum, 524k/sum all fall here)
- `hot_saving <= 0`: optix cannot amortize the cold penalty → return inf (none in this packet)
- general case: `cold_penalty / hot_saving` → 17.18 for 524k/count

### 2. Does the packet correctly refuse M7 promotion despite hot-query wins?

Yes. All top-level and per-pair flags are false: `m7_promoted`, `release_authorized`, `public_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`. `m7_qualified_release_rows` = 0.

The five M7 blockers are concrete and non-trivial:

1. `prepared_query_contract_not_yet_public_tutorial` — without a public tutorial explaining the prepared-query lifecycle, users cannot reproduce the hot-query scenario or understand what they are buying.
2. `repeat_count_and_amortization_policy_not_reviewed` — the packet shows repeat-aware math but does not define what repeat count is a legitimate user workload assumption.
3. `cold_setup_costs_must_be_reported_next_to_hot_speedups` — at 524k/sum, both cold costs exceed 213s and are not hidden; at 262k/sum, optix cold is 65s.
4. `no_fresh_m7_pod_rerun_after_feasibility_packet` — this is analysis on existing evidence, not a fresh M7-designated rerun.
5. `no_public_row_level_external_review_for_promoted_wording` — external review of the release wording itself has not occurred.

The refusal is principled: the 262k/count case already wins end-to-end at repeat=1 (18x), yet the packet still refuses promotion because the public contract is missing. This is the correct discipline.

### 3. Does it clearly block the false reading "RayDB-style V3 is 158x faster end to end"?

Yes. The packet blocks this claim through three independent mechanisms:

1. `forbidden_public_reading` field in the JSON: "Do not claim RayDB-style V3 is 158x faster end to end, do not claim whole-database speedup, and do not hide cold/setup cost behind hot-query ratios."
2. The MD report surfaces this verbatim and is checked by `test_report_blocks_end_to_end_overclaim`.
3. The repeat-aware table makes the 524k/sum end-to-end at repeat=1 explicit: 1.020x, not 158x. A reader who looks at the table sees that the 158x hot ratio becomes a 1.020x end-to-end result at the first query.

The 158x figure is the 524k/sum hot prepared-query ratio only. With optix_cold=215.84s and embree_cold=218.03s, both cold costs are nearly symmetric and the claimed speedup collapses to near-unity at repeat=1. The packet makes this visible.

### 4. Are the tests strong enough?

The five tests cover the critical correctness and boundary cases. Three concerns are filed as P1:

**What the tests cover well:**
- All top-level flags blocked (feasibility, not m7, not release)
- 524k/count break-even range (> 10, < 25) and single-query loss (< 1.0)
- 524k/sum hot speedup > 100x, cold cost > 200s, 1.0 < repeat=1 < 1.1
- Per-pair: m7_promoted, release_authorized, public_speedup_claim_authorized, both rt_core_accelerated flags, non-empty blockers, internal claim_status
- Script idempotency: rebuilt summary and scales match committed JSON
- Report key phrases including forbidden claim

**P1 gaps (see P1 section for details):**
- No explicit test for the 262k/count scenario (break_even=1, repeat=1=18.08x, the packet's strongest evidence)
- `count_rows_need_repeat_amortization` uses `any()` over pairs; the packet has one count row with break_even=1.0 (always wins) and one with 17.18 (needs amortization) — the flag is True but could mislead
- `render_markdown()` hardcodes `release_authorized: false` etc. as literal strings rather than deriving from the payload; a future regression where `build_payload()` is changed would not be caught by the report test

### 5. P0 and P1 issues

## P0 Issues

None. The math is correct, the verdict is correct, the boundary text is present and tested, and the packet's evidence base is correctly handled.

## P1 Issues

**P1-1: MD summary table always shows `prepared_query_contract_not_yet_public_tutorial` as "Main blocker" for all four pairs.**

`render_markdown()` uses `pair["m7_blockers"][0]`, which is always the first element of the blocker list. For 524k/count, the first element is `prepared_query_contract_not_yet_public_tutorial` but the operationally critical fact is `single_query_end_to_end_not_optix_win` (OptiX actually loses at repeat=1). A reader scanning the summary table cannot learn from the "Main blocker" column that the 524k/count is a single-query loss. The repeat=1 speedup column (0.592x) does show this, but the blocker column misses the opportunity to name it prominently.

Fix: render the last blocker in the list (which the script appends conditionally and is the most case-specific) as "Main blocker", or render all blockers separated by a visible delimiter, or annotate the "Break-even repeats" column with a "(loss)" marker when repeat=1 < 1.0.

**P1-2: No test explicitly validates the 262k/count favorable scenario.**

The 262k/count case is the packet's strongest evidence: break_even=1, end-to-end at repeat=1=18.08x. There is no assertion that specifically pins this scenario's properties. If the 262k source JSON were replaced with a degraded run, `test_repeat_amortization_keeps_count_and_sum_honest` would not catch it (it only examines 524k pairs).

Fix: add at least two assertions for `pairs[(262144, "count")]` in `test_repeat_amortization_keeps_count_and_sum_honest`:
```python
count_262k = pairs[(262144, "count")]
self.assertEqual(count_262k["break_even_repeat_count_ceiling"], 1)
self.assertGreater(count_262k["repeat_scenarios"]["1"]["end_to_end_speedup"], 15.0)
```

**P1-3: `render_markdown()` hardcodes release/claim flags as literal strings.**

```python
"release_authorized: false",
"public_speedup_claim_authorized: false",
"whole_app_speedup_claim_authorized: false",
```

These are not derived from `payload`. If `build_payload()` were ever modified to set `release_authorized: True`, the MD header would still show `false`. The `test_report_blocks_end_to_end_overclaim` test would pass incorrectly because it reads the committed MD file (which has the hardcoded strings), not the rebuilt output.

Fix: derive these from the payload:
```python
f"release_authorized: {str(payload['release_authorized']).lower()}",
f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
f"whole_app_speedup_claim_authorized: {str(payload['whole_app_speedup_claim_authorized']).lower()}",
```

**P1-4: 262k/sum Embree workload_build cost (105.16s) is not surfaced despite exceeding 100s.**

`min_workload_build_sec` for 262k/sum is 64.08s (the OptiX path), which is below the 100s threshold that triggers `large_sum_workload_build_cost_must_be_prominent`. However, the Embree workload_build for 262k/sum is 105.16s. If a user attempts to benchmark this row with Embree alone (before they have an OptiX setup), they face a 105s cold cost that is not flagged anywhere in the packet. The current design correctly uses `min()` to represent the cheapest available path, but the absence of the Embree cold cost from the summary is a silent gap.

Fix: document in the packet markdown that `min_workload_build_sec` reflects the fastest-path cold cost (OptiX where available) and that the Embree baseline cold cost may be significantly higher. Or add a `large_embree_cold_cost_must_be_prominent` blocker when `embree_workload_build > 100.0` for any mode.

**P1-5: Warmup asymmetry between the two source evidence files is not documented.**

The 262k source evidence used `warmup=1`; the 524k source used `warmup=2`. The feasibility packet does not record this difference. Warmup count affects both the cold_prepare_total_sec measurement and the steady-state elapsed_median_sec. Cross-scale comparisons in the repeat-aware table are not directly affected (each pair uses its own source values), but the asymmetry should be disclosed for any future rerun that attempts to standardize across scales.

Fix: add a `source_warmup` field per scale in the feasibility JSON, or note the warmup values in the packet markdown under the source evidence section.

## Evidence Integrity

Source evidence files verified:
- `docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/m28_raydb_grouped_reduction_262144.json`: status=ok, 4 rows, all matches_cpu_reference=true, embree rt_core_accelerated=false, optix rt_core_accelerated=true.
- `docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620/m28_raydb_grouped_reduction_524288.json`: status=ok, 4 rows, all matches_cpu_reference=true, embree rt_core_accelerated=false, optix rt_core_accelerated=true.

Both files have `public_speedup_claim_authorized: false` at top level and per-row. RT-core flag distinction is correctly recorded in source and correctly propagated to the feasibility packet and tests.

The prior Codex 2-AI consensus on the RayDB M28 evidence (`codex_phoenix_v3_raydb_m28_grouped_reduction_2ai_consensus_2026-06-20.md`) accepted the same raw data as internal evidence only. The feasibility packet uses that accepted evidence as its input without widening any claim.

## Wording Gate

The release wording gate (`v3_release_wording_gate.py`) now requires:
- `grouped_reduction_m7_feasibility_not_promoted`
- `Do not claim RayDB-style V3 is 158x faster end to end`
- `cold/setup and repeat-count policy are not yet a public contract`

All three strings are present in the committed packet. The gate correctly guards that these boundary phrases survive any future documentation edit.

## Bottom Line

The packet correctly characterizes grouped reduction as a strong internal candidate that cannot yet be released. The math is verified. The refusal to promote is principled and not just procedural — the 524k/count case genuinely loses on single-query end-to-end (0.592x), and the 524k/sum case barely wins at repeat=1 (1.020x) despite a 158x hot ratio. The 262k/count case is the only pair that wins cleanly end-to-end from the first query, and even that is correctly blocked on the absent public contract. No test or reasoning in the packet contradicts the verdict.

Fix the five P1 items. Consensus is authorized after fixes.
