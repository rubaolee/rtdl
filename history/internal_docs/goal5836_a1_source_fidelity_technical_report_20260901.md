# Goal5836 A1 author-source fidelity technical report

Date: 2026-09-01
Stage: `A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION`
Scope: exact-paper and exact-source static semantics only
Author build/execution: 0
RTDL Goal5836 execution: 0
Input freezes/routes: 0
GPU/POD workers: 0
Timings/performance results: 0
Product/case-study source mutations: 0
External review: not requested or authorized

## 1. Authorization and terminal result

The owner instruction received after A0 is preserved in
`goal5836_a1_owner_authorization_20260901.md` and is interpreted fail-closed as:

```text
AUTHORIZE_STAGE_A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION_ONLY
```

That file is 1,189 bytes and has SHA-256
`066dbd5ea12182f6eda1936ade2ba3b1dc0be2a019b7e1d9989f524d1a9efa47`.
The authorization is consumed.

The preregistered A1 classification is:

```text
MATERIAL_PREDICATE_DIFFERENCE
```

The resulting machine status is:

```text
TERMINAL_MAPPING_REFUSAL__KEEP_GOAL5835_SCOPE__A2_NOT_REACHABLE
```

The controlling authority is
`goal5836_a1_source_fidelity_20260901/SOURCE_FIDELITY_AUTHORITY.json`:

```text
whole-file SHA-256:
f05b026c2e96506466a400de71ee8ab6893f8deecb547447f29b8af567842c5f

internal authority seal:
5d52efd485eb9433a442c3a9a81d880e91e80bb38de33d6b4499a2329c3034d6
```

This is a completed negative scientific outcome, not an unfinished stage.
The successful Paper-App promotion path did not complete. Under the frozen
preaction, a material predicate difference terminates the Goal5836 transaction
at A1. A2--A5 are unreachable and there is no next owner gate inside this
transaction.

## 2. Evidence custody

A1 reverified A0 authority SHA-256
`5d18d5736be47288e6867d29df93a05bc2f7a81462101e563d65f88c5d236bef`
before inspecting semantics. The evidence remains:

```text
paper: official arXiv:2409.09918v2 author-submitted revision
paper bytes: 34,726,851
paper SHA-256: 9a0003bda2ce176415389c99af0e91aea0fc1564a3bfb7388b8054760993c9c0
author repository: https://github.com/Ssz990220/RTCollisionDetection.git
author commit: bacbf77a612bba3e6e8f7a464fa0fa2c67298ac7
author root tree: 3e5e1c3a2a128148eae61bc94a22eaae491e496f
```

The A1 builder verifies all 203 files in the deterministic A0 source capsule
against the complete A0 inventory, including archive path set/order, byte
length, SHA-256, Git blob OID and selection-rule equality. It then binds the
seven files needed for the semantic call chain by path, bytes, SHA-256 and Git
OID. No source file was taken from a mutable checkout or an unpinned branch.

## 3. Paper and source findings

The exact paper supports the following method facts:

| Paper locator | Method fact used by A1 |
|---|---|
| PDF page 5, Section III-C | Constant-radius round curves represent swept spheres; successive poses define piecewise-linear centers; directed obstacle edges address inside starts. |
| PDF page 7, Section V-A.2 | The RT-CCD method detects collisions with mesh edges, not face-only intersections. |
| PDF page 10, Algorithm 2 and Appendix D | The directed graph is constructed to preserve CCD correctness. |

These page/section locators were obtained by human static inspection of the
exact hash-bound PDF. The authority binds the PDF bytes and records the
locators, but does not claim a dependency-free mechanical re-extraction of PDF
text. A reviewer must check those exact pages for semantic audit.

The exact author source establishes the actual benchmark call chain:

| Source | Bound observation |
|---|---|
| `RTCD/Meshes/mesh.h` | Builds a directed loop edge set and emits selected forward and reverse directions. |
| `RTCD/CollisionScenes/obstacle.h` | Selects the loop/directed edge set when requested. |
| `RTCD/Benchmark/Curve/benchmark.cpp` | The continuous benchmark invokes `buildSharedScene(true)`, so it actually enables directed loop edges. |
| `RTCD/Robot/batchCurveRobot.h` | Pose samples form round-linear curves, sphere radius becomes curve width and round endcaps are enabled. |
| `RTCD/CollisionDetector/CCCuda.cu` | Finite obstacle-edge rays increment per-trajectory hit counts. |
| `RTCD/CollisionDetector/CollisionDetector.h` | Uses one-sided ray generation and built-in round-linear endcaps. |
| `RTCD/CollisionDetector/Test/testCollisionCheckerCurve.cpp` | Positive hit count means collision; the selected linear route uses round caps, while a quadratic test separately composes endpoint-pose results. |

Every source observation in the authority also carries exact line numbers and
an anchor SHA-256. The report does not rely on an unpinned web rendering or
model memory.

## 4. Semantic classification matrix

| Dimension | Decision | Reason |
|---|---|---|
| Piecewise-linear swept-sphere representation | `MATCH` | Both routes map successive sphere centers to round-linear swept volumes. |
| Constant radius and linear endcaps | `MATCH` | Both use a constant positive radius/width and round endcaps. |
| Finite-edge hit to Boolean reduction | `MATCH_AT_BOOLEAN_PREDICATE_LEVEL` | Author count greater than zero and Goal5835 OR reduction express the same selected Boolean abstraction. |
| Face-interior-only collision | `MATCH_LIMITATION` | Both intentionally omit collisions that touch no mesh edge. |
| Obstacle-edge direction contract | `MATERIAL_PREDICATE_DIFFERENCE` | The author benchmark uses a strongly connected directed edge graph; Goal5835 deduplicates an unordered edge and preserves one arbitrary first direction. |
| Inside-start and initial-overlap coverage | `MATERIAL_PREDICATE_DIFFERENCE` | The author connectivity invariant recovers a one-sided outside-to-inside crossing when another edge direction begins inside the hollow curve; Goal5835 explicitly excludes start-inside/initial-overlap behavior. |
| Discrete endpoint/pose composition | `MATCH_FOR_SELECTED_LINEAR_SUBPATH_ONLY` | Round caps cover the selected linear route. No quadratic-route claim is made. |

## 5. Why edge direction changes the predicate

The direction difference is not an implementation detail or optional
optimization. The author route traces one-sided finite obstacle-edge rays
against hollow OptiX curves. A ray beginning inside a hollow curve can present
only the back face and miss. The paper and source therefore require a strongly
connected directed edge graph so that the obstacle traversal supplies a
direction that enters the swept volume from outside.

Goal5835 canonicalizes shared edges by unordered vertex identity and lets the
first sorted triangle occurrence choose one direction. It proves neither
strong connectivity nor outside-to-inside availability, and its README
explicitly excludes initial overlap. Consequently there exist inputs accepted
by the author's predicate contract that are outside Goal5835's predicate. The
two mappings cannot be called source-faithful merely because ordinary crossing
fixtures, radius semantics and Boolean reduction match.

## 6. Frozen consequence

The predecessor preaction requires `MATERIAL_PREDICATE_DIFFERENCE` to produce
an unconditional terminal mapping refusal. A1 therefore preserves Goal5835 as:

```text
paper_app_status: NOT_A_PAPER_APP
source_relation:
SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES__A1_MATERIAL_PREDICATE_DIFFERENCE
complete_rtccd_claimed: false
performance_claimed: false
generalization_exam_count: 0
```

No input may be substituted, no route may be materialized and no GPU result
can repair this transaction after the classification was observed. A future
attempt would require a separately owner-defined and preregistered successor
goal that introduces an application-neutral directed-connectivity/orientation
contract and new evidence. It must not edit this authority or relabel Goal5835.

## 7. Verification

```text
python3 scripts/goal5836_a1_build_source_fidelity.py --verify-stored
python3 -m unittest tests.goal5836_a1_source_fidelity_test -v
python3 -m unittest discover -s tests -p 'goal583[3-6]*_test.py'
```

The stored verifier passes. All 18 A1 hostile tests pass. The complete
Goal5833--Goal5836 regression is 148/148. Hostile cases include coordinated
re-sealing attempts that try to upgrade the classification, authorize or
reopen A2, hide a material row, inflate claims, introduce forbidden
observations, drift exact capsule bytes or use non-relative identity paths.

## 8. Final claim

> Static inspection of the exact arXiv v2 paper and exact author commit found
> that Goal5835 matches the selected paper route's ordinary piecewise-linear
> swept-sphere, radius/endcap, edge-only and Boolean semantics, but does not
> preserve the author's directed-connectivity invariant or inside-start
> coverage. Goal5836 therefore terminates at A1 without input freeze,
> execution, performance evidence or Paper-App promotion.
