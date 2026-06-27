# External Critical Review - Phoenix V3 Hausdorff Threshold-Summary P0 Repair Packet

Reviewer: External AI (Claude), acting independently

Date: 2026-06-21

Scope: Row-scoped M7 gate for the 1,048,576-points-per-side large row only.

## 1. Verdict

APPROVE WITH AMENDMENTS.

Both previous P0 blockers are closed. The large-row stability evidence is
internally consistent and the numbers in the candidate wording are
arithmetically correct against the stability JSON. One wording amendment is
required before M7 promotion; two P1 notes should be recorded but do not block.

## 2. P0 Closure Status

| P0 | Prior Status | Repair Provided | Verdict |
| --- | --- | --- | --- |
| Missing variance/stability data | Open | 5 independent paired process samples; phase-total mean 1.240x, stddev 0.012, relative CV about 0.95%; all 5 above 1x | CLOSED |
| Missing oracle definition | Open | `expected_tiled_hausdorff(copies=N)` defined with brute-force derivation, scaling logic, and threshold comparison formula | CLOSED |

The stability signal is clean. Five samples on the same pod show phase-total
ratios of 1.224-1.254x with very low dispersion. The oracle is deterministic
and correctly scoped to `oracle_within_threshold =
oracle["hausdorff_distance"] <= threshold`.

## 3. Arithmetic Cross-Check

| Wording claim | JSON field | JSON value | Check |
| --- | --- | --- | --- |
| query speedup mean 1.639x | `query_ratio_mean` | 1.6386841... | rounds to 1.639 |
| phase-total speedup mean 1.240x | `phase_total_ratio_mean` | 1.240042... | rounds to 1.240 |
| weakest phase-total speedup 1.224x | `weakest_phase_total_optix_speedup_vs_embree` | 1.2243669... | rounds to 1.224 |

Numbers are conservatively drawn from the stability rerun, not from the single
one-shot three-row rerun estimate.

## 4. Required Amendment

The candidate wording omits that phase-total includes scene preparation.

Scene preparation times in the stability data are materially asymmetric: OptiX
scene-prepare averages about 5.93s versus Embree about 5.86s, so OptiX is
slightly slower to prepare. The phase-total win emerges from query phase
savings partially absorbing the preparation overhead. A reader who interprets
"phase-total" as a hot-query metric will overread the claim.

Required amendment: add a parenthetical after "phase-total speedup" disclosing
the inclusion of scene preparation.

## 5. P1 Notes

P1-A: Oracle covers only the positive threshold case.

All pairs produce `oracle_within_threshold = true` because the fixture
Hausdorff distance is 0.300 against threshold 0.400. The reject path is
untested at this input size and threshold. This does not invalidate the
speedup numbers, but it should be recorded.

P1-B: Temporal independence of the 5 stability samples is not verified.

The JSON records no timestamps or inter-run gaps. If the samples were run in
rapid succession within a single script invocation, shared warm GPU/kernel
state could compress run-to-run variance artificially. The claim of
"independent paired process samples" is asserted via separate process samples
and files, but cannot be independently verified from timestamps alone.

## 6. Safety Of Candidate Wording

The candidate wording is safe after the required amendment:

- one input size: 1,048,576 per side;
- one threshold: 0.4;
- one GPU class and pod: RTX 4000 Ada;
- same-contract `directed_threshold_prepared`;
- smaller rows disclosed as not phase-total wins;
- no full Hausdorff distance, witness materialization, X-HD reproduction,
  V3-over-V2, all-scale, or all-threshold generality.

## 7. Exact Final Allowed Wording

```text
RTDL V3 includes a generic Hausdorff threshold-summary route where, at
1,048,576 points per side and threshold 0.4 on a single RTX 4000 Ada pod,
prepared OptiX fixed-radius threshold decisions beat the same-contract Embree
route across five independent paired process samples: query speedup mean
1.639x, phase-total speedup mean 1.240x (phase-total includes scene
preparation), weakest phase-total speedup 1.224x, with repeat=5/warmup=1
inside each sample. Smaller rows in the same rerun are query wins but not
phase-total wins.
```

## 8. Exact Forbidden Wording

```text
RTDL computes full Hausdorff faster.
Hausdorff V3 is faster end to end.
X-HD is reproduced.
V3 is faster than V2.
OptiX is faster for all Hausdorff scales.
OptiX is faster for all threshold values.
OptiX is faster for all RTX GPUs.
OptiX beats Embree at the 65,536-point or 262,144-point scale end to end.
The threshold-summary route is faster for all input sizes.
Phase-total speedup is X without counting scene preparation.
```

## 9. Outstanding Gate Condition

The JSON records `current_packet_2ai_consensus_status: pending`. M7 promotion
must not proceed until 2-AI consensus is confirmed. No flag in the packet
should be flipped until consensus is satisfied.

## Summary

Both P0s are closed. Approve with one required amendment: scene preparation
disclosure in the phase-total claim. The large row's stability evidence is
sound; the smaller rows remain correctly blocked. M7 row-scoped promotion is
permitted after the amendment is applied and 2-AI consensus is satisfied.
