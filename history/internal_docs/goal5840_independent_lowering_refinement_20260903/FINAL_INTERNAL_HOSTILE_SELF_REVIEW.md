# Goal5840 final internal hostile self-review

Date: 2026-09-03

Review mode: strict internal review only. The owner deferred external review
while traveling. This document is not independent review or consensus.

Verdict: `ACCEPT_AT_PREREGISTERED_BOUNDED_REFINEMENT_SCOPE`

Finding count: `P0=0`, `P1=0`, `P2=6`, `P3=3`.

## Reviewed surfaces

This review inspected the preregistration, pre-Pod authority, all six preserved
failure reports and repair authorities, final source commit, native build
manifest, four raw target bundles, four independent checker reports, runtime
trust roots, exact mutation report, Attempt-07 log, Pod result, two byte-equal
Mac verification results, final authority builder, tests, and technical report.

It reran the Goal5840 test discovery, final authority rederivation, frozen-core
seal verification, inherited route tests, Python compilation, and Git diff
checks. No external AI or human result was consulted.

## P0 findings

None.

There is no evidence that a non-OptiX path was called true OptiX, that an
earlier partial attempt was promoted, that expected outputs were changed after
execution, that mutation failures were hidden, or that frozen-core bytes were
modified.

## P1 findings

None within the exact bounded claim.

A claim of general compiler soundness, arbitrary Callback IR, checker
generalization, application correctness, performance, or independent consensus
would create a P1 finding immediately. The final authority encodes all of those
claims as false.

## P2 findings

### P2-1: checker independence is structural, not independent authorship

Codex implemented both the production evidence path and the separate checker.
The checker has a standard-library-only execution mode, does not import RTDL
projection builders, and derives target facts from different representations.
That prevents direct implementation reuse but not shared conceptual bias.
External critical review remains mandatory before manuscript closure.

### P2-2: six repairs create an overfitting risk

Attempts 1 through 6 exposed real evidence and checker defects. In particular,
Attempt 6 revealed the sphere route's two-level physical plan. The final checker
repair is principled and its self-consistent attacker test is stronger, but it
was designed after seeing an instance of the same route. Attempt 7 is therefore
a clean final execution, not a blind checker-generalization experiment. The
claim must stay limited to the exact routes.

### P2-3: the capturer and trust-root recorder remain in the TCB

The checker cannot reconstruct bytes that the capturer omits. The runtime
executable root is observed after materialization by the same runner, not by an
independent hardware attestor. Raw source/PTX, producer/consumer receipts, exact
DSO binding, and an external Git commit reduce accidental inconsistency; they do
not defeat a malicious capturer.

### P2-4: CP004 is bounded syntactic evidence

Status-before-output and continuation completeness are checked using exact AST,
source/PTX anchors, native source manifests, and runtime receipts for three
known routes. This is not a general control-flow proof and does not prove the
NVIDIA compiler, OptiX implementation, or hardware semantics.

### P2-5: one mutation per route/property is liveness, not completeness

All 15 unique mutations and 20 mode applications are rejected after untrusted
hashes are recomputed. This demonstrates that every frozen property check is
live against one selected fault. It does not establish that these mutations
span every bug capable of violating the property.

### P2-6: the native DSO is not committed

The DSO and complete raw transfer capsule are separately retained and
hash-bound, while Git contains all raw JSON bundles, the build manifest, exact
source identities, and the reproduction command. A future reviewer can inspect
the result without the DSO, but a fresh ELF replay needs the retained capsule or
a rebuild.

## P3 findings

### P3-1: the route and fixture denominator is small

Three route groups and four deterministic fixtures are sufficient for the
preregistered bounded question. They do not represent the full language or an
application corpus.

### P3-2: no performance data was collected

Goal5840 tests correctness of the evidence relation. It does not measure
checker overhead, preparation cost, steady execution, or speedup. Goal5842 owns
that question.

### P3-3: external review remains zero

The result has internal hostile review only. It cannot be described as 2-AI,
3-AI, independent-human, or external consensus evidence.

## Adversarial questions

| Attack | Review answer |
| --- | --- |
| Is this still the same implementation checking itself? | The author is shared, but the target checker is separately implemented, cannot import declaration projectors, and parses generated artifacts and runtime receipts. This narrows rather than eliminates same-author bias. |
| Did hashes prove semantics? | No. Hashes bind bytes and identities. CP001 through CP004 compare separately extracted bounded facts; CP005 uses identity binding. |
| Could the mutation suite pass by changing an unobserved field? | Each frozen mutation must produce both checker and property rejection after untrusted hashes are recomputed. A self-consistent sphere rewrite is also rejected by the externally supplied executable identity root. This proves liveness for those mutations only. |
| Was Attempt 7 rerun until favorable? | No. The final output path was absent, one PID was started, and one terminal PASS appears in the preserved log. Attempts 1 through 6 remain separately documented and unaccepted. |
| Is this only CUDA inside an OptiX DSO? | No. All four modes carry `optix_traversal_observed` physical receipts plus traversable/SBT/buffer/native binding evidence. |
| Did the sphere checker compare the wrong plan levels? | Attempt 6 did and was rejected. Attempt 7 independently derives the inner physical plan and authority while retaining the distinct outer generic plan. |
| Can a malicious runner fabricate everything? | The current evidence is integrity-bound, not remotely attested. A malicious capturer remains outside the threat model and in the declared TCB. |
| Does 20/20 prove compiler soundness? | No. It proves five properties for four modes and liveness for 20 frozen mutation applications. |
| Is this an application or performance result? | No. Both claim fields are false. |

## Value versus engineering overhead

The academically useful result is the bounded source-to-target refinement
evidence and explicit TCB, not the SSH wrapper, artifact copying, or six harness
repairs. Those repairs were necessary because accepting a convenient but
incorrect checker would make R3 stronger, not weaker. Once Attempt 7 passed and
the Mac replay agreed byte-for-byte, further harness work became low value and
was stopped.

## Final decision

Accept Goal5840 at exactly the final-authority wording. The result materially
improves the CGO argument against self-consistency criticism, but only as a
bounded executable preservation case series. Preserve every negative claim
field. Do not call it a soundness theorem or independent consensus. Proceed to
Goal5841 and Goal5842 rather than adding more Goal5840 machinery.
