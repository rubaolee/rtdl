# Goal5135 - X-HD Stanford Graphics Sample PLY Author Gate

## Verdict

`xhd_stanford_graphics_sample_ply_author_gate_matched`

## Purpose

Goal5135 executes the author `hd_exec` gate for the Level B Stanford graphics
sample PLY packet prepared in Goal5134, then compares author `HDResult` with the
RTDL directed input1-to-input2 reference under the author PLY preprocessing
contract.

This is a Level B same-source bounded sample gate. It is not exact paper dataset
reproduction, not Figure 5 reproduction, and not a performance result.

## Inputs

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_dragon_res4_sample256.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_happy_res4_sample256.ply
```

The samples were deterministically generated from public Stanford res4 PLY files:

```text
deterministic_even_index_sample_including_first_and_last
```

## Author POD Run

POD:

```text
root@213.173.108.24 -p 13502
GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
```

Author binary:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

Command:

```text
python3 run_xhd_author_json_gate.py \
  --input1 stanford_dragon_res4_sample256.ply \
  --input2 stanford_happy_res4_sample256.ply \
  --n-dims 3 \
  --input-type ply \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --author-json stanford_graphics_sample256_author_hd_exec_output_pod.json \
  --summary stanford_graphics_sample256_author_gate_summary_pod.json \
  --tolerance 1e-6
```

The raw author run succeeded:

```text
author_run.returncode = 0
author HDResult = 0.11612465232610703
author Running.AvgTime = 4.04 ms
```

## Preprocessing Contract Discovered

The first comparator attempt using raw PLY coordinates failed:

```text
author HDResult = 0.11612465232610703
raw RTDL directed_a_to_b = 0.07136699450130711
matched = false
```

The author JSON reports both input MBR lower bounds as `0.0`, while the Stanford
PLY coordinates have non-zero / negative coordinate minima. Recomputing the
RTDL reference after translating each input independently to its coordinate-wise
minimum bound matches the author result:

```text
translate_each_input_to_min_bound
RTDL directed_a_to_b = 0.11612464969699586
abs_diff = 2.6291111648868437e-09
matched = true
```

This preprocessing is now an explicit gate option:

```text
--translate-each-input-to-min-bound
```

It is documented in the result summaries as:

```text
reference_preprocessing = ["translate_each_input_to_min_bound"]
```

## Result Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_rtdl_route_summary.json
```

Key values:

```text
point_count_a = 256
point_count_b = 256
author_comparison_reference = directed_a_to_b
author_hd_result = 0.11612465232610703
rtdl_author_comparison_distance = 0.11612464969699586
abs_diff = 2.6291111648868437e-09
tolerance = 1e-6
matched = true
rtdl_matches_exact_reference = true
```

RTDL route diagnostic:

```text
directed_a_to_b = 0.11612464969699586
directed_b_to_a = 0.06962366802783376
```

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
Ran 23 tests in 0.266s
OK
```

## Claim Boundary

This goal claims:

- author `hd_exec` successfully ran on the bounded Stanford sample256 PLY pair;
- the author `HDResult` matches the RTDL directed reference after explicit
  author-style min-bound translation preprocessing;
- the result is a Level B same-source bounded sample correctness gate.

This goal does **not** claim:

- exact paper dataset reproduction;
- full-resolution Dragon / HappyBuddha reproduction;
- paper Figure 5 graphics reproduction;
- author performance parity;
- any author-vs-RTDL performance ratio;
- RTDL implementation of the X-HD RT-core algorithm;
- that the author `Running.AvgTime=4.04ms` is comparable to RTDL local route
  time.

## Next

Goal5136 should decide whether to:

1. extend the Level B graphics gate to larger reduced-resolution PLY files, or
2. stop the exact-reference route at sample scale and move to X-HD algorithmic
   gap analysis for scalable graphics reproduction.

The second route is likely required before any full-resolution graphics claim.
