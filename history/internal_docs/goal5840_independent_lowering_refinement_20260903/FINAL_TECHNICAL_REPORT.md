# Goal5840 final technical report

Date: 2026-09-03

Status:
`PASS__GOAL5840_COMPLETE_AT_PREREGISTERED_BOUNDED_REFINEMENT_SCOPE`

Final authority seal:
`3857a8c1f579808ea96a2f54c58e5698818deae7b879c849523ccf72a3f59a80`

## Executive result

Goal5840 addresses reviewer attack R3: RTDL's declaration-side projections,
hashes, and mutation liveness do not by themselves show that accepted language
semantics survive concrete lowering. The goal therefore built a separate
target-side extractor/checker that consumes exact generated artifacts, ABI
metadata, native producer evidence, runtime bindings, and execution receipts.
It does not import RTDL's declaration-side projection builders.

One fresh Attempt-07 run from clean commit
`79fdbb61c2afd602a16e8fc01b27d0cf8a576e7b` passed the complete frozen
denominator:

| Result | Observed |
| --- | ---: |
| Route groups | 3 |
| Required execution modes | 4 |
| True OptiX modes | 4/4 |
| Expected outputs matched | 4/4 |
| Independent property checks | 20/20 |
| Unique preregistered mutation units | 15/15 rejected |
| Mode-replicated mutation applications | 20/20 rejected |
| Goal5838 frozen-core files changed | 0/3 |

The Pod result seal is
`ff2a71ca1331219da5a89dd0f4f847637ebe406fb9403ac95d7b9c34830b3049`.
The downloaded-artifact verification seal is
`574b46be2a2d65a27cb3c3e2b1cdbf2371998ab8d2f5ecc8626b06a0d5448f60`.
Two Mac verifier executions produced byte-identical output.

This is bounded structural lowering/refinement evidence for the exact three
routes and five properties. It is not a general compiler-soundness theorem,
arbitrary Callback-IR support, application correctness, performance evidence,
external review, or consensus.

## Why this work matters

Before Goal5840, RTDL could show that a declaration was admitted, that a
provider executed, and that selected mutations were rejected. A hostile
reviewer could still argue that declaration and implementation merely repeated
the same misconception. Hash equality proves identity, not semantic
correctness. A test produced by the same projector can also agree with itself
while lowering the wrong behavior.

Goal5840 narrows that gap. For each supported route, the checker separately
extracts target facts from raw generated Python/CUDA/PTX text, compiled ABI
records, native build-input descriptors, SBT and buffer receipts, physical
traversal receipts, and executable identity preimages. It then compares those
facts with the admitted source contract. The mutation suite changes the exact
generated bundle after admission, recomputes untrusted internal hashes, and
requires target-side rejection before another GPU launch.

The contribution is therefore not another callback, benchmark, or wrapper. It
is an auditable bounded argument that selected RTDL semantic obligations remain
connected to the artifact that reached true OptiX execution.

## Frozen question and denominator

The preregistration fixed five properties before implementation:

| ID | Property |
| --- | --- |
| CP001 | Role/effect closure |
| CP002 | Semantic ABI ownership |
| CP003 | Physical binding |
| CP004 | Status-gated continuation and completeness |
| CP005 | Executable identity chain |

The denominator is 3 route groups x 5 properties, or 15 unique claim units.
Triangle reduction has two required modes, so the exact mutation suite applies
20 route/mode/property mutations. Uncovered cells could not be silently
removed; they would have failed the preregistered result.

## Supported routes and observed outputs

| Route | Mode | Frozen expected and observed output | Independent checks | True OptiX |
| --- | --- | --- | ---: | --- |
| `bounded_relation` | fail-closed bounded pair collection | `[(100,10),(100,30),(200,20)]` | 5/5 | yes |
| `triangle_reduction` | all-hit count | `5` | 5/5 | yes |
| `triangle_reduction` | weighted-hit count | `35` | 5/5 | yes |
| `builtin_sphere` | any-hit count and continue per query | counts `[4,1,1,0,4,0]` | 5/5 | yes |

The first three modes exercise two stable routes. The sphere mode is the
independently selected Goal5838 topology. It has a two-level lowering: an outer
generic family plan and an inner physical built-in-sphere plan. The final
checker derives the inner plan and its authority from the outer callback/effect
contract, the physical-schema protocol authority, the target identity, and the
fixed physical template. It does not incorrectly require the inner and outer
plan hashes to be equal.

## What true OptiX means here

The final evidence does not classify code as OptiX merely because it resides in
an OptiX-linked library. Each mode records target/native binding, a nonzero
OptiX traversable, SBT and buffer contracts, physical producer evidence,
successful runtime status, and an
`optix_traversal_observed` execution receipt. The sphere route additionally
binds the built-in-sphere physical plan and its native-producer and traversal
nonces.

The fresh provider DSO is 7,181,936 bytes with SHA-256
`8060367df223bbcedd45bf8002820ee45338047c977dde93a4951ce67a27de4c`.
The runner bound `RTDL_OPTIX_LIB` to that exact admitted DSO before every route
was materialized.

## Exact execution environment

The owner supplied the endpoint `root@213.173.108.100:12943`. Environment
repair and compatible tool selection were agent-owned.

| Property | Value |
| --- | --- |
| GPU | NVIDIA RTX 2000 Ada Generation, 16,380 MiB |
| Driver | 580.159.04 |
| Compute capability | 8.9 |
| CUDA include | CUDA 12.8 target include tree |
| OptiX SDK | 9.0.0 |
| Python | 3.12.3 |
| NumPy / Numba | 2.4.4 / 0.65.1 |
| Source state | clean detached checkout of `79fdbb6...` |

The provider was rebuilt in a new build directory from that checkout. Its
manifest binds ten native source blobs, the compiler inputs, dynamic NVRTC,
required ABI symbols, output DSO, and clean Git custody. Goal5840 separately
checked all 17 symbols needed by its three routes; the downloaded ELF contained
all 17 among 861 exported dynamic symbols.

## Attempt history and repair validity

Attempts 1 through 6 are retained as unaccepted engineering failures. They did
not change the preregistered routes, modes, fixtures, expected outputs, five
properties, or 15-unit denominator.

| Attempt | Failure found | Accepted complete result |
| ---: | --- | --- |
| 1 | SSH/transport custody defect | no |
| 2 | enum-role evidence mismatch | no |
| 3 | inline CP001 checker defect | no |
| 4 | stale CP004 control-flow anchor | no |
| 5 | exact runtime DSO was not bound for sphere lookup | no |
| 6 | checker equated distinct outer and inner sphere plan hashes | no |
| 7 | fresh build and complete frozen run | yes |

Every repair was documented and frozen before the next formal attempt. No
post-failure GPU diagnostics were relabelled as evidence. Attempt 7 started once
with a previously absent output directory and produced exactly the expected 11
files.

This history is a limitation as well as a validity control. The checker was
debugged against earlier instances of the same bounded routes, so Attempt 7 is
not a blind test of checker generalization. It establishes exact-route
refinement evidence, not unseen-route coverage.

## Independent replay and mutation result

The complete off-repository raw capsule was 3,170,210 bytes with SHA-256
`adfe14c69913c8234f5b301ea32bb4ceb231683058ee81009c740cfc2d027347`.
The hash matched before and after transfer to the Mac. The raw capsule contains
the 11 evidence files, native build directory, DSO, and execution log. The
generated DSO is intentionally not committed to Git; its source/build identity
and digest are committed, and rebuilding is required if the separately retained
raw capsule is lost.

The Mac verifier did not trust the Pod's aggregate PASS field. It reparsed the
downloaded ELF symbol table, revalidated Git blobs from the caller-supplied
commit, checked every internal domain-separated seal, reran all four standalone
target checks, and independently replayed all 20 mutations. A second execution
produced identical bytes.

Each mutation changed a generated-artifact or runtime-binding fact and
recomputed untrusted hashes. Every checker verdict was `REJECT`, every target
property verdict was `REJECT`, and no mutation needed another GPU launch. This
shows liveness for the frozen mutations. It does not show that the mutation set
enumerates every possible compiler defect.

## Trusted computing base

The bounded result still trusts:

- the evidence capturer and runtime trust-root recorder to expose the relevant
  raw bytes;
- the separately implemented target checker and its bounded parsers;
- the Python runtime, standard library, Git object database, and SHA-256 as an
  integrity commitment;
- the host compiler, NVRTC, NVVM, PTX toolchain, OptiX, CUDA driver, and GPU;
- the correctness of the exact-route physical templates and source anchors.

The result has no cryptographic signature or independent hardware attestation.
An external caller-supplied Git commit is the durable trust root. Goal5841 and
Goal5843 retain the external review gates.

## Verification gates

At closure:

- Goal5840 tests pass 65/65;
- final authority rederivation passes;
- both Mac verification files are byte-identical;
- Goal5838 frozen-core seal verification passes with zero changed bytes;
- inherited route regressions remain required in the final gate;
- Python compilation and `git diff --check` remain required before commit.

## Exact conclusion

Goal5840 supplies evidence against the narrow R3 claim that RTDL's accepted
semantics are checked only by declaration-side projections produced by the same
implementation. For three exact route groups, four true-OptiX modes, and five
bounded properties, a separate target-side checker accepted all positive
artifacts and rejected all preregistered generated-artifact mutations.

This is a useful CGO contribution because it changes the evidence model from
self-consistency to source-to-target refinement checks. The six harness repairs
are not themselves academic novelty; they are the cost of making that evidence
auditable. Goal5840 stops here rather than spending more time on infrastructure.
The next scientific work is external-human authoring evidence and causal
admission-cost/performance evaluation.
