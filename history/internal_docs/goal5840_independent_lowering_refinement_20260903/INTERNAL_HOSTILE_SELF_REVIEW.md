# Goal5840 preregistration hostile internal self-review

Date: 2026-09-03

Scope: preregistration quality only. No extractor, mutation, GPU or
preservation result exists yet.

Verdict: `ACCEPT_PREREGISTRATION__DO_NOT_ACCEPT_GOAL_RESULT`

## Findings

### P1: structural separation is not semantic independence

An AST import ban and isolated process show that the checker does not call the
existing RTDL projectors. They do not prove that two implementations do not
share the same conceptual mistake. The final claim must therefore be “separate
target-side extraction for three bounded routes,” not an independently proved
compiler theorem. External critical review remains a later gate.

### P1: the target evidence bundler remains trusted

The checker cannot recover bytes that the bundler omits or detect a false
semantic label merely because the label is hash-bound. The preregistration
correctly places the bundler in the TCB and requires raw source/PTX anchors plus
producer/consumer evidence. The implementation must fail closed when an
executable fact lacks such an anchor; it may not synthesize a convenient marker
and then “independently” parse that marker.

### P1: CP004 is the highest-risk implementation obligation

Status-before-output and completeness are control-flow properties. Symbol and
metadata equality alone cannot establish them. Each supported route needs a
bounded source/PTX control-flow rule and a mutation that removes or reorders the
guard while recomputing untrusted hashes. If that cannot be implemented, the
affected route/property cell must be removed from the preservation statement,
which fails the preregistered 15-cell goal.

### P2: logical mutation selectors precede the bundle schema

The 15 selectors are intentionally frozen before implementation, but their
concrete JSON pointers do not yet exist. The implementation may define a
one-to-one schema path for each selector and record that mapping. It may not
replace a selector with an easier mutation. An unmappable selector is a failed
claim unit.

### P2: the baseline is Git-dependent

The mutable baseline files are bound to commit `2f256d5...` and SHA-256 values,
not copied into a separate source capsule. This is sufficient while the pushed
Git revision remains available, but a clean artifact capsule would need to
include those baseline blobs before submission.

### P2: positive execution remains unavailable locally

macOS can implement and test deterministic evidence schemas and pre-launch
mutation rejection, but it cannot create new true-OptiX receipts. Goal5840
cannot pass until all three exact positive routes are captured on an NVIDIA
OptiX environment. Missing GPU evidence is pending work, not a negative
scientific outcome.

### P2: same-author bias remains

The project author and Codex are designing both the production evidence path
and the separate checker. The prospective mutation freeze limits post-hoc
adaptation but does not substitute for independent external review. No external
review or consensus may be claimed while the travel constraint remains.

## Decision

The preregistration is sufficiently specific to begin implementation: scope is
three routes, the denominator is 15 route/property cells, every mutation target
is frozen, and failure/claim boundaries are explicit. The review accepts only
that experimental design. It supplies no evidence that lowering preservation
has been established.
