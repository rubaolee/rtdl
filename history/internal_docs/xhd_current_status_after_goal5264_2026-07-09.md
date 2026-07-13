# X-HD Current Status After Goal5264

Date: 2026-07-09

## One-Line Status

```text
xhd_public_modelnet40_all400_and_graphics_representatives_hd_exec_entrypoint_complete__full_paper_incomplete
```

## What Is Now Covered By The User-Facing RTDL Entry

Primary script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

Batch bridge:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
```

Covered evidence:

```text
1. bounded WKT same-input gates
2. public ModelNet40 all-400 pair identities represented in the paper-branch log index
3. Stanford Graphics Dragon -> HappyBuddha full-public representative pair
4. Stanford Graphics Dragon -> AsianDragon scaled 1e-3 same-source candidate
```

## Strongest Correctness Evidence

ModelNet40 all-400:

```text
matched = 400 / 400
max_author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = true for all cases
```

Dragon -> HappyBuddha:

```text
author rerun HDResult = 0.12572988867759705
RTDL HDResult = 0.12572988629271128
author_abs_diff ~= 2.38e-9
per_source_witness_exact = true under exact-witness route
```

Dragon -> AsianDragon scaled 1e-3:

```text
author rerun HDResult = 0.06536787003278732
paper log HDResult = 0.06536811590194702
RTDL HDResult = 0.06536787240753439
author_abs_diff ~= 2.37e-9
rtdl_vs_paper_log_abs_diff ~= 2.43e-7
per_source_witness_exact = true
```

## Performance Status

Performance evidence remains denominator-labeled and non-parity:

```text
ModelNet40 all-400 RTDL route / author process-wall = 1.648x slower
ModelNet40 all-400 RTDL route / author internal AvgTime = 150.39x slower
Dragon -> HappyBuddha exact-witness route wall ~= 620.92 ms
Dragon -> AsianDragon exact-witness route wall ~= 2651.05 ms
```

No author speedup or parity is claimed.

## Remaining Full-Paper Blockers

Still not closed:

```text
exact paper byte-input identity
all paper datasets
paper Figures 5-11
author RT-core algorithm equivalence
author internal AvgTime parity
same-source/scaled candidate = exact paper dataset
```

## Current Review Packet

```text
history/internal_docs/call_for_review_goals5255_5264_xhd_hd_exec_entrypoint_modelnet40_graphics_performance_docs_2026-07-09.md
```

Goals5255-5264 remain `implemented_review_pending` until external review is
present.
