# X-HD Current Status After Goal5266

Date: 2026-07-09

## One-Line Status

```text
xhd_public_modelnet40_all400_and_graphics_representatives_hd_exec_entrypoint_complete__full_paper_incomplete
```

## User-Facing RTDL Entrypoint

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

Covered evidence:

```text
1. bounded WKT same-input gates
2. public ModelNet40 all-400 pair identities represented in the paper-branch log index
3. Stanford Graphics Dragon -> HappyBuddha
4. Stanford Graphics Dragon -> AsianDragon scaled 1e-3
5. Stanford Graphics ThaiStatuette scaled 1e-3 -> HappyBuddha
6. Stanford Graphics ThaiStatuette scaled 1e-3 -> AsianDragon scaled 1e-3
```

## Latest Addition

Goal5266:

```text
source = public Stanford XYZRGB ThaiStatuette scaled 1e-3
source vertex_count = 4999996
target = public Stanford AsianDragon scaled 1e-3
target vertex_count = 3609600
paper log HDResult = 0.28763845562934875
author rerun HDResult = 0.28763842582702637
RTDL HDResult = 0.2876384148709406
abs(RTDL - author rerun) ~= 1.10e-8
abs(RTDL - paper log) ~= 4.08e-8
per_source_witness_exact = true
RTDL route wall ~= 10.770s
author internal AvgTime = 18.864ms
```

## Performance Status

Performance evidence remains denominator-labeled and non-parity:

```text
ModelNet40 all-400 RTDL route / author process-wall = 1.648x slower
ModelNet40 all-400 RTDL route / author internal AvgTime = 150.39x slower
Dragon -> HappyBuddha exact-witness route wall ~= 0.621s
Dragon -> AsianDragon exact-witness route wall ~= 2.651s
ThaiStatuette -> HappyBuddha exact-witness route wall ~= 5.013s
ThaiStatuette -> AsianDragon exact-witness route wall ~= 10.770s
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
history/internal_docs/call_for_review_goals5255_5266_xhd_hd_exec_entrypoint_modelnet40_graphics_performance_docs_2026-07-09.md
```

Goals5255-5266 remain `implemented_review_pending` until external review is
present.
