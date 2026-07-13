# Goal5272 - X-HD Figure 11 Author Memory Log Matrix

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Goal

After Goal5271 closed the current Figure 6 path as a Level-B diagnostic only,
pick a next paper target with available evidence. Figure 11 is the best next
target to start because the author repository contains memory logs and a
plotting script:

```text
/tmp/xhd-goal5112/author/expr/draw_mem.py
/tmp/xhd-goal5112/author/expr/logs/mem
```

This goal extracts the author-side Figure 11 memory matrix exactly according to
the `draw_mem.py` data-loading contract. It does **not** claim Figure 11
reproduction because RTDL memory instrumentation has not yet been matched to
the author memory accounting boundary.

## Primary Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5272_figure11_author_memory_log_matrix_2026-07-09.json
```

## Author Memory Contract

`draw_mem.py` uses:

```text
logs/mem/{nn_gpu,clover_gpu,rt_gpu}/{geo,graphics}/*.json
```

and maps methods to:

```text
nn_gpu     -> NN-KD
clover_gpu -> NN-Clover
rt_gpu     -> X-HD
```

For NN-KD / NN-Clover, `Memory` is a scalar byte count. For X-HD, `Memory` is a
component dict and `draw_mem.py` sums the components:

```text
BVH + Grid + MBRs B + WL + WL Heavy Peak
```

## Extracted Matrix

Graphics rows:

```text
Dragon / Asian Dragon
Dragon / Buddha
Thai / Asian Dragon
Thai / Buddha
```

Mean total memory:

```text
NN-KD     23.765 MB
NN-Clover 60.500 MB
X-HD      46.015 MB
```

X-HD mean breakdown:

```text
BVH            0.078 MB
Grid           7.940 MB
MBRs B         0.037 MB
WL            20.743 MB
WL Heavy Peak 17.216 MB
```

Geospatial rows:

```text
USCounty / USZipcode
USWater / USBlock
OSMLakes / OSMParks
```

Mean total memory:

```text
NN-KD      1271.344 MB
NN-Clover  3613.532 MB
X-HD       1548.594 MB
```

X-HD mean breakdown:

```text
BVH             15.886 MB
Grid           639.568 MB
MBRs B           5.194 MB
WL             849.307 MB
WL Heavy Peak   38.640 MB
```

## Claim Boundary

Authorized:

```text
Goal5272 reproduces the author-side memory-log matrix extraction used by
draw_mem.py.
```

Not authorized:

```text
Figure 11 reproduced
full X-HD paper reproduction
exact paper dataset identity
RTDL memory parity
author/RTDL memory ratio
performance parity
```

## Next Required Work

To move from author-side matrix extraction to Figure 11 reproduction, the next
goal must define and implement an RTDL memory accounting boundary that can be
compared to the author fields:

```text
BVH
Grid
MBRs B
WL
WL Heavy Peak
```

Until that boundary exists and is measured on corresponding workloads, Figure
11 remains `not_reproduced`.
