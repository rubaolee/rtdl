# Call For Review - X-HD Graphics Level-B Packet Through Goal5300

Please strictly review the current X-HD public Stanford graphics Level-B
evidence packet.

## Scope

This packet consolidates the current graphics-only Level-B same-source evidence:

```text
Goal5291: Dragon -> HappyBuddha candidate matrix.
Goal5298: author-only graphics value precheck for four public graphics cases.
Goal5299: RTDL comparison for ThaiStatuette scaled -> HappyBuddha.
Goal5300: RTDL comparison for ThaiStatuette scaled -> AsianDragon scaled.
```

This packet does **not** ask for approval of exact paper dataset reproduction,
full Figure 5 reproduction, full X-HD paper reproduction, or author-vs-RTDL
performance ratios.

## Files Under Review

```text
history/internal_docs/goal5291_xhd_figure5_dragon_happy_candidate_matrix_result_2026-07-09.md
history/internal_docs/call_for_review_goal5291_xhd_figure5_dragon_happy_candidate_matrix_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5291_figure5_dragon_happy_candidate_matrix_2026-07-09.json
tests/goal5291_xhd_figure5_dragon_happy_candidate_matrix_test.py

history/internal_docs/goal5298_xhd_author_graphics_precheck_result_2026-07-09.md
history/internal_docs/call_for_review_goal5298_xhd_author_graphics_precheck_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5298_author_graphics_precheck_summary_pod.json
tests/goal5298_xhd_author_graphics_precheck_test.py

history/internal_docs/goal5299_xhd_thai_happy_rtdl_comparison_result_2026-07-09.md
history/internal_docs/call_for_review_goal5299_xhd_thai_happy_rtdl_comparison_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_level_b_rtdl_comparison_matrix_2026-07-09.json
tests/goal5299_xhd_thai_happy_rtdl_comparison_test.py

history/internal_docs/goal5300_xhd_thai_asian_rtdl_comparison_result_2026-07-09.md
history/internal_docs/call_for_review_goal5300_xhd_thai_asian_rtdl_comparison_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_level_b_rtdl_comparison_matrix_2026-07-09.json
tests/goal5300_xhd_thai_asian_rtdl_comparison_test.py
```

## Evidence Summary

Author-only precheck:

```text
case                       author HDResult        paper-log HDResult      matched
Dragon -> HappyBuddha       0.12572988867759705    0.12572969496250153    true
Dragon -> Asian scaled      0.06545527279376984    0.06536811590194702    false
Thai scaled -> HappyBuddha  0.21912431716918945    0.21912434697151184    true
Thai scaled -> Asian scaled 0.28763842582702637    0.28763845562934875    true
```

RTDL comparison evidence:

```text
Dragon -> HappyBuddha:
  author rerun = 0.12572988867759705
  RTDL route   = 0.12572988629271128
  abs diff     ~= 2.38e-9
  caveat       = Goal5211/5212 fast scalar route has approximate per-source
                 witnesses for early-aborted sources.

Thai scaled -> HappyBuddha:
  author rerun       = 0.21912431716918945
  RTDL exact-witness = 0.2191243235042005, route ~= 5.00s, witness exact
  RTDL fast-scalar   = 0.2191243235042005, route ~= 1.00s, witness approximate

Thai scaled -> Asian scaled:
  author rerun       = 0.28763842582702637
  RTDL exact-witness = 0.2876384148709406, route ~= 10.76s, witness exact
  RTDL fast-scalar   = 0.2876384148709406, route ~= 12.51s, witness approximate
```

Important negative evidence:

```text
Dragon -> AsianDragon scaled is not value-matched and must not be used for
Figure 5 performance comparison under current input mapping.
```

## Claim Boundary

Allowed summary:

```text
The current public Stanford graphics Level-B evidence contains three
value-matched same-source author rerun cases. RTDL has scalar-directed-HD
matches for Dragon->HappyBuddha, Thai->HappyBuddha, and Thai->Asian, with
exact-witness routes available for the two Thai cases. This remains Level-B
same-source evidence only.
```

Forbidden summaries:

```text
Figure 5 reproduced.
Full X-HD paper reproduced.
Exact paper graphics datasets recovered.
RTDL matches author performance.
RTDL is faster/slower than author by ratio X.
Fast-scalar always faster than exact-witness.
Fast-scalar provides exact per-source witnesses.
Dragon->Asian is a valid value-matched Figure 5 candidate.
```

## Review Questions

1. Does Goal5298 correctly identify three value-matched graphics Level-B
   candidates and one no-go candidate?
2. Is Dragon -> HappyBuddha correctly classified as Level-B value-matched
   evidence, not exact Figure 5 reproduction?
3. Do Goals5299 and 5300 correctly compare RTDL scalar HDResult to author rerun
   and paper-log scalar values?
4. Is exact-witness correctly classified as per-source witness exact for the two
   Thai cases?
5. Is fast-scalar correctly classified as scalar-only / approximate-witness
   evidence?
6. Is the Goal5300 observation correct that fast-scalar is slower than
   exact-witness on Thai -> Asian, so the route label is not a universal speed
   guarantee?
7. Is the refusal to report author-vs-RTDL performance ratios correct across
   the packet?
8. Is the packet boundary correct: graphics Level-B evidence only, no Figure 5
   reproduction, no exact paper dataset status, no full paper reproduction?
9. Should this packet be closed as the current public graphics Level-B evidence
   set?

## Expected Answer Shape

```text
Verdict:
  approve_goals5291_5300_xhd_graphics_level_b_packet__three_value_matched_rtdl_cases_no_ratio
  OR revise_graphics_level_b_packet_claim_boundary_or_witness_status
  OR block_graphics_level_b_packet_due_to_incorrect_value_or_evidence

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
```
