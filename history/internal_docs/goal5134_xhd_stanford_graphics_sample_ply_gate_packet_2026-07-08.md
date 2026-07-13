# Goal5134 - X-HD Stanford Graphics Sample PLY Gate Packet

## Verdict

`xhd_stanford_graphics_sample_ply_gate_packet_ready__rtdl_half_passed__author_pod_pending`

## Purpose

Goal5134 prepares the first real Level B same-source graphics gate packet using
Stanford Dragon / HappyBuddha PLY data acquired in Goal5132 and the PLY input
bridge added in Goal5133.

This goal deliberately uses deterministic bounded samples instead of
full-resolution Dragon x HappyBuddha. The current RTDL exact/reference route
materializes pairwise candidate rows; full-resolution Dragon x HappyBuddha would
require roughly `437645 * 543652 ~= 238 billion` candidate pairs and is not a
valid near-term exact-route gate.

## Inputs

Source PLY files:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip_res4.ply
Paper-reproduction-apps/x-hd-paper/data/external/stanford/happy_recon/happy_vrip_res4.ply
```

Deterministic sample fixtures:

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_dragon_res4_sample256.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_happy_res4_sample256.ply
```

Sampling:

```text
deterministic_even_index_sample_including_first_and_last
```

Sample summaries:

```text
Paper-reproduction-apps/x-hd-paper/results/stanford_dragon_res4_sample256_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_happy_res4_sample256_summary.json
```

Sample facts:

| Dataset | Source vertices | Sample vertices | Sample SHA256 |
| --- | ---: | ---: | --- |
| Dragon res4 | 5205 | 256 | `4169139EBB52583F0897D6AB921DC697477DBE052E6BC29F6E530373A9017C10` |
| HappyBuddha res4 | 7108 | 256 | `2E1FF5CFBBA7E8F2526DDABA25A848A27A126E6717DF6FCD318AD517C34557E6` |

## RTDL Route Result

Local RTDL exact/reference route artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_rtdl_route_summary.json
```

Observed:

```text
point_count_a = 256
point_count_b = 256
author_comparison_reference = directed_a_to_b
author_comparison_distance = 0.07136699450130711
rtdl_route.directed_a_to_b.distance = 0.07136699450130711
rtdl_route.directed_b_to_a.distance = 0.07319800210893737
rtdl_matches_exact_reference = true
matched = null
```

`matched=null` is expected because no author JSON has been produced yet for this
sample.

## Verification

New sampler:

```text
Paper-reproduction-apps/x-hd-paper/scripts/prepare_xhd_ply_sample.py
```

New test:

```text
tests/goal5134_xhd_ply_sample_gate_packet_test.py
```

Commands run:

```text
py -m unittest tests.goal5133_xhd_ply_input_bridge_test \
  tests.goal5134_xhd_ply_sample_gate_packet_test

py -m unittest tests.goal5111_xhd_author_json_gate_test \
  tests.goal5115_xhd_rtdl_route_gate_test \
  tests.goal5118_xhd_bounded3d_rtdl_route_gate_test \
  tests.goal5127_xhd_generic_nearest_pipeline_extraction_test \
  tests.goal5128_non_hausdorff_max_nearest_consumer_test \
  tests.goal5133_xhd_ply_input_bridge_test \
  tests.goal5134_xhd_ply_sample_gate_packet_test
```

Results:

```text
Ran 6 tests ... OK
Ran 22 tests ... OK
```

## POD Author Gate Status

The gate packet is ready for author execution:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py \
  --input1 Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_dragon_res4_sample256.ply \
  --input2 Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_happy_res4_sample256.ply \
  --n-dims 3 \
  --input-type ply \
  --author-bin <path-to-hd_exec> \
  --author-json Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_author_hd_exec_output_pod.json \
  --summary Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_author_gate_summary_pod.json \
  --tolerance 1e-6
```

Current POD SSH attempt with the supplied host/port returned:

```text
Permission denied (publickey,password).
```

No author result is claimed until the POD author command succeeds.

## Claim Boundary

This goal claims:

- same-source Stanford graphics sample fixtures are prepared;
- RTDL exact/reference route matches exact reference on the 256 x 256 PLY sample;
- the author POD gate packet is ready.

This goal does **not** claim:

- author `hd_exec` has matched this PLY sample;
- exact paper dataset reproduction;
- full-resolution Dragon / HappyBuddha reproduction;
- paper Figure 5 graphics reproduction;
- performance ratio;
- X-HD RT-core algorithmic reproduction.

## Next

Goal5135 should execute the prepared author PLY gate on POD and compare
author `HDResult` against the established directed input1-to-input2 RTDL
reference.
