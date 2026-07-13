# Call For Review - Goal5186 X-HD Full Public Author hd_exec Gate

Please strictly review Goal5186:

```text
history/internal_docs/goal5186_full_public_author_hd_exec_gate_result_2026-07-08.md
```

Primary evidence:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_author_gate.py
tests/goal5186_xhd_full_public_author_gate_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_hd_exec_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Context

Goals5178-5185 established a Level B public Stanford Dragon/HappyBuddha
candidate and validated bounded RTDL source subsets against exact subset
oracles up to source_limit `8192`.

Goal5186 does something different: it runs the author `hd_exec` binary on the
full public candidate:

```text
dragon_vrip.ply: 437645 points
happy_vrip.ply: 543652 points
```

It then compares the produced author `HDResult` to the author paper-branch log
value for the same workload name:

```text
author HDResult on public full candidate: 0.12572988867759705
paper-branch log HDResult:               0.12572969496250153
abs diff:                                1.9371509552001953e-07
tolerance:                               1e-6
matched:                                 true
```

This is author evidence for the Level B same-source candidate. It is **not** an
RTDL all-source route, exact paper dataset identity, figure reproduction, or
performance ratio.

## Requested Review Questions

1. Does Goal5186 correctly run author `hd_exec` on the full public Stanford
   Dragon/HappyBuddha candidate rather than on the smaller `res4_full` fixture?
2. Does the raw author JSON support the reported values:
   `HDResult=0.12572988867759705`, point counts `[437645, 543652]`,
   `Running.AvgTime=7.823`, and two XHD iterations?
3. Is the comparison to the paper-branch author-log `HDResult` legitimate as
   Level B same-source evidence, with `abs diff ~= 1.94e-7` at `1e-6`
   tolerance?
4. Does the report correctly avoid promoting this to Level C exact paper
   dataset identity, given missing author input bytes/hashes?
5. Does the new script correctly avoid computing any RTDL exact reference or
   full pairwise oracle for the full candidate?
6. Do the tests adequately protect the gate boundary: author JSON vs paper-log
   comparison only, no RTDL exact/all-source claim, no full paper claim?
7. Does the manifest update record the raw author JSON and summary without
   overstating reproduction/performance?
8. Are the author `Running.AvgTime` fields useful as phase evidence but not
   sufficient for an author-vs-RTDL performance ratio?
9. Should Goal5186 close as `implemented_review_pending` with the verdict label
   below, or is any amendment required before it can be queued for the next
   consolidated X-HD review packet?

## Expected Answer Shape

Please answer with:

```text
Verdict: <approve / approve_with_required_amendments / revise / block>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Question answers:
1. ...
2. ...
...
9. ...

Requested verdict label if approved:
approve_goal5186_full_public_author_hd_exec_gate_level_b_only
```

## Non-Authorized Claims

Please fail the review if the package claims any of:

```text
exact paper dataset reproduction
full X-HD paper reproduction
Figure 5 reproduction
RTDL all-source route completion
RTDL exact reference for the full public candidate
author-vs-RTDL speedup/parity/performance ratio
```
