# Goal5271 - X-HD Level-B Pruning Diagnostic

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Goal

After Goal5270, Figure 6 remains blocked on exact paper input availability.
This goal therefore creates a separately named Level-B pruning diagnostic from
the current public/same-source Dragon -> AsianDragon scaled candidate.

This is **not** Figure 6 reproduction.

## Primary Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5271_level_b_pruning_diagnostic_2026-07-09.json
```

## Diagnostic Scope

Input regime:

```text
Level-B public/same-source scaled candidate
Stanford Dragon -> AsianDragon scaled 1e-3
```

Not claimed:

```text
exact paper byte-input identity
Figure 6 reproduction
full paper reproduction
author RT-core equivalence
author/RTDL performance ratio
```

## Correctness-Clean Profile Rows

Only variants that match the candidate reference HD are included in the primary
diagnostic:

| Label | EB | Prune | LB | HD matches | AvgTime ms | Hits | ComparedPoints |
|---|---:|---:|---:|---:|---:|---:|---:|
| noopt | false | false | 0 | true | 6976.301 | 128532825 | 176279179922 |
| eb | true | false | 0 | true | 1841.428 | 15269735 | 21009262745 |
| eb_prune | true | true | 0 | true | 146.486 | 15163664 | 586805995 |

Derived effects on this candidate:

```text
EB time speedup vs NoOpt:             3.7885x
EB+Prune time speedup vs EB:         12.5707x
EB+Prune time speedup vs NoOpt:      47.6244x

EB ComparedPoints reduction vs NoOpt:        8.3905x
EB+Prune ComparedPoints reduction vs EB:    35.8027x
EB+Prune ComparedPoints reduction vs NoOpt: 300.4045x
```

These are candidate-level author profiling effects. They are not RTDL speedups
and not paper Figure 6 values.

## Invalid / Diagnostic Controls

The author Figure 6 XHD setting on the candidate is invalid:

```text
eb=true prune=true lb=256
HDResult = 0.06545527279376984
matches reference = false
check=true aborts
```

The candidate becomes correctness-clean at higher LB thresholds; `lb=2048`
passes `check=true` in Goal5269. But:

```text
lb=2048 is a candidate-only control.
lb=2048 is not the author Figure 6 setting.
lb=2048 is not authorized as a Figure 6 substitute.
```

## Claim Boundary

Authorized:

```text
This packet reports a Level-B pruning diagnostic on the current public/scaled
candidate and shows how EB and Prune reduce author profiling work counters for
the correctness-clean lb=0 variants.
```

Not authorized:

```text
Figure 6 reproduced
full X-HD paper reproduction
exact paper dataset identity
author RT-core equivalence
author/RTDL performance ratio
lb=2048 as Figure 6 substitute
```

## Next Recommended Work

This diagnostic is a useful fallback while exact Figure 6 inputs remain
unavailable. The next full-paper move should not deepen this diagnostic unless
there is a specific review request; instead:

```text
1. keep trying to acquire exact paper graphics inputs, or
2. move to another paper figure/dataset with a weaker exact-input blocker.
```
