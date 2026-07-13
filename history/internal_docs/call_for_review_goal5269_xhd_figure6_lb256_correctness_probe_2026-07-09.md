# Call For Review - Goal5269 X-HD Figure 6 LB=256 Correctness Probe

Date: 2026-07-09

## Scope

Strictly review Goal5269, which follows Goal5268 by isolating the author
LB=256/full-XHD correctness failure on the current Dragon -> AsianDragon
Level-B candidate.

This goal does **not** claim Figure 6 reproduction. It classifies whether the
failure is compatible with a Level-B candidate/provenance gap and whether any
substitute threshold can be used as Figure 6 evidence.

## Files To Review

```text
history/internal_docs/goal5269_xhd_figure6_lb256_correctness_probe_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5269_figure6_lb256_correctness_probe_2026-07-09.json
tests/goal5269_xhd_figure6_lb256_correctness_probe_test.py
```

Related context:

```text
history/internal_docs/goal5268_xhd_figure6_pruning_phase_counter_mapping_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_figure6_pruning_phase_counter_mapping_2026-07-09.json
```

## Key Facts To Verify

1. The author `run_rt_comparison.sh` script uses
   `/local/storage/shared/HDDatasets/graphics/dragon.ply` and
   `/local/storage/shared/HDDatasets/graphics/asian_dragon.ply` with
   `eb=true`, `prune=true`, `lb=256`, `profiling`, and `check=true`.
2. The current POD does not have that exact `/local/storage/shared/HDDatasets`
   graphics directory.
3. The author paper-branch log records an LB=256 Dragon -> AsianDragon run on
   those exact paths, but the current public/scaled candidate has slightly
   different MBRs despite matching point counts.
4. On the current candidate, `lb=32..1152` gives the same wrong HDResult, while
   `lb>=1280` in the refined scan gives the correct HDResult.
5. `lb=1024 check=true` aborts and `lb=2048 check=true` passes.
6. The packet therefore refuses to treat `lb=2048` as a Figure 6 substitute and
   refuses all Figure 6 / full paper / exact input / performance-ratio claims.

## Review Questions

1. Does the artifact correctly distinguish author exact-path log evidence from
   the current Level-B public/scaled candidate evidence?
2. Is the MBR mismatch sufficient to keep exact paper byte-input identity open?
3. Does the LB threshold scan support the conclusion that LB=256 is not
   correctness-clean on the current candidate?
4. Is it correct to say that `lb=2048` is a correctness-clean diagnostic
   substitute but not a Figure 6 reproduction?
5. Does the packet avoid blaming the author implementation broadly, given that
   the author log has an LB=256 exact-path result while our exact input files
   are unavailable?
6. Does the packet preserve all claim boundaries?
7. Is the recommended next step right: exact-input availability check or a
   separately named Level-B pruning diagnostic, but no Figure 6 plot/table yet?

## Expected Verdict Labels

Approve:

```text
approve_goal5269_lb256_failure_classified__figure6_still_not_reproduced
```

Require amendments:

```text
revise_goal5269_before_using_lb_threshold_evidence
```

Block:

```text
block_goal5269_due_to_figure6_or_exact_input_overclaim
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
