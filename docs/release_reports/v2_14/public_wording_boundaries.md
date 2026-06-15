# RTDL v2.14 Public Wording Boundaries

Status: locked for v2.14 closeout.

Date: 2026-06-15

## Allowed Thesis

RTDL v2.14 refreshes the benchmark-app comparison packet with current best-known RTDL OptiX/RT-core and Embree CPU routes. The allowed performance wording is row-scoped, contract-scoped, backend-scoped, partner-scoped, hardware-scoped, and phase-scoped.

For RTDBSCAN, v2.14 may additionally cite the Goal4389 prepared-grid partner
supplement: under that current contract, Numba is the measured large-scale
winner over the same-contract CuPy opponent. This does not broaden the backend
comparison or authorize a large full-app RTDBSCAN speedup claim.

## Required Sentence Shape

Every public performance sentence must name:

- app and row;
- exact contract;
- backend pair;
- partner policy;
- hardware;
- timing protocol;
- speedup direction;
- caveat.

## Blocked Wording

Do not say:

- RT cores accelerate every benchmark app.
- v2.14 proves whole-application speedups for every row.
- RTDL reproduces the full RayJoin paper.
- RTDL hot compute matches the RayJoin authors' C++/CUDA/OptiX implementation.
- RTDL beats RayJoin as a whole system.
- RTDBSCAN has a large full-app RT-core speedup.
- Barnes-Hut is accelerated as a full force solver.
- Contact manifold is accelerated as a full physics solver.
- Hausdorff exact witness-distance is accelerated.
- Triangle counting reproduces RT-Graph paper speedups.
- LibRTS paper artifacts are reproduced.
- Partner choice is automatic.
- A partner-dependent benchmark claim is complete without both the current best partner and a same-contract Numba reference.
- true zero-copy or complete device residency is delivered.
- AMD or Intel GPU results are covered.
- V3.0 planner/device-resident execution graph is delivered.

## RayJoin Overlay Boundary

RayJoin overlay is public-review-ready for the available 2/8 exact-ready
Section 5.7 CDB subset. The remaining 6/8 exact inputs are unavailable in the
current public/pod artifact set, so v2.14 may report the measured 2/8 subset but
must not claim full 8/8 Section 5.7 reproduction.

## Transition To V3.0

v2.14 may say that V3.0 is the next architecture phase after closeout. It must also say that V3.0 implementation is not authorized until the V3.0 M1 IR design document is frozen.
