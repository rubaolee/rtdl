# RTDL v2.14 Publication Note

Status: published source-tree release note for tag `v2.14`.

Version marker target: `v2.14`

## Publication Status

v2.14 is released as a source-tree benchmark-app cleanup and row-scoped
comparison packet. The benchmark-app boost gates passed, current-head pod
evidence is indexed, external review accepts the public wording boundary, and
maintainer authorization was given before tagging.

## Publication Shape

The v2.14 statement is row-scoped:

```text
RTDL v2.14 refreshes the benchmark-app comparison packet with current best-known
RTDL OptiX/RT-core and Embree CPU routes. Public performance wording is
row-scoped: each sentence names the benchmark app, contract, backend pair,
partner policy, hardware, timing protocol, speedup direction, and caveat.
```

## Required Before Publication

- [x] v2.14 app inventory is frozen.
- [x] v2.14 same-contract comparison matrix is finalized with Goal4381/Goal4383 supersession rows.
- [x] Every included row has a phase explanation.
- [x] RayJoin author-code caveat is included.
- [x] Embree CPU fairness settings are current for included rows.
- [x] OptiX/RT-core pod evidence is current for 11/11 non-overlay rows and the 2/8 available exact-ready RayJoin overlay rows.
- [x] Public wording packet has zero unexplained rows in the final closeout packet.
- [x] App-author implementation strategy documents primitive-first, explicit-partner, same-contract backend comparison, and no-arbitrary-OptiX-callback boundaries.
- [x] Claude/Gemini accept the V3.0 preflight boundary.
- [x] Claude accepts the Goal4390 app-author strategy with boundary fixes applied.
- [x] Maintainer explicitly authorizes publication.

## Current Fresh Evidence

- Non-overlay same-contract matrix: `validation: accept`, 11/11 rows correct.
- RayJoin Section 5.7 overlay: the 2/8 available exact-ready rows are complete
  and public-review-ready as that exact subset; 6/8 remain unavailable in the
  current public/pod artifact set, so full 8/8 reproduction wording stays
  blocked.
- Block x Water is no longer Embree-faster under the current RTDL route:
  RTDL OptiX 28.650s vs RTDL Embree 53.793s.
- RTDBSCAN uses the Goal4383 compact Embree threshold evidence: at 524,288 points, total is 1.05x faster on OptiX and the threshold stage is 1.37x faster.
- Contact uses the Goal4383 jittered-grid evidence: 4,294,967,296 possible AABB pairs, 65,536 witness rows, and 1.23x OptiX AABB-query speedup.
- Goal4390 documents how app authors should choose primitives, partners, and
  backend comparisons in v2.14; Claude returned `accept-with-boundary`, and the
  required fixes are applied.

## Public Wording That Must Stay Blocked

- RT cores make every benchmark app faster.
- These rows are whole-application speedups unless separately proven.
- RTDL beats RayJoin as a whole system.
- RTDL reproduces the RayJoin paper.
- RTDL reproduces the full 8/8 RayJoin Section 5.7 overlay matrix.
- RTDL hot compute matches the RayJoin authors' specialized C++/CUDA/OptiX hot
  path.
- Partner selection is automatic.
- Numba/CuPy/Triton is universally best.
- Intel GPU or AMD GPU performance is covered.
- true zero-copy or complete device residency is delivered.
- V3.0 planner/device-resident execution graph is delivered.
- Do not say arbitrary raw OptiX callbacks are exposed as the v2.14 user API.
