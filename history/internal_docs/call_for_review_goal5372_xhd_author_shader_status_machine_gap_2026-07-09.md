# Call For Review - Goal5372 X-HD Author Shader Status-Machine Gap

Date: 2026-07-09

Please strictly review Goal5372:

```text
history/internal_docs/goal5372_xhd_author_shader_status_machine_gap_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5372_author_shader_status_machine_gap.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5372_author_shader_status_machine_gap.py
tests/goal5372_author_shader_status_machine_gap_test.py
```

## Context

The current X-HD `-lb` line has rejected simpler explanations for author
`OffloadingSize`:

```text
author OffloadingSize                         = 27,133,990
RTDL author-radius materialized rows          = 21,006,960
RTDL author-radius inline count-only kind2    = 21,006,960
RTDL inline + existing global-bound kind2     = 21,006,960
RTDL author-radius no-inline raw kind2        = 304,981,889
```

Therefore the next real target is author shader payload/status-machine
semantics, not scalar radius, materialization, raw kind2, or the existing RTDL
global-bound flag.

## Requested Review Questions

1. Does Goal5372 correctly pin the author shader payload fields and status bits
   from the author source?
2. Does it correctly identify the critical branches that affect
   `OffloadingSize`: radius/cmin2 prune, cmax2 abort, heavy-cell offload append,
   point-loop early break, valid complete source, and miss source?
3. Does it correctly include `loadBalanceProcessing` as part of the author
   state machine rather than treating `OffloadingSize` as an isolated row count?
4. Does the gap matrix accurately state what RTDL currently has and what is
   missing for Dragon -> AsianDragon `lb256` denominator parity?
5. Does the next gate contract require the right fields:
   active queue size, raw offload rows before sort/reduce, status counts,
   cmax2 abort counts, miss count, current-best state source, and row-count
   parity?
6. Does the goal avoid promoting Goal5370's app-owned queue-state reference to
   RTDL core API?
7. Does it avoid claiming explicit `-lb` support, row-count parity, Figure 7/11
   reproduction, author RT-core parity, performance ratio, exact paper dataset
   reproduction, or full X-HD reproduction?
8. Is the proposed next step correct: either implement a generic experimental
   status-machine probe or instrument/regenerate author to produce the stronger
   oracle?

## Expected Answer Shape

```text
Verdict:
  approve_goal5372_author_shader_status_machine_gap_matrix
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  2. ...
  ...
```

## Requested Verdict Label

```text
approve_goal5372_author_shader_status_machine_gap_matrix
```
