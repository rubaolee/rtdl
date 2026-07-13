# Goal5268 - X-HD Figure 6 Pruning Phase/Counter Mapping

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Goal

Start the next substantive full-paper target after the entrypoint gates:

```text
Figure 6 - pruning effectiveness on Dragon -> AsianDragon
```

The objective was not to claim Figure 6 reproduction. The objective was to
identify the author flags/scripts/JSON fields and determine whether a valid
same-source scaled candidate can produce Figure 6-style phase/counter evidence.

## Primary Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_figure6_pruning_phase_counter_mapping_2026-07-09.json
```

## Author Source Mapping

Relevant author source locations on the current POD:

```text
/tmp/xhd-goal5112/author/src/flags.cc
  --eb
  --prune
  --lb
  --profiling

/tmp/xhd-goal5112/author/src/main.cpp
  copies FLAGS_eb / FLAGS_prune / FLAGS_lb / FLAGS_profiling into RunConfig

/tmp/xhd-goal5112/author/src/hd_impl/hausdorff_distance_rt.h
  writes per-iteration NumInputPoints, NumOutputPoints, RTTime,
  OffloadingSize, CUDATime, Radius, CMax2, and, under profiling,
  Hits and ComparedPoints

/tmp/xhd-goal5112/author/expr/run_rt_comparison.sh
  runs rt_hdist external baseline plus:
    rt gpu eb=false prune=false lb=0
    rt gpu eb=true  prune=false lb=0
    rt gpu eb=true  prune=true  lb=0
    rt gpu eb=true  prune=true  lb=256
```

## POD Runs

Input:

```text
Dragon -> AsianDragon scaled 1e-3
```

The first three profiling variants are correctness-clean against the author
reference HD:

```text
noopt:
  eb=false prune=false lb=0
  HDResult = 0.06536787003278732
  Running.AvgTime = 6976.301 ms
  Hits = 128,532,825
  ComparedPoints = 176,279,179,922

eb:
  eb=true prune=false lb=0
  HDResult = 0.06536787003278732
  Running.AvgTime = 1841.428 ms
  Hits = 15,269,735
  ComparedPoints = 21,009,262,745

eb_prune:
  eb=true prune=true lb=0
  HDResult = 0.06536787003278732
  Running.AvgTime = 146.486 ms
  Hits = 15,163,664
  ComparedPoints = 586,805,995
```

The full X-HD / load-balanced profiling variant is not correctness-clean on
this Level-B scaled candidate:

```text
xhd_lb256:
  eb=true prune=true lb=256
  check=false HDResult = 0.06545527279376984
  author reference HDResult = 0.06536787003278732
  check=true aborts:
    Wrong HausdorffDistance. Result: 0.06545527 Answer: 0.06536787 Diff: -0.00008740
  Running.AvgTime = 19.64 ms
  RTTime = 8.405 ms
  CUDATime = 4.243 ms
  OffloadingSize = 2,241,985
  Hits = 23,980,889
  ComparedPoints = 56,056,564
```

## Interpretation

This is useful progress but not Figure 6 reproduction.

What is now proven:

```text
1. The author flags and script structure for Figure 6-style pruning variants
   are identified.
2. Profiling JSON exposes the counters previously missing from ordinary
   run_all logs: Hits and ComparedPoints.
3. NoOpt, EB, and EB+Prune variants can be run on the Level-B scaled candidate
   and remain correctness-clean against the author reference HD.
```

What blocks Figure 6:

```text
1. The external RT-HDIST baseline referenced by run_rt_comparison.sh is not in
   the current RTDL/POD evidence chain.
2. The LB=256/full-XHD profiling variant is not correctness-clean on the
   current scaled public candidate; check=true aborts.
3. Exact author paper input bytes/hashes are still absent.
4. Therefore a Figure 6 plot/table would be an overclaim until the LB=256
   correctness issue is explained under the author's exact script/input
   conditions or an accepted instrumentation route is built.
```

## Claim Boundary

Authorized:

```text
Goal5268 provides a Figure 6 phase/counter mapping and shows which fields are
available from author profiling JSON.
```

Not authorized:

```text
Figure 6 reproduced
full X-HD paper reproduction
exact paper byte-input identity
author RT-core equivalence
author performance parity or speedup
```

## Next Recommended Work

```text
Goal5269 - resolve the LB=256/full-XHD Figure 6 correctness issue
```

Candidate actions:

```text
1. Try the author's exact paper path/environment if exact inputs become
   available.
2. Run the same profiling sequence on the raw author-log public candidate and
   compare with the scaled candidate.
3. Inspect loadBalanceProcessing / profiling interaction to determine whether
   profiling or the Level-B scaled candidate changes correctness.
4. Do not publish Figure 6 until the full-XHD profiling variant is
   correctness-clean or explicitly excluded with a paper-faithful substitute.
```
