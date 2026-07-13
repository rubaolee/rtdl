# Consolidated Call For Review - X-HD Goals5130-5133 Full-Reproduction Feasibility Node

Please strictly review the X-HD full-paper-reproduction feasibility node covering
Goals5130-5133.

## Files To Review

Goal5130:

```text
history/internal_docs/goal5130_xhd_paper_target_matrix_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
```

Goal5131:

```text
history/internal_docs/goal5131_xhd_dataset_provenance_acquisition_matrix_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_dataset_provenance_matrix_2026-07-08.json
```

Goal5132:

```text
history/internal_docs/goal5132_xhd_stanford_graphics_same_source_acquisition_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_stanford_graphics_acquisition_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/external/README.md
Paper-reproduction-apps/x-hd-paper/data/external/stanford/README.md
```

Goal5133:

```text
history/internal_docs/goal5133_xhd_ply_input_bridge_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_route_gate.py
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny3d_ply_a.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny3d_ply_b.ply
Paper-reproduction-apps/x-hd-paper/results/tiny3d_ply_local_reference_summary.json
Paper-reproduction-apps/x-hd-paper/results/tiny3d_ply_rtdl_route_summary.json
tests/goal5133_xhd_ply_input_bridge_test.py
```

Shared state:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## What This Node Claims

1. The X-HD paper targets are now decomposed into Table 1 and Figure 5-11
   targets.
2. Exact paper inputs are not available in current evidence.
3. Same-source public candidates are identified.
4. Stanford Dragon and HappyBuddha source archives were acquired, hashed, and
   inspected as Level B same-source graphics candidates.
5. The paper app now has an app-owned ASCII PLY input bridge and parameterized
   `--input-type wkt|ply` gates.
6. A tiny PLY local smoke proves the RTDL public 3D column route can consume PLY
   and match exact reference.

## What This Node Does Not Claim

- full X-HD paper reproduction;
- exact paper dataset reproduction;
- paper Figure 5 graphics reproduction;
- author `hd_exec` success on Stanford Dragon/HappyBuddha;
- RTDL success on full-resolution Stanford Dragon/HappyBuddha;
- X-HD RT-core algorithmic reproduction;
- author performance parity;
- any performance ratio.

## Critical Review Questions

1. Are Goals5130/5131 honest about the Level B vs Level C boundary, especially
   the rule that count/Gini/statistical matching is not enough for exact paper
   input reproduction?
2. Is the paper target matrix complete enough to guide future Figure 5-11 work?
3. Is Dragon-HappyBuddha a reasonable first Level B graphics path?
4. Does Goal5132 properly record source URLs, byte sizes, hashes, and PLY header
   counts without upgrading them to exact paper evidence?
5. Is it correct to state that current full-resolution Dragon x HappyBuddha is
   not viable for the exact pairwise RTDL reference route because it would
   materialize roughly 238 billion candidate pairs?
6. Is the PLY input bridge app-owned and free of RTDL core pollution?
7. Do the gate runners preserve WKT behavior while adding PLY support?
8. Are the tiny PLY smoke summaries enough to prove the bridge, while correctly
   not claiming author success?
9. Does the manifest/register accurately mark Goals5130-5133 as implemented /
   review pending, with no hidden performance or paper claims?
10. Should the next authorized goal be a bounded PLY POD gate, not a
    full-resolution or performance gate?

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
approve_goals5130_5133_xhd_full_reproduction_feasibility_node__level_b_ply_ready
```
