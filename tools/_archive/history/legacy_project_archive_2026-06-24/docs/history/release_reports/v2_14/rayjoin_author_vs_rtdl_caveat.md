# RTDL v2.14 RayJoin Author-vs-RTDL Caveat

Status: published caveat in source-tree tag `v2.14`.

## Required Separation

RayJoin comparisons must separate three different questions:

| Question | Valid comparison |
| --- | --- |
| Does RTDL reproduce the RayJoin program surface? | LSI, PIP, and overlay contracts compared against author-code behavior and counts where available. |
| Does RTDL OptiX beat RTDL Embree? | Same RTDL app, same contract, fixed partner policy, OptiX/RT-core route versus Embree CPU route. |
| Does RTDL hot compute match author C++/CUDA/OptiX? | Hot-processing phases only, with read/deserialization excluded or separately reported. |

## Current RayJoin Overlay Interpretation

Goal4380 reran the exact-ready Section 5.7 overlay pairs on the pod:

| Row | Local Author RT process wall | RTDL OptiX | RTDL Embree CPU | OptiX-vs-Embree |
| --- | ---: | ---: | ---: | ---: |
| County x Zipcode | 5.521s | 5.782s | 15.121s | 2.61x |
| Block x Water | 27.944s | 28.650s | 53.793s | 1.88x |

Allowed interpretation:

> RTDL OptiX is near local author process wall and faster than RTDL Embree CPU
> on the 2 exact-ready Section 5.7 overlay rows under the selected
> cached/preprocessed application-wall protocol.

Also allowed:

> The measured 2/8 exact-ready Section 5.7 overlay rows are public-review-ready
> as the currently available exact CDB subset.

Blocked interpretation:

> RTDL hot compute matches the RayJoin authors' specialized C++/CUDA/OptiX hot
> path.

Also blocked:

> RTDL fully reproduces the 8/8 RayJoin Section 5.7 overlay matrix.

The current public/pod artifact set has only 2/8 exact preprocessed CDB overlay
input pairs. The remaining six lakes/parks continent pairs are unavailable for
same-contract exact comparison, so they do not block publishing the measured
2/8 subset, but they do block full 8/8 matrix wording.

## Why The Stronger Claim Is Blocked

The Block x Water author process wall includes large map read/deserialization
time. The author printed hot-processing phases are much smaller than the process
wall. RTDL's wall time instead reflects runtime compute, preparation,
materialization, and generic primitive orchestration.

Therefore, v2.14 must not use near process-wall parity as evidence of hot-path
parity. The stronger author-hot-compute claim belongs to V3.0-class work with
device-resident/fused execution and profiler-grade phase accounting.

## V3.0 Carry-Forward

RayJoin remains a strong V3.0 diagnostic workload. The V3.0 target should be a
generic planner/device-resident/fused primitive graph that makes RTDL ray
workload lowering closer to expert C++/CUDA/OptiX implementations without
adding RayJoin-specific native engine semantics.
