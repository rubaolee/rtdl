# Consolidated Call For Review - X-HD Goals5130-5136 Level-B Graphics Scaling Packet

Please strictly review the X-HD Level-B graphics line covering Goals5130-5136.

## Files To Review

Planning and provenance:

```text
history/internal_docs/goal5130_xhd_paper_target_matrix_2026-07-08.md
history/internal_docs/goal5131_xhd_dataset_provenance_acquisition_matrix_2026-07-08.md
history/internal_docs/goal5132_xhd_stanford_graphics_same_source_acquisition_2026-07-08.md
```

Input bridge and sample gates:

```text
history/internal_docs/goal5133_xhd_ply_input_bridge_result_2026-07-08.md
history/internal_docs/goal5134_xhd_stanford_graphics_sample_ply_gate_packet_2026-07-08.md
history/internal_docs/goal5135_xhd_stanford_graphics_sample_ply_author_gate_result_2026-07-08.md
history/internal_docs/goal5136_xhd_stanford_graphics_sample_scaling_result_2026-07-08.md
```

Code and tests:

```text
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/prepare_xhd_ply_sample.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_route_gate.py
tests/goal5133_xhd_ply_input_bridge_test.py
tests/goal5134_xhd_ply_sample_gate_packet_test.py
```

Key result artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_stanford_graphics_acquisition_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample1024_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample2048_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_rtdl_route_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample1024_rtdl_route_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample2048_rtdl_route_summary.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Claims Under Review

1. Exact X-HD paper inputs remain unavailable in current evidence.
2. Stanford Dragon/HappyBuddha are valid Level B same-source graphics candidates.
3. ASCII PLY support was added at the app layer, not as an RTDL core primitive.
4. Author PLY comparison requires explicit per-input min-bound translation.
5. Author `hd_exec` matches RTDL directed reference on Stanford-derived PLY
   samples of size 256, 1024, and 2048.
6. Values:

```text
sample256:
  author = 0.11612465232610703
  RTDL   = 0.11612464969699586
  diff   = 2.63e-9
  matched = true

sample1024:
  author = 0.1215052381157875
  RTDL   = 0.1215052343959716
  diff   = 3.72e-9
  matched = true

sample2048:
  author = 0.12136761099100113
  RTDL   = 0.12136761603270661
  diff   = 5.04e-9
  matched = true
```

7. RTDL exact-reference route scaling exposes a floor:

```text
sample1024 RTDL route ~= 3.75s
sample2048 RTDL route ~= 33.00s
```

8. Therefore the exact-reference route is a correctness route, not the
   full-resolution performance route.

## Claims Not Authorized

- exact paper dataset reproduction;
- full-resolution Dragon / HappyBuddha reproduction;
- Figure 5 reproduction;
- fair author-vs-RTDL performance ratio;
- author performance parity;
- X-HD RT-core algorithmic reproduction.

## Critical Review Questions

1. Are the Level B vs Level C boundaries preserved throughout?
2. Is the Stanford source acquisition evidence sufficient for same-source
   graphics selection?
3. Is the discovered min-bound preprocessing contract justified and explicit?
4. Do sample256/1024/2048 all genuinely match author `HDResult` under the
   directed input1-to-input2 contract?
5. Does the report avoid using author `Running.AvgTime` as a fair comparison
   against RTDL local exact-reference route time?
6. Does the scaling evidence justify stopping the exact-reference sample-size
   climb?
7. Is the next recommended goal correctly identified as X-HD algorithmic route
   gap analysis rather than full-resolution exact-reference execution?
8. Are there any overclaims or hidden exact-paper/performance claims?

## Expected Answer Shape

```text
Verdict: approve | approve_with_required_amendments | block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to 8 review questions:
1. ...
...
8. ...
```

## Requested Verdict Label

If acceptable:

```text
approve_goals5130_5136_xhd_level_b_graphics_scaling__algorithmic_gap_next
```
