# Consolidated Call For Review - X-HD Goals5130-5135 Level-B Graphics Author Gate Packet

Please strictly review the X-HD Level-B graphics reproduction packet covering
Goals5130-5135.

## Files To Review

Planning / provenance:

```text
history/internal_docs/goal5130_xhd_paper_target_matrix_2026-07-08.md
history/internal_docs/goal5131_xhd_dataset_provenance_acquisition_matrix_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_dataset_provenance_matrix_2026-07-08.json
```

Stanford source acquisition:

```text
history/internal_docs/goal5132_xhd_stanford_graphics_same_source_acquisition_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_stanford_graphics_acquisition_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/external/README.md
Paper-reproduction-apps/x-hd-paper/data/external/stanford/README.md
```

PLY bridge and gate packet:

```text
history/internal_docs/goal5133_xhd_ply_input_bridge_result_2026-07-08.md
history/internal_docs/goal5134_xhd_stanford_graphics_sample_ply_gate_packet_2026-07-08.md
history/internal_docs/goal5135_xhd_stanford_graphics_sample_ply_author_gate_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/prepare_xhd_ply_sample.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_route_gate.py
tests/goal5133_xhd_ply_input_bridge_test.py
tests/goal5134_xhd_ply_sample_gate_packet_test.py
```

Result artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/stanford_dragon_res4_sample256_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_happy_res4_sample256_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_rtdl_route_summary.json
```

Shared state:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Claims Under Review

1. Exact paper inputs are still unavailable; this is Level B same-source evidence.
2. Stanford Dragon / HappyBuddha public meshes were acquired and hashed.
3. A deterministic sample256 PLY pair was generated from Stanford res4 meshes.
4. The author `hd_exec` ran on POD on that sample PLY pair.
5. The first raw-coordinate comparator failed, revealing a preprocessing
   mismatch.
6. The author PLY path reports MBR lower bounds at zero; explicit
   `translate_each_input_to_min_bound` preprocessing makes the RTDL directed
   reference match author `HDResult`.
7. Final values:

```text
author HDResult = 0.11612465232610703
RTDL directed input1->input2 = 0.11612464969699586
abs_diff = 2.6291111648868437e-09
tolerance = 1e-6
matched = true
rtdl_matches_exact_reference = true
```

8. The result is a bounded Level B graphics correctness gate, not exact paper or
   performance reproduction.

## Claims Not Authorized

- exact paper dataset reproduction;
- full-resolution Dragon / HappyBuddha reproduction;
- Figure 5 graphics reproduction;
- author-vs-RTDL performance ratio;
- author performance parity;
- X-HD RT-core algorithmic reproduction.

## Critical Review Questions

1. Are the Level B vs Level C boundaries preserved?
2. Is the Stanford source acquisition evidence sufficient for same-source
   graphics selection?
3. Is deterministic sample256 a reasonable bounded gate, while not being
   confused with exact paper input?
4. Is the author POD evidence real and correctly recorded?
5. Is the raw-coordinate mismatch honestly reported?
6. Is `translate_each_input_to_min_bound` a justified explicit preprocessing
   contract for this PLY author comparison?
7. Does the final matched summary use the established directed input1-to-input2
   contract?
8. Does the RTDL route summary prove RTDL-vs-exact-reference agreement under the
   same preprocessing?
9. Are tests sufficient, and did the change preserve earlier WKT gates?
10. Should the next step be algorithmic gap analysis or carefully larger
    reduced-resolution gates, not full-resolution performance claims?

## Expected Answer Shape

```text
Verdict: approve | approve_with_required_amendments | block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to 10 review questions:
1. ...
...
10. ...
```

## Requested Verdict Label

If acceptable:

```text
approve_goals5130_5135_xhd_level_b_graphics_author_gate_matched
```
