# Goal5217 Level-B Same-POD Performance Matrix Result

Date: 2026-07-09

## Verdict

```text
completed_level_b_same_pod_phase_matrix__no_ratio_authorized
```

## Purpose

After Goal5216, the project had a strong Level-B representative X-HD packet but
still lacked a same-POD author/RTDL timing matrix for the current route.

Goal5217 runs the same public Stanford Dragon -> HappyBuddha representative
workload on the same POD and records:

```text
author internal Running.AvgTime
author process wall
RTDL fresh route wall
RTDL full gate including input load
RTDL explicit-warm measured route wall
RTDL explicit warmup cost
```

This is a phase-boundary matrix, not a performance-ratio claim.

## Machine-Readable Matrix

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5217_level_b_same_pod_performance_matrix_2026-07-09.json
```

## POD

```text
host = 213.173.108.24
port = 13502
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

POD access used the wrapper:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 ...
```

## Workload

```text
target = graphics_dragon_happy_buddha
source = public Stanford Dragon / dragon_vrip.ply
target = public Stanford HappyBuddha / happy_vrip.ply
point_counts = [437645, 543652]
level = Level B same-source representative
```

Exact paper dataset identity remains unproved.

## Runs

The matrix uses 5 repeats per regime:

```text
author hd_exec repeats = 5
RTDL fresh repeats = 5
RTDL explicit-warm repeats = 5
```

All author repeats produced the same public-data author re-run HDResult and are
within `1e-6` of the paper-branch author-log HDResult. All RTDL fresh and warm
measured repeats matched the author re-run HDResult. The paper-log value remains
distinct from the public-data author re-run value.

## Median Results

```text
author internal Running.AvgTime median = 7.722 ms
author process wall median           = 1.9058002084493637 s

RTDL fresh route wall median         = 0.8396428748965263 s
RTDL fresh full total incl load      = 1.5200408399105072 s

RTDL explicit-warm measured route    = 0.2896384373307228 s
RTDL explicit-warm full total
  incl load + warmup + measured      = 1.812147118151188 s
```

The current fresh route median is slightly lower than the single-run Goal5212
fresh route (`~0.852s`) and should be treated as same-POD repeat evidence for
the same route, not a new algorithmic change.

## Denominator Boundary

The following denominators are not the same:

```text
author internal Running.AvgTime:
  author internal kernel/algorithm timing reported by hd_exec JSON

author process wall:
  wall time around one author hd_exec process invocation

RTDL fresh route wall:
  RTDL route time excluding public input load

RTDL fresh full total:
  RTDL runner total including public input load

RTDL explicit-warm measured route:
  RTDL measured route after a separate warmup case

RTDL explicit-warm full total:
  input load + warmup case + measured case
```

Because these are different denominators, and because exact paper dataset
identity is still unproved, this goal does **not** authorize an author-vs-RTDL
performance ratio.

## Interpretation

This matrix is useful because it removes one source of ambiguity:

```text
author process wall and RTDL wall numbers are now recorded on the same POD for
the same Level-B representative public workload.
```

But the matrix does not remove the larger claim-boundary blockers:

```text
exact paper inputs are still unavailable;
author internal time and RTDL route wall are different phase boundaries;
warm route time excludes warmup;
full paper figures are not reproduced.
```

## What This Proves

```text
The author binary re-run on the public Dragon/HappyBuddha representative pair
is close to the paper-branch author-log HDResult, but not identical to it.

The current RTDL route still matches the author re-run HDResult across fresh
and explicit-warm repeats.

Same-POD timing evidence is now available for author internal time, author
process wall, RTDL fresh route, RTDL full gate, and RTDL explicit-warm route.
```

## What This Does Not Prove

```text
full X-HD paper reproduction;
exact paper dataset reproduction;
author-vs-RTDL speedup or slowdown ratio;
author parity;
warm-only performance;
exact paper figure reproduction;
X-HD-specific RTDL primitive.
```

## Claim Boundary

Allowed:

```text
On the same POD and same public Dragon -> HappyBuddha Level-B representative
workload, the current RTDL route matches the author hd_exec re-run on public
data. The author re-run remains distinct from the paper-branch log value.
Median author process wall is about 1.906s; median RTDL fresh full gate
including input load is about 1.520s; median RTDL fresh route wall is about
0.840s; median explicit-warm measured route is about 0.290s with warmup
reported separately.
```

Required caveat:

```text
These are phase-separated numbers, not an authorized author-vs-RTDL performance
ratio, and this remains Level-B representative evidence rather than exact paper
dataset reproduction.
```

Forbidden:

```text
RTDL is faster/slower than author by Xx;
author parity achieved;
full X-HD paper reproduction complete;
exact paper dataset reproduction complete;
warm route is the default headline;
exact paper figures reproduced.
```

## Files

Remote POD artifacts were downloaded into:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5217_author_repeat*_summary_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5217_author_repeat*_raw_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5217_rtdl_fresh_repeat*_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5217_rtdl_warm_repeat*_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5217_level_b_same_pod_performance_matrix_2026-07-09.json
```

## Next Recommendation

Send Goal5217 together with the Goal5216 midterm packet for strict review.

If approved:

```text
Use the Goal5217 matrix as the stable Level-B phase-boundary performance
evidence.
Keep all ratios unauthorized unless a future review aligns dataset, hardware,
phase boundary, and runtime regime.
```
