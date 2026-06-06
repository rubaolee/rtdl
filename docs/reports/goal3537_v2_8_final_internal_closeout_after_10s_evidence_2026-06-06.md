# Goal3537: v2.8 Final Internal Closeout After 10s Evidence

Date: 2026-06-06

Status: final internal closeout supplement; not public release authorization.

## Purpose

Goal3522 already closed v2.8 internally with 3-AI consensus. Goal3536 then
added stricter A5000 10-second steady-state evidence for the v2.8-vs-v2.3
comparison. This supplement records the final v2.8 position after that newer
measurement:

- v2.8 is internally closed as an architecture, prepared-execution,
  measurement, documentation, and claim-discipline foundation.
- v2.8 is not positioned as a broad performance leap over v2.3.
- v2.9 starts from the Goal3536 performance diagnosis.

## Evidence Chain

| Goal | Role | Final reading |
| --- | --- | --- |
| Goal3522 | Internal v2.8 closeout consensus | v2.8 accepted with boundary as an internal prepared-execution version. |
| Goal3527 | Performance recovery plan consensus | Same-runner diagnostics are not enough; performance work must use promoted paths, repeat guards, and weak-row repair. |
| Goal3533 | Promoted-path recovery table | Useful targeted repairs, but still not a broad all-app performance conclusion. |
| Goal3536 | 10s steady-state A5000 packet | Measurement quality improved; performance result is modest and exposes remaining weak rows. |

## Goal3536 Performance Reading

Goal3536 is the final v2.8 measurement caveat.

Target-compliant 10-second rows:

| App row | v2.8/v2.3 |
| --- | ---: |
| contact manifold | 1.187x |
| RayDB grouped count | 0.973x |
| RayDB grouped sum | 0.998x |
| RT-DBSCAN grouped stream | 1.013x |
| RTNN prepared ranked summary | 1.055x |
| triangle counting | 1.019x |

Target-compliant subset: median `1.016x`, geomean `1.039x`.

All-row diagnostic summary: median `1.006x`, geomean `0.946x`. This all-row
number is not the final performance headline because five rows are partial, but
it must be carried forward so readers do not cherry-pick only the
target-compliant subset.

Partial diagnostic rows:

| App row | v2.8/v2.3 | Why partial |
| --- | ---: | --- |
| Hausdorff X-HD threshold | 0.988x | no app repeat hook; wrapper only reached about 0.5s |
| spatial RayJoin prepared full route | 1.046x | no app repeat hook; wrapper only reached milliseconds |
| robot collision prepared buffers | 1.006x | repeat hook exists, but wall guard prevents long stretch |
| Barnes-Hut node coverage | 0.464x | no repeat hook; real weak row |
| LibRTS AABB index | 0.894x | no repeat hook; wrapper reached about 6s, not 10s |

## Final v2.8 Position

Codex closes v2.8 as:

1. an internal prepared-execution foundation;
2. a cleaner benchmark and learner-docs foundation;
3. a stronger claim-boundary and evidence-bookkeeping foundation;
4. a better primitive/front-door organization foundation;
5. not a public release;
6. not a public speedup release;
7. not a broad RT-core speedup release;
8. not a true-zero-copy or arbitrary partner-composition release.

The important shift is this: Goal3536 makes the performance story more honest.
It prevents the project from turning short-run noise into a headline. The next
version must therefore be performance-first.

## RayDB Correction

Earlier short-run evidence made RayDB grouped sum look like a large v2.8 win.
Goal3536 corrected that under long-run measurement:

- grouped count: `0.973x`;
- grouped sum: `0.998x`.

RayDB remains a valid primitive-first grouped-reduction capability. It is not a
current positive speedup headline.

## Carry-Forward Weak Rows

v2.9 must start from these concrete performance debts:

1. Add real repeat hooks or resident benchmark loops for Hausdorff, spatial
   RayJoin, robot collision, Barnes-Hut, and LibRTS.
2. Repair or classify Barnes-Hut node coverage, currently `0.464x`.
3. Repair or classify LibRTS AABB index, currently `0.894x`.
4. Stop treating RayJoin as one noisy sub-millisecond route; measure its
   promoted contracts with large-scale resident loops.
5. Keep RayDB count and sum separate.
6. Keep all partner use explicit and avoid hidden PyTorch, CuPy, Numba, or
   Triton dispatch.

## Public Boundary

This supplement does not authorize:

- public v2.8 release wording;
- public speedup wording;
- broad RT-core speedup wording;
- package-install or PyPI wording;
- true zero-copy wording;
- whole-app acceleration wording;
- paper-reproduction wording;
- app-specific native-engine shortcuts;
- hidden partner selection.

Any public release or public performance claim still requires a separate
user-requested release packet and fresh review.

## Final Statement

v2.8 is closed internally. The next active lane is v2.9 performance-first work.
