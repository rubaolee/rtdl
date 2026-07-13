# Call For Review - Goal5166 X-HD Full Public Res4 Level-B Scaling

Please strictly review Goal5166.

## Files

```text
history/internal_docs/goal5166_xhd_res4full_scaling_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
tests/goal5166_xhd_res4full_scaling_test.py
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

Fixtures and summaries:

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_dragon_res4_full.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_happy_res4_full.ply
Paper-reproduction-apps/x-hd-paper/results/stanford_dragon_res4_full_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_happy_res4_full_summary.json
```

POD artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_post_goal5163_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/perf_res4full_author_hd_exec_output_pod.json
```

## Claims Under Review

1. Goal5166 adds normalized full public Stanford res4 fixtures:

```text
Dragon res4:       5205 points
HappyBuddha res4:  7108 points
```

2. These fixtures remain Level B same-source representative evidence, not exact
   paper inputs.
3. The current post-Goal5163 OptiX route supports `res4full`.
4. The same-POD production-style matrix matched author HDResult:

```text
author HDResult = 0.1241602823138237
RTDL author_comparison_distance = 0.12416027787377293
author_abs_diff = 4.440050771492565e-09
matched = true
```

5. The full-res4 route median is:

```text
RTDL route median = 0.059233590960502625 s
RTDL total median = 0.0998341366648674 s
author Running.AvgTime = 4.56 ms
author process wall = 1.1186843365430832 s
```

6. No author-vs-RTDL speedup/parity ratio is authorized.
7. This is the strongest current public Stanford Level B scaling evidence, but
   still not full X-HD paper reproduction.

## Review Questions

1. Are the full res4 fixtures correctly classified as Level B same-source
   representative inputs rather than exact paper datasets?
2. Does the runner change remain a simple case addition rather than an
   app-specific shortcut in RTDL core?
3. Does the POD artifact prove author HDResult matching for the full public
   res4 pair under the existing directed input1-to-input2 and min-bound
   preprocessing contract?
4. Does the result preserve the no-ratio/no-parity claim boundary?
5. Is it fair to treat full-res4 as the latest scaling/profile point after
   Goal5165, not as full paper reproduction?
6. Does the phase breakdown support choosing future performance targets from
   fresh full-res4 profile evidence?
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
approve_goal5166_xhd_full_public_res4_level_b_scaling__no_ratio_no_full_paper_claim
```
