# Consolidated Call For Review - Goals5255-5263 X-HD hd_exec Entrypoint Coverage

Date: 2026-07-09

## Review Scope

Please strictly review Goals5255-5263 as one X-HD `hd_exec`-compatible
user-entrypoint packet.

This packet covers:

```text
bounded WKT smoke,
public ModelNet40 OFF all-400,
Stanford Graphics Dragon -> HappyBuddha PLY,
Running.AvgTime semantics,
performance matrix,
README/manifest status.
```

## Goals Covered

```text
Goal5255: RTDL hd_exec-compatible single-case entrypoint.
Goal5256: bounded 3D GPU route POD smoke.
Goal5257: one public ModelNet40 OFF pair through the entrypoint.
Goal5258: Running.AvgTime semantics hardening.
Goal5259: summary-driven batch bridge.
Goal5260: all-400 public ModelNet40 batch through the entrypoint.
Goal5261: denominator-separated all-400 performance matrix.
Goal5262: README/manifest status update.
Goal5263: full-public Stanford Dragon -> HappyBuddha graphics PLY through the entrypoint.
```

## Primary Evidence

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json
```

Primary app entrypoints:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
```

Docs:

```text
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Central Claims

1. The X-HD RTDL paper app has an app-owned author-style `hd_exec` entrypoint.
2. The entrypoint supports WKT, OFF, and PLY input paths currently used by the
   paper-app evidence.
3. Public ModelNet40 all-400:

```text
400 / 400 matched author rerun HDResult
max_author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = true for all 400 under cell-mbr-exact-witness
```

4. Stanford Graphics Dragon -> HappyBuddha Level-B representative:

```text
author_hd_result = 0.12572988867759705
RTDL HDResult = 0.12572988629271128
abs_diff = 2.3848857610975216e-09
fast-scalar route wall ~= 536.22 ms, per_source_witness_exact=false
exact-witness route wall ~= 620.92 ms, per_source_witness_exact=true
```

5. Performance denominators remain separated:

```text
RTDL ModelNet40 route-wall sum / author process-wall sum = 1.65x slower
RTDL ModelNet40 route-wall sum / author internal Running.AvgTime sum = 150.39x slower
```

6. The packet does not claim:

```text
full X-HD paper reproduction complete
exact paper byte-input identity
all paper datasets/Figures reproduced
author RT-core algorithm equivalence
author performance parity or speedup
```

## Review Questions

1. Does this packet establish the `hd_exec`-compatible runner as the correct
   primary RTDL user entrypoint for the X-HD paper app?
2. Are ModelNet40 and Stanford Graphics evidence correctly labeled as
   public/same-source author-rerun evidence rather than exact paper byte-input
   identity?
3. Are route labels and witness contracts clear enough to distinguish fast
   HDResult routes from exact per-source witness routes?
4. Are performance denominators safe and sufficiently labeled?
5. Does the README/manifest status string remain honest:

```text
xhd_public_modelnet40_all400_hd_exec_entrypoint_complete__full_paper_incomplete
```

6. What should be the next full-paper blocker after this packet: exact dataset
   provenance, remaining paper datasets/Figures, or author RT-core internal
   AvgTime algorithm gap?

## Expected Verdict Labels

Preferred approval:

```text
approve_goals5255_5263_xhd_hd_exec_entrypoint_modelnet40_graphics_performance_docs
```

Possible amendment:

```text
revise_goals5255_5263_due_to_entrypoint_or_claim_boundary
```

Possible block:

```text
block_goals5255_5263_due_to_overclaimed_full_paper_or_invalid_comparison
```

Please provide:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to review questions:
```
