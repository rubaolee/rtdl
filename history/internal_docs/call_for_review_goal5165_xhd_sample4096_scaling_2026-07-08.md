# Call For Review - Goal5165 X-HD Sample4096 Level-B Scaling

Please strictly review Goal5165.

## Files

```text
history/internal_docs/goal5165_xhd_sample4096_scaling_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
tests/goal5165_xhd_sample4096_scaling_test.py
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

Fixtures and summaries:

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_dragon_res4_sample4096.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_happy_res4_sample4096.ply
Paper-reproduction-apps/x-hd-paper/results/stanford_dragon_res4_sample4096_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_happy_res4_sample4096_summary.json
```

POD artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample4096_post_goal5163_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/perf_sample4096_author_hd_exec_output_pod.json
```

## Claims Under Review

1. Goal5165 adds deterministic 4096-point Level B Stanford graphics fixtures
   from public Dragon/HappyBuddha res4 PLYs.
2. The current post-Goal5163 OptiX route supports `sample4096`.
3. The same-POD production-style matrix matched author HDResult:

```text
author HDResult = 0.12403063476085663
RTDL author_comparison_distance = 0.12403064103157131
author_abs_diff = 6.270714683620504e-09
matched = true
```

4. The sample4096 route median is:

```text
RTDL route median = 0.041182391345500946 s
RTDL total median = 0.06723665446043015 s
author Running.AvgTime = 4.301 ms
author process wall = 1.1219238340854645 s
```

5. No author-vs-RTDL speedup/parity ratio is authorized.
6. This is Level B same-source representative scaling evidence, not exact paper
   dataset reproduction and not full paper reproduction.

## Review Questions

1. Are the sample4096 fixtures correctly classified as Level B same-source
   representative samples rather than exact paper inputs?
2. Does the runner change remain a simple case addition rather than an
   app-specific shortcut in RTDL core?
3. Does the POD artifact prove author HDResult matching for sample4096 under
   the existing directed input1-to-input2 and min-bound preprocessing contract?
4. Does the result preserve the no-ratio/no-parity claim boundary?
5. Is it fair to treat sample4096 as an expanded scaling/profile point after
   Goal5164, not as a new full-reproduction milestone?
6. Does the phase breakdown support the conclusion that the current route is
   relatively balanced and that future performance work should be selected from
   fresh profile evidence?
7. Are the tests and manifest/register updates sufficient for this bounded
   goal?

## Expected Verdict Shape

```text
verdict_label:
blocking_findings:
required_amendments:
non_blocking_notes:
answers:
  1. ...
  ...
  7. ...
```

Suggested approval label:

```text
approve_goal5165_xhd_sample4096_level_b_scaling__no_ratio_no_full_paper_claim
```
