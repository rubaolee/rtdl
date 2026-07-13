# Goal5270 - X-HD Figure 6 Exact-Input Availability / Diagnostic Decision

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Goal

Resolve the decision left open by Goal5269:

```text
Can we honestly continue toward Figure 6 reproduction on the current POD/input
state, or must the current work be downgraded to a separately named Level-B
pruning diagnostic?
```

This goal does not implement a new route and does not add a new performance
claim. It is a claim-boundary and input-provenance gate.

## Primary Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5270_figure6_exact_input_availability_decision_2026-07-09.json
```

## POD Availability Probe

The current POD is reachable:

```text
POD_OK
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

But the author exact dataset root required by the Figure 6 script is absent:

```text
/local/storage/shared/HDDatasets                  missing
/local/storage/shared/HDDatasets/graphics         missing
/local/storage/shared/HDDatasets/graphics/dragon.ply        missing
/local/storage/shared/HDDatasets/graphics/asian_dragon.ply  missing
```

The current POD does contain candidate files under:

```text
/tmp/xhd_goal5234/data/dragon.ply
/tmp/xhd_goal5234/data/asian_dragon.ply
/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply
```

These are useful Level-B candidate inputs, but they are not proof of exact
paper byte-input identity.

## Author Figure 6 Contract

The author Figure 6-style script uses:

```text
/tmp/xhd-goal5112/author/expr/run_rt_comparison.sh
dataset1=/local/storage/shared/HDDatasets/graphics/dragon.ply
dataset2=/local/storage/shared/HDDatasets/graphics/asian_dragon.ply
normalize=false
variant=rt
execution=gpu
profiling=true
check=true
```

The Figure 6 variant sequence is:

```text
NoOpt:    eb=false prune=false lb=0
EB:       eb=true  prune=false lb=0
EB+Prune: eb=true  prune=true  lb=0
XHD:      eb=true  prune=true  lb=256
```

The paper-branch log records an LB=256 exact-path run:

```text
HDResult = 0.06536811590194702
Running.AvgTime = 17.2604 ms
OffloadingSize sum = 2,366,254
point counts = 437,645 / 3,609,600
```

## Carry-Forward From Goal5269

On the current public/same-source Dragon -> AsianDragon scaled candidate:

```text
lb=256 check=true aborts:
  Wrong HausdorffDistance. Result: 0.06545527 Answer: 0.06536787

lb=2048 check=true passes.
```

The higher `lb=2048` threshold is correctness-clean for the candidate, but it
is not the author Figure 6 XHD setting. Using it would create a different
diagnostic experiment, not a reproduction of Figure 6.

## Decision

```text
Figure 6 reproduction status: not_reproduced
Exact input blocker: true
Level-B pruning diagnostic allowed: true
Level-B diagnostic must be named separately: true
lb=2048 substitute authorized as Figure 6: false
```

## Claim Boundary

Authorized:

```text
Current exact Figure 6 inputs are unavailable on the POD.
Current public/scaled candidate blocks Figure 6 reproduction because LB=256 is
not correctness-clean.
A separately named Level-B pruning diagnostic may be produced, provided it does
not claim to be Figure 6.
```

Not authorized:

```text
Figure 6 reproduced
full X-HD paper reproduction
exact paper dataset identity
author RT-core equivalence
performance ratio
lb=2048 as a Figure 6 substitute
```

## Next Recommended Work

The clean next choices are:

```text
1. If exact /local/storage/shared/HDDatasets graphics files become available,
   rerun the author Figure 6 sequence exactly.

2. If exact files remain unavailable, create Goal5271 as a separately named
   Level-B pruning diagnostic, or move to another figure/dataset whose exact
   input blocker is weaker.
```

Recommended next label:

```text
Goal5271 - Level-B pruning diagnostic from current public/scaled candidate
```
