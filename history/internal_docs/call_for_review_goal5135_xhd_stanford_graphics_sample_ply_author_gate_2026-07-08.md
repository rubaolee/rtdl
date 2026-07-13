# Call For Review - Goal5135 X-HD Stanford Graphics Sample PLY Author Gate

Please strictly review Goal5135.

## Files To Review

```text
history/internal_docs/goal5135_xhd_stanford_graphics_sample_ply_author_gate_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_route_gate.py
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_rtdl_route_summary.json
tests/goal5133_xhd_ply_input_bridge_test.py
tests/goal5134_xhd_ply_sample_gate_packet_test.py
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Review Questions

1. Did the author `hd_exec` actually run on POD and produce an `HDResult` for
   the Stanford sample256 PLY pair?
2. Is the initial raw-coordinate mismatch honestly reported?
3. Is the inferred preprocessing contract justified by the author JSON MBR lower
   bounds and the successful min-bound translated comparator?
4. Is `--translate-each-input-to-min-bound` implemented as an explicit gate
   option rather than hidden behavior?
5. Does the final author gate correctly match under that explicit preprocessing
   with `abs_diff <= 1e-6`?
6. Does the RTDL route summary also match exact reference under the same
   preprocessing?
7. Does the report avoid claiming exact paper dataset reproduction, Figure 5
   reproduction, performance ratio, or X-HD RT-core algorithmic reproduction?
8. Is the result correctly labeled Level B same-source bounded sample
   correctness?
9. Are the tests sufficient to guard the PLY bridge and preprocessing helper?
10. Should the next step be a decision between larger reduced-resolution gates
    and X-HD algorithmic gap analysis, rather than jumping to full-resolution
    performance?

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
approve_goal5135_xhd_stanford_graphics_sample_ply_author_gate_matched
```
