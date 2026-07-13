# Consolidated Call For Review - X-HD Goals5130-5134 Level-B Graphics Feasibility Packet

Please strictly review the X-HD full-reproduction feasibility packet covering
Goals5130-5134.

## Files To Review

Target and provenance:

```text
history/internal_docs/goal5130_xhd_paper_target_matrix_2026-07-08.md
history/internal_docs/goal5131_xhd_dataset_provenance_acquisition_matrix_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_dataset_provenance_matrix_2026-07-08.json
```

Stanford acquisition and PLY bridge:

```text
history/internal_docs/goal5132_xhd_stanford_graphics_same_source_acquisition_2026-07-08.md
history/internal_docs/goal5133_xhd_ply_input_bridge_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_stanford_graphics_acquisition_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/external/README.md
Paper-reproduction-apps/x-hd-paper/data/external/stanford/README.md
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_route_gate.py
tests/goal5133_xhd_ply_input_bridge_test.py
```

Sample gate packet:

```text
history/internal_docs/goal5134_xhd_stanford_graphics_sample_ply_gate_packet_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/scripts/prepare_xhd_ply_sample.py
tests/goal5134_xhd_ply_sample_gate_packet_test.py
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_dragon_res4_sample256.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_happy_res4_sample256.ply
Paper-reproduction-apps/x-hd-paper/results/stanford_dragon_res4_sample256_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_happy_res4_sample256_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_rtdl_route_summary.json
```

Shared state:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Claims Under Review

1. X-HD paper targets are decomposed into dataset/table/figure targets.
2. Exact paper inputs remain unavailable under current evidence.
3. Stanford Dragon/HappyBuddha are valid Level B same-source graphics candidates.
4. Public Stanford archives were downloaded locally, hashed, and inspected.
5. ASCII PLY input support was added at the app layer, not RTDL core.
6. Deterministic sample256 PLY fixtures were created from Stanford res4 files.
7. RTDL public 3D column route matches exact reference on the sample256 PLY pair.
8. Author `hd_exec` has not yet run on this sample; author comparison remains
   pending.

## Claims Not Authorized

- full X-HD paper reproduction;
- exact paper dataset reproduction;
- Figure 5 graphics reproduction;
- author `hd_exec` match on Stanford graphics sample;
- RTDL full-resolution Dragon/HappyBuddha success;
- X-HD RT-core algorithmic reproduction;
- performance ratio or author parity.

## Critical Review Questions

1. Are Level B and Level C boundaries clean, especially "statistics do not prove
   exact paper inputs"?
2. Is the paper target matrix sufficient for future Figure 5-11 planning?
3. Is Stanford Dragon/HappyBuddha a sensible first graphics Level B path?
4. Are source URLs, archive hashes, PLY hashes, and header counts documented
   enough for reproducibility?
5. Is the PLY loader properly app-owned, with no RTDL core pollution?
6. Does the PLY bridge preserve old WKT behavior and fail closed for unsupported
   binary PLY?
7. Is deterministic sample256 an acceptable bounded gate packet, while not being
   confused with exact paper input?
8. Does the RTDL route summary prove only RTDL-vs-exact-reference agreement,
   not author agreement?
9. Is the full-resolution route warning correct: current exact pairwise route is
   not viable for roughly 238B Dragon x HappyBuddha candidate pairs?
10. Should the next authorized step be only Goal5135: run author `hd_exec` on the
    sample PLY pair and compare against the existing directed RTDL reference?

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
approve_goals5130_5134_xhd_level_b_graphics_feasibility_packet__author_gate_pending
```
