# Call For Review - Goal5268 X-HD Figure 6 Pruning Phase/Counter Mapping

Date: 2026-07-09

## Scope

Strictly review Goal5268, which starts the first substantive X-HD paper-figure
target after the user-facing entrypoint work:

```text
Figure 6 - pruning effectiveness on Dragon -> AsianDragon
```

This goal is **not** claiming Figure 6 reproduction. It maps the author source,
flags, script variants, and profiling JSON counters, then runs the author
Figure-6-style variants on the current Level-B public same-source/scaled
Dragon -> AsianDragon candidate.

## Files To Review

```text
history/internal_docs/goal5268_xhd_figure6_pruning_phase_counter_mapping_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_figure6_pruning_phase_counter_mapping_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_fig6_noopt_dragon_asian_scaled_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_fig6_eb_dragon_asian_scaled_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_fig6_eb_prune_dragon_asian_scaled_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_fig6_xhd_dragon_asian_scaled_profile_pod.json
tests/goal5268_xhd_figure6_pruning_mapping_test.py
```

## Key Facts To Verify

1. The author-source mapping is real and relevant:
   `--eb`, `--prune`, `--lb`, and `--profiling` exist in the author flags;
   `RunConfig` receives those flags; profiling JSON exposes `Hits` and
   `ComparedPoints` in addition to timing/offload fields.
2. The goal correctly identifies the Figure-6-style author variant sequence:
   no optimization, early break, early break plus prune, and full X-HD
   load-balancing with `lb=256`, while noting that the external RT-HDIST
   baseline is unavailable in the current evidence chain.
3. The first three author profiling variants on the current Level-B scaled
   candidate remain correctness-clean against the author reference HD:
   noopt, EB, and EB+Prune all report `matches_author_reference=true`.
4. The LB=256/full-XHD profiling variant is **not** correctness-clean on this
   Level-B scaled candidate:
   `check=true` aborts with `Wrong HausdorffDistance`, while `check=false`
   reports a different HDResult.
5. The report therefore refuses to claim Figure 6 reproduction, full paper
   reproduction, exact paper byte-input identity, author RT-core equivalence,
   or any author/RTDL performance ratio.

## Review Questions

1. Does Goal5268 correctly map the author Figure 6 flags/script/counter fields?
2. Are the four downloaded POD profiling JSON artifacts sufficient evidence for
   the stated mapping and caveat?
3. Is it correct to treat noopt, EB, and EB+Prune as usable phase/counter
   evidence on this Level-B scaled candidate?
4. Is it correct to block any Figure 6 reproduction claim because the
   LB=256/full-XHD profiling variant fails `check=true` on this candidate?
5. Does the packet keep Level-B same-source/scaled evidence separate from exact
   paper byte-input identity?
6. Does the packet avoid performance-ratio or author-parity overclaiming?
7. Is the recommended next goal right: resolve the LB=256/full-XHD correctness
   issue before attempting a Figure 6 plot/table?

## Expected Verdict Labels

Approve:

```text
approve_goal5268_figure6_mapping_ready__figure6_not_reproduced
```

Require amendments:

```text
revise_goal5268_before_using_figure6_evidence
```

Block:

```text
block_goal5268_due_to_figure6_overclaim_or_invalid_counter_mapping
```

## Expected Answer Shape

Please answer with:

```text
Verdict: <label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers:
1. ...
2. ...
...
7. ...
```
