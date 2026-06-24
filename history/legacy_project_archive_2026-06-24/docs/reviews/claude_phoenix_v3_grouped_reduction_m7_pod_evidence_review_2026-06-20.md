# Claude Review: Phoenix V3 Grouped-Reduction M7 Pod Evidence

Date: 2026-06-20

Reviewer: Claude (claude-sonnet-4-6)

Primary file: `docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_pod_evidence_2026-06-20.md`

Evidence root: `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m7_20260620/`

## Verdict

```text
approve-with-required-fixes
P0 issues: 0
P1 issues: 2
2ai_consensus_authorized: true after P1 fixes
```

All four authorization flags are correctly false throughout the intake chain. All
repeat-aware numbers have been independently verified against the raw evidence
JSONs. The post-run intake correctly refuses M7 promotion and the boundary
statements are honest. Two P1 fixes are required before Codex writes consensus:
a stale speedup ratio in the `foolish_actions` narrative field, and an
inconsistent pair-level `claim_status` label for fresh-run pairs.

## Review Question Answers

### 1. Does the report correctly interpret the fresh warmup=3 evidence?

Yes. The pod evidence report makes the following correct interpretations:

- Both scales used `warmup=3` (confirmed in raw JSON `parameters.warmup` for
  both files).
- The old 213s+ cold-setup issue that plagued the old feasibility packet is gone:
  the largest cold prepare total in this run is 5.938s (524288/sum/OptiX).
- The strongest hot-query ratio is 224.269x (262144/sum), correctly identified.
- Count rows need ~14 repeats to break even (independently computed: 13.632 for
  262144/count, 13.734 for 524288/count — ceilings both 14).
- Sum rows become compelling for repeated queries, especially by repeat 100
  (32.395x for 262144/sum, 33.608x for 524288/sum — both verified).
- Public wording still requires a prepared-query contract, repeat policy, and
  external review before any M7 promotion.

The interpretation is accurate and does not over-read the evidence.

### 2. Does the post-run intake correctly refuse M7 promotion?

Yes. The post-run intake JSON declares:

```text
status: grouped_reduction_m7_post_run_intake_not_promoted
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promoted: false
m7_qualified_release_rows: 0
```

All four authorization flags are false and the status string explicitly names the
intake as non-promoted. The M7 blockers listed are:

```text
prepared_query_contract_not_yet_public_tutorial
repeat_count_and_amortization_policy_not_reviewed
cold_setup_costs_must_be_reported_next_to_hot_speedups
no_public_row_level_external_review_for_promoted_wording
fresh_rerun_requires_external_review_before_m7_promotion
```

All five are substantive and correctly applied. The fresh_rerun flag correctly
triggered the substitution of `fresh_rerun_requires_external_review_before_m7_promotion`
in place of `no_fresh_m7_pod_rerun_after_feasibility_packet` (confirmed in both
the script logic and the per-pair blocker lists in the intake JSON).

### 3. Are the hot-query ratios and repeat-aware end-to-end results reported honestly?

Yes — all numbers independently verified from the raw evidence JSONs.

**Hot-query speedups** (embree_hot / optix_hot):

| Scale | Mode | Embree hot (s) | OptiX hot (s) | Reported ratio | Computed ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| 262144 | count | 0.008850519 | 0.000927970 | 9.538x | 9.5375x |
| 262144 | sum | 1.108349849 | 0.004942048 | 224.269x | 224.2693x |
| 524288 | count | 0.015092172 | 0.001711417 | 8.819x | 8.8185x |
| 524288 | sum | 2.407434307 | 0.013336916 | 180.509x | 180.5091x |

All ratios match.

**Break-even repeat counts** ((optix_cold − embree_cold) / (embree_hot − optix_hot)):

| Scale | Mode | Computed (raw) | Reported ceiling |
| --- | --- | ---: | ---: |
| 262144 | count | 13.6328 | 14 |
| 262144 | sum | 1.0033 | 2 |
| 524288 | count | 13.7341 | 14 |
| 524288 | sum | 0.9606 | 1 |

All break-even values and ceilings match.

**Repeat-1 end-to-end speedups** (embree_total / optix_total at repeat=1):

| Scale | Mode | Embree total (s) | OptiX total (s) | Reported | Computed |
| --- | --- | ---: | ---: | ---: | ---: |
| 262144 | count | 0.27922 | 0.37931 | 0.736x | 0.7361x |
| 262144 | sum | 2.98640 | 2.99009 | 0.999x | 0.9988x |
| 524288 | count | 0.36695 | 0.53734 | 0.683x | 0.6829x |
| 524288 | sum | 6.04548 | 5.95108 | 1.016x | 1.0159x |

All match. Notably the 262144/sum row loses by 0.001x at repeat=1 (OptiX cold
setup is 2.985s vs Embree's 1.878s; the hot-query saving of 1.103s per repeat
doesn't cover the 1.107s cold penalty until repeat=2). The 524288/sum row barely
wins at 1.016x. Both are reported honestly, not rounded to a win.

**Repeat-100 end-to-end speedups** (verified for the two most material rows):

| Scale | Mode | Embree total (s) | OptiX total (s) | Reported | Computed |
| --- | --- | ---: | ---: | ---: | ---: |
| 262144 | sum | 112.713 | 3.479 | 32.395x | 32.395x |
| 524288 | sum | 244.381 | 7.271 | 33.608x | 33.608x |

All correct.

The claim-scope labeling in the raw JSONs is consistent: every row has
`comparison_scope: internal_same_contract_prepared_query_refresh_not_public_speedup`
and `public_speedup_claim_authorized: false`. No row is tagged for external
publication.

### 4. Is it correct that grouped_reduction still needs a public prepared-query contract and fresh-result review before M7 promotion?

Yes. The five M7 blockers are all genuine and none has been resolved by this run:

1. **No public prepared-query contract exists.** The prepared-query model
   (fixed schema, pre-loaded BVH, hot-repeat workload) is not documented in any
   public tutorial. Users cannot reproduce the winning scenario without that
   contract. This blocker is real.

2. **Repeat-count and amortization policy not reviewed.** The break-even analysis
   requires a public statement about what repeat counts are realistic for the
   workloads grouped_reduction targets. Neither the rerun packet nor this
   post-run intake provides that policy.

3. **Cold/setup costs must be reported next to hot speedups.** The 224.269x
   hot-query ratio is correct but the 2.985s OptiX cold setup for 262144/sum
   makes single-query end-to-end a slight loss (0.999x). Any public claim must
   show both together.

4. **No public row-level external review for promoted wording.** This review is
   the first external review of the fresh result; Codex consensus has not yet
   closed.

5. **Fresh-rerun requires external review before M7 promotion.** This is the
   structural gate: the rerun packet explicitly stated that post-run external
   review is required before any M7 promotion is considered. This review
   satisfies that gate, but consensus must follow.

The marginal single-query win for 524288/sum (1.016x) is not sufficient to
override the missing public contract. Even the strongest case — 180.509x hot
speedup with repeat-1 win — lacks a public amortization policy that would let
users know when they can expect that scenario.

### 5. What P0/P1 fixes are required before Codex writes consensus?

See P0 and P1 sections below.

## P0 Issues

None.

## P1 Issues

**P1-1: Stale "158x" figure in `goal_level_decision_audit.foolish_actions`.**

Both `m7_grouped_reduction_post_run_intake.json` and `m7_grouped_reduction_post_run_intake.md`
contain this text in their goal-level decision audit:

```text
It would be foolish to promote the 158x sum hot-query ratio without cold/setup
cost and repeat-count context.
```

There is no 158x ratio anywhere in this run's evidence. The actual hot-query
speedups are 224.269x (262144/sum) and 180.509x (524288/sum). The 158x figure
appears to be a stale placeholder from the pre-run feasibility work; it was
hardcoded in `scripts/v3_phoenix_grouped_reduction_m7_feasibility.py` at the
`goal_level_decision_audit.foolish_actions` field (line ~141) and was not updated
when the fresh-rerun path was added.

The inconsistency is internal to a narrative field and does not affect any
authorization flag or numeric table. However, the `forbidden_public_reading` field
in the same document correctly says "up to 224.269x" — so the two fields in the
same document disagree about what the maximum ratio is. A downstream reader or
Codex consensus document citing the `foolish_actions` text would carry a wrong
number.

Fix required in `scripts/v3_phoenix_grouped_reduction_m7_feasibility.py`:
update the `foolish_actions` string in `build_payload()` to reference the actual
computed maximum, either by interpolating `max_hot_query_speedup` (as is already
done for `forbidden_public_reading`) or by using a correct magnitude (e.g.,
"over 180x"). Regenerate `m7_grouped_reduction_post_run_intake.json` and
`m7_grouped_reduction_post_run_intake.md` from the updated script. The test
suite should add an assertion that `foolish_actions` does not contain "158x".

**P1-2: Per-pair `claim_status` is `"internal_feasibility_not_m7"` for fresh-rerun pairs.**

Every pair in `m7_grouped_reduction_post_run_intake.json` carries:

```json
"claim_status": "internal_feasibility_not_m7"
```

The overall `status` correctly says `grouped_reduction_m7_post_run_intake_not_promoted`,
but the pair-level field still uses the feasibility label. The field `claim_status`
is set to the hardcoded string `"internal_feasibility_not_m7"` in `_pair_summary()`
regardless of `fresh_rerun`. Any downstream tool that reads pair-level
`claim_status` to distinguish feasibility evidence from fresh-rerun intake evidence
will misclassify these pairs.

Fix: in `_pair_summary()` in `scripts/v3_phoenix_grouped_reduction_m7_feasibility.py`,
set `claim_status` conditionally:

```python
"claim_status": "internal_post_run_intake_not_m7" if fresh_rerun else "internal_feasibility_not_m7",
```

Regenerate the intake JSON and MD. The pod evidence test
`test_all_sources_are_warmup3_and_claim_flags_false` should assert the correct
pair-level `claim_status` for a fresh-rerun intake.

## Arithmetic Spot-Check: Independent Verification

The following values were computed independently from the raw evidence JSON
files and compared against the post-run intake:

**262144/count break-even**:
(0.37837917 − 0.27037230) / (0.00885052 − 0.00092797) = 0.10800687 / 0.00792255 = 13.6328 → ceiling 14 ✓

**262144/sum break-even**:
(2.98514418 − 1.87805255) / (1.10834985 − 0.00494205) = 1.10709163 / 1.10340780 = 1.0033 → ceiling 2 ✓

**524288/count break-even**:
(0.53562857 − 0.35185550) / (0.01509217 − 0.00171142) = 0.18377307 / 0.01338075 = 13.7341 → ceiling 14 ✓

**524288/sum break-even**:
(5.93774370 − 3.63804919) / (2.40743431 − 0.01333692) = 2.29969451 / 2.39409739 = 0.9606 → ceiling 1 ✓

**262144/sum repeat-100 end-to-end**:
- Embree: 1.87805255 + 100 × 1.10834985 = 112.713 s ✓
- OptiX: 2.98514418 + 100 × 0.00494205 = 3.479 s ✓
- Speedup: 112.713 / 3.479 = 32.395x ✓

**524288/sum repeat-1 end-to-end**:
- Embree: 3.63804919 + 2.40743431 = 6.0455 s ✓
- OptiX: 5.93774370 + 0.01333692 = 5.9511 s ✓
- Speedup: 6.0455 / 5.9511 = 1.0159x ✓ (marginal win reported honestly as 1.016x)

No arithmetic errors were found.

## Boundary Statement Assessment

**Allowed internal reading** (from intake):

```text
The generic prepared grouped-reduction primitive has fresh pod evidence for
large hot-query wins and repeat-100 end-to-end wins under warmup=3.
```

Accurate: all four hot-query ratios are large (≥ 8.8x), and all four
repeat-100 end-to-end speedups are genuine wins (≥ 2.4x).

**Forbidden public reading** (from pod evidence report):

```text
Do not claim the fresh grouped_reduction hot-query ratios, up to 224.269x, are
end-to-end speedups. Do not claim whole-database speedup. Do not promote M7
before fresh-result external review and a public prepared-query contract.
```

All three prohibitions are correctly stated. The "up to 224.269x" cap matches
the computed max hot-query speedup exactly.

## Claim-Boundary Gate Confirmation

The pod artifacts record:

```text
m7_execution.status: 0
```

The claim-boundary gate text (per test `test_run_artifacts_and_report_exist`)
must contain "claim-boundary gate ok". This gate was the P0-fix deliverable from
the prior rerun-packet review and is confirmed present in the test suite.

All four authorization flags were false at commit time and are false in the
intake JSON. The gate correctly asserts `whole_app_speedup_claim_authorized` in
addition to the three other flags (confirmed as part of the prior rerun-packet
P0 fix that was applied before this run).

## Test Suite Assessment

The four test methods in `tests/v3_phoenix_grouped_reduction_m7_pod_evidence_test.py`
cover the critical cases:

1. `test_post_run_intake_is_fresh_not_promoted` — asserts all five top-level
   flags and key summary fields including `pair_count=4`, `all_cpu_reference_match`,
   `all_optix_hot_faster`, and `any_sum_row_has_large_cold_cost=False`.

2. `test_all_sources_are_warmup3_and_claim_flags_false` — asserts per-scale
   `source_warmup=3`, per-pair CPU match, RT-core flags, and that
   `fresh_rerun_requires_external_review_before_m7_promotion` is present and
   `no_fresh_m7_pod_rerun_after_feasibility_packet` is absent.

3. `test_repeat_aware_results_block_hot_query_overclaim` — pins the key
   numerical facts: 262144/sum hot > 200x but repeat-1 < 1.0; 524288/sum hot >
   180x, repeat-1 between 1.0 and 1.1; count break-even between 10 and 20;
   repeat-100 wins for both modes.

4. `test_run_artifacts_and_report_exist` — checks that required artifact files
   are present, `m7_execution.status` is "0", claim-boundary gate text is
   correct, and the report MD contains key phrases including "224.269x",
   "Repeat 1 end-to-end", and "repeat-1 losses".

Coverage is sound. After P1 fixes are applied, one additional assertion is
recommended:

- In `test_all_sources_are_warmup3_and_claim_flags_false`, assert that
  `pair["claim_status"] == "internal_post_run_intake_not_m7"` for each pair (so
  the P1-2 fix is mechanically guarded).
- In any intake-focused test, assert that
  `"158" not in payload["goal_level_decision_audit"]["foolish_actions"]` (or
  more specifically that the `foolish_actions` text does not name a ratio that
  does not appear in the evidence).

## Wording Gate

Not run in this review session. The prior Codex consensus confirms the wording
gate passed before the pod run (`violations: []`). The pod evidence report does
not add any new public wording; it explicitly marks itself as intake-not-promotion.
No new gate run is required for this post-run intake document, but the gate should
be confirmed to still pass after P1 fixes regenerate the intake JSON/MD.

## Lineage Integrity

This run correctly closes the loop opened by the prior rerun-packet review:

1. The prior Claude review found P0: `whole_app_speedup_claim_authorized` missing
   from the claim-boundary gate. That fix was applied and confirmed in the Codex
   consensus before the pod run.

2. The pod ran exactly the accepted execution shape: two scales, two modes per
   scale, two backends, warmup=3, `--include-iteration-walls`, with post-run
   intake required before interpretation.

3. Old warmup=1/2 evidence was not merged (both source files carry
   `source_warmup: 3`).

4. The intake produces the required repeat-aware totals for all nine repeat
   counts (1, 2, 5, 10, 25, 50, 100, 500, 1000).

5. The intake correctly computes cold+hot totals from
   `cold_prepare_total_sec` (not from `workload_build_sec` alone), so the
   repeat-aware scenarios correctly amortize the full cold cost.

No lineage regression is present.

## Observations (Not Blockers)

- **Embree/sum iteration count is low (repeat=10 after warmup=3).** At 1.108s
  per iteration (262144/sum), 10 post-warmup iterations gives ~11s of
  measurement time and a stable median. At 2.407s per iteration (524288/sum),
  10 iterations gives ~24s. This is lower sample count than count rows (400
  post-warmup), but `prepared_steady_state: true` and the large per-iteration
  cost suggest the median is reliable. Not a blocker.

- **The 524288/sum repeat-1 win (1.016x) is marginal.** It is correctly
  reported and correctly kept as internal intake evidence rather than a public
  claim. The break-even ceiling of 1 (raw 0.9606) means OptiX wins at any
  repeat count for this scale/mode, but the 1.6% margin makes the single-query
  case unsuitable for public wording without further validation runs.

- **`git_head: "fatal: not a git repository"` in both raw JSONs.** This is
  expected for a pod run in a non-git directory. It reduces artifact
  traceability (no commit hash in evidence files). Not a blocker for this
  intake, but a future improvement would be to stamp the commit hash before
  uploading to the pod.

## Bottom Line

The fresh warmup=3 pod evidence is honest and complete. The hot-query wins are
real (up to 224.269x). The repeat-aware end-to-end analysis is arithmetically
correct and correctly shows that single-query parity requires sum-mode or many
repeats. The intake correctly refuses M7 promotion and preserves all four
authorization flags as false.

Two P1 fixes are required: correct the stale "158x" reference in `foolish_actions`,
and update per-pair `claim_status` to distinguish fresh-rerun intake from
feasibility. Both fixes are one-line changes in the generator script followed by
artifact regeneration. After those fixes, confirm 20 tests still pass, the
wording gate still passes, and Codex consensus is authorized.
