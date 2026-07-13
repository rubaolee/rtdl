# Goal5136 - X-HD Stanford Graphics Sample Scaling Result

## Verdict

`xhd_stanford_graphics_sample_scaling_2048_matched__exact_route_scaling_floor_exposed`

## Purpose

Goal5136 extends the Level B Stanford graphics PLY gate beyond sample256 to
sample1024 and sample2048, then uses the observed RTDL exact-route scaling to
decide whether to keep pushing exact-reference sample size or switch to X-HD
algorithmic route gap analysis.

## Inputs

Samples are deterministic even-index samples from Stanford res4 PLY files:

```text
Dragon source: dragon_vrip_res4.ply, 5205 vertices
Happy source:  happy_vrip_res4.ply, 7108 vertices
```

Sample artifacts:

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_dragon_res4_sample1024.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_happy_res4_sample1024.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_dragon_res4_sample2048.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_happy_res4_sample2048.ply
```

## Results

All comparisons use:

```text
author_comparison_reference = directed_a_to_b
reference_preprocessing = ["translate_each_input_to_min_bound"]
tolerance = 1e-6
```

| Sample | Pair rows | Author HDResult | RTDL directed A->B | abs diff | matched | Author AvgTime | RTDL route |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 256 x 256 | 65,536 | 0.11612465232610703 | 0.11612464969699586 | 2.63e-9 | true | 4.04 ms | 0.068 s |
| 1024 x 1024 | 1,048,576 | 0.1215052381157875 | 0.1215052343959716 | 3.72e-9 | true | 4.298 ms | 3.753 s |
| 2048 x 2048 | 4,194,304 | 0.12136761099100113 | 0.12136761603270661 | 5.04e-9 | true | 4.202 ms | 33.001 s |

Result artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample1024_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample1024_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample1024_rtdl_route_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample2048_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample2048_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample2048_rtdl_route_summary.json
```

## Interpretation

The correctness story improved:

- the author binary matches the RTDL directed reference on three Stanford-derived
  PLY samples;
- the discovered PLY preprocessing contract is stable across sample sizes;
- this is a real Level B same-source graphics correctness line, not just a tiny
  synthetic fixture.

The scalability story is also clear:

- RTDL's current route is an exact pairwise reference path;
- it materializes all candidate pairs;
- 1024 x 1024 already costs about `3.75s`;
- 2048 x 2048 costs about `33s`;
- res4 full (`5205 x 7108 ~= 37M` pairs) would be much larger;
- full-resolution Dragon x HappyBuddha (`437645 x 543652 ~= 238B` pairs) is not
  a viable target for this exact-reference route.

Therefore continuing to increase exact-reference sample size is low value. The
next meaningful work is X-HD algorithmic gap analysis / implementation planning:

- grid grouping;
- radius growth;
- pruning by bounds;
- RT nearest-cell traversal;
- heavy-cell offload;
- adaptive grid sizing;
- memory accounting.

## Verification

Regression command:

```text
py -m unittest tests.goal5111_xhd_author_json_gate_test \
  tests.goal5115_xhd_rtdl_route_gate_test \
  tests.goal5118_xhd_bounded3d_rtdl_route_gate_test \
  tests.goal5127_xhd_generic_nearest_pipeline_extraction_test \
  tests.goal5128_non_hausdorff_max_nearest_consumer_test \
  tests.goal5133_xhd_ply_input_bridge_test \
  tests.goal5134_xhd_ply_sample_gate_packet_test
```

Result:

```text
Ran 23 tests in 0.289s
OK
```

## Claim Boundary

This goal claims:

- Level B Stanford graphics correctness gates matched at sample sizes 256, 1024,
  and 2048;
- the author PLY min-bound translation contract remained stable;
- the current RTDL exact-reference route is not a scalable full-resolution route.

This goal does **not** claim:

- exact paper dataset reproduction;
- full-resolution Dragon / HappyBuddha reproduction;
- Figure 5 reproduction;
- fair author-vs-RTDL performance ratio;
- author performance parity;
- X-HD RT-core algorithmic reproduction.

## Next

Goal5137 should be X-HD algorithmic route gap analysis for the graphics path.
The exact-reference route has served its correctness role; it should not be used
as the main full-resolution performance route.
