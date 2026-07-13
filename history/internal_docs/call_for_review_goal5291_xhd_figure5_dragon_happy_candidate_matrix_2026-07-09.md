# Call For Review - Goal5291 X-HD Figure 5 Dragon -> HappyBuddha Candidate Matrix

Date: 2026-07-09

Please strictly review Goal5291.

## Files Under Review

```text
history/internal_docs/goal5291_xhd_figure5_dragon_happy_candidate_matrix_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5291_figure5_dragon_happy_candidate_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure5_dragon_happy_candidate_matrix.py
tests/goal5291_xhd_figure5_dragon_happy_candidate_matrix_test.py
```

Supporting evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_phase_matrix_goal5188_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_fresh_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
```

## Questions

1. Does the artifact correctly extract the five Figure 5 graphics paper-log
   records for `dragon.ply -> happy_buddha.ply`?
2. Is the value evidence correct?
   - paper log = `0.12572969496250153`
   - author rerun = `0.12572988867759705`
   - RTDL = `0.12572988629271128`
   - all differences within `1e-6`
3. Is it correct to classify this as a Level-B same-source value-matched
   candidate while still refusing exact paper dataset identity?
4. Does the matrix correctly separate paper-log timing, author rerun timing,
   RTDL fresh route timing, and RTDL explicit-warm timing?
5. Is it correct to forbid any author-vs-RTDL performance ratio under current
   evidence?
6. Does the report correctly carry forward the Goal5211/5212 caveat that
   global-bound early break preserves the max-nearest / directed-HD value but
   may make many per-source witnesses approximate?
7. Does the claim boundary avoid Figure 5 reproduction, full matrix
   reproduction, exact paper dataset reproduction, and full paper reproduction
   claims?
8. Should Goals5288-5291 now be reviewed as the current Figure 5 packet, with
   Dragon -> Asian stopped and Dragon -> HappyBuddha promoted only as a
   value-matched Level-B candidate?

## Expected Answer Shape

Please answer with:

```text
verdict_label: ...
blocking_findings:
required_amendments:
non_blocking_notes:
answers:
  Q1: ...
  Q2: ...
  ...
  Q8: ...
```

Acceptable verdict examples:

```text
approve_goal5291_figure5_dragon_happy_value_matched_candidate_ratio_forbidden
revise_goal5291_value_or_denominator_boundary
block_goal5291_due_to_incorrect_value_extraction
```
