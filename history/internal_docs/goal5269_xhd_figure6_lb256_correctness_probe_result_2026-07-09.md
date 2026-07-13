# Goal5269 - X-HD Figure 6 LB=256 Correctness Probe

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Goal

Resolve the immediate blocker exposed by Goal5268:

```text
Why does the author Figure-6-style LB=256/full-XHD variant fail check=true on
the current Dragon -> AsianDragon Level-B same-source/scaled candidate?
```

This goal does **not** claim Figure 6 reproduction. It classifies the failure so
the project does not accidentally publish a Figure 6 plot/table from a
non-paper-faithful substitute.

## Primary Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5269_figure6_lb256_correctness_probe_2026-07-09.json
```

## What Was Checked

### Author Script And Paper-Branch Log

The author script:

```text
/tmp/xhd-goal5112/author/expr/run_rt_comparison.sh
```

uses the exact-path workload:

```text
/local/storage/shared/HDDatasets/graphics/dragon.ply
/local/storage/shared/HDDatasets/graphics/asian_dragon.ply
```

with:

```text
variant=rt
execution=gpu
normalize=false
eb=true
prune=true
lb=256
profiling=true
check=true
```

The author paper-branch log contains an LB=256 run for that path:

```text
expr/logs/end2end/rt_gpu/graphics/dragon.ply_asian_dragon.ply.json
HDResult = 0.06536811590194702
Running.AvgTime = 17.2604 ms
LB = 256
OffloadingSize sum = 2,366,254
input point counts = 437,645 / 3,609,600
```

But the exact `/local/storage/shared/HDDatasets/graphics` directory is **not
available** on the current POD.

### Current Level-B Candidate

The current candidate uses public/same-source files:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip.ply
Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon_scaled_1e-3.ply
```

The point counts match the author log, but the MBRs differ slightly from the
author log:

```text
dragon upper abs diffs:
  [1.9371509552001953e-07, 1.4901161193847656e-08, 7.450580596923828e-09]

asian upper abs diffs:
  [4.917383193969727e-07, 1.4901161193847656e-08, 1.4901161193847656e-08]
```

This is exactly the kind of fingerprint that prevents an exact paper byte-input
identity claim.

## LB Threshold Scan

On the current Level-B candidate, with `eb=true` and `prune=true`:

```text
lb=0      -> HDResult 0.06536787003278732, correct
lb=32     -> HDResult 0.06545527279376984, wrong
lb=64     -> HDResult 0.06545527279376984, wrong
lb=128    -> HDResult 0.06545527279376984, wrong
lb=192    -> HDResult 0.06545527279376984, wrong
lb=256    -> HDResult 0.06545527279376984, wrong
lb=384    -> HDResult 0.06545527279376984, wrong
lb=512    -> HDResult 0.06545527279376984, wrong
lb=1024   -> HDResult 0.06545527279376984, wrong
lb=1152   -> HDResult 0.06545527279376984, wrong
lb=1280   -> HDResult 0.06536787003278732, correct
lb=2048   -> HDResult 0.06536787003278732, correct
lb=4096   -> HDResult 0.06536787003278732, correct
```

`check=true` confirms the split:

```text
lb=1024 -> aborts:
  Wrong HausdorffDistance. Result: 0.06545527 Answer: 0.06536787

lb=2048 -> Check.Pass = true
```

## Interpretation

The author Figure 6 script records LB=256 on exact author paths, but the current
public/scaled candidate does not have exact byte identity and fails LB=256
correctness.

A higher threshold such as `lb=2048` is correctness-clean on this candidate, but
that is **not** the Figure 6 script setting and must not be promoted as Figure 6
reproduction.

## Claim Boundary

Authorized:

```text
Goal5269 classifies the Figure 6 LB=256 blocker as a Level-B candidate /
provenance gap and records a threshold scan showing where the current
candidate becomes correctness-clean.
```

Not authorized:

```text
Figure 6 reproduced
exact paper byte-input identity
author RT-core equivalence
author/RTDL performance ratio
using lb=2048 as a Figure 6 substitute
```

## Next Recommended Work

The honest next choices are:

```text
1. If exact /local/storage/shared/HDDatasets graphics files become available,
   rerun the author run_rt_comparison.sh sequence directly.

2. If exact files remain unavailable, mark Figure 6 blocked on exact input
   provenance and create only a separately named Level-B pruning diagnostic
   that does not claim Figure 6 reproduction.
```

Recommended next goal:

```text
Goal5270 - Figure 6 exact-input availability / Level-B diagnostic decision
```
