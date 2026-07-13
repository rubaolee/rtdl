# Call For Review: Goal5490 LibRTS Numeric WKT Loader No-Go

Please review this bounded app-owned no-go. The implementation adds an
experimental numeric WKT parser, but the result does not demonstrate a
material load improvement. No RTDL core API or WKT semantics were added.

## Files

- implementation:
  `Paper-reproduction-apps/librts-paper/run_exact_point_contains_count_gate.py`
- runner:
  `Paper-reproduction-apps/librts-paper/run_exact_point_contains_prepared_phase_columns_repeat.py`
- test: `tests/goal5489_librts_prepared_phase_repeat_test.py`
- result:
  `Paper-reproduction-apps/librts-paper/results/librts_goal5490_dtl_cnty_numeric_loader.json`
- report:
  `history/internal_docs/goal5490_librts_numeric_wkt_loader_no_go_result_2026-07-12.md`

## Review questions

1. Does the numeric loader emit columns equivalent to the existing loader on
   polygon and multipolygon fixtures?
2. Does the POD result use exact archive-derived files and match the author
   count on all three repeats?
3. Is the comparison correctly described as separate-run evidence without a
   performance regression or speedup claim?
4. Is rejecting further lakes numeric-loader work without a demonstrated
   small-case benefit a sound stop-loss decision?
5. Does the code keep WKT parsing app-owned and leave RTDL core generic?
6. Are all claims about Figure 6, pointwise relations, author parity, ratios,
   device zero-copy, full paper reproduction, and Embree closed?

## Expected answer shape

```text
Verdict: approve_no_go | revise
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
```
