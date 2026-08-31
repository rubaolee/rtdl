# Strict self-review: Goal5834 built-in round-linear curves

Date: 2026-08-30  
Disposition: **PASS at bounded functional scope; claim ceiling mandatory**

## Adversarial verdict

I tried to reject Goal5834 as a compiler/RT systems reviewer. The final result
survives the relevant attacks, but only after one material correctness repair.

### P0/P1 issue found and closed

The original axial endcap-only query was admitted by the public schema. The
closed-capsule oracle said hit and OptiX said miss. Replacing it with an easier
fixture without changing admission would have been result shopping: the public
claim would still cover a known counterexample.

The final implementation makes the boundary executable. Potential contacts
whose query/curve cross ratio is below `2^-12` are rejected before launch. The
final positive endcap fixture is nonparallel and exact; the original axial
case is retained as a negative test with oracle=hit, rejection reason, and
unchanged native execution count. This closes the correctness defect by
narrowing the declared domain, not by hiding the observation.

### Contract-liveness attack

The Goal5789 failure mode was applied exhaustively. The audit mutates every
non-null serialized ABI scalar occurrence (611), every physical-schema scalar
occurrence (35, including 11 compiler-owned buffer/hit declarations), every
target field (6), and every canonical-plan field (7). No mutated populated leaf
remained silently admissible. The four semantic roles also executed on GPU;
the counters match the expected hit/miss mix.

### Physical-substitution attack

The runtime descriptor and independent verifier require the exact curve build
input and round-linear primitive enums, primitive flags, default linear endcap,
built-in IS module, no user IS, static build, one GAS, one SBT record, no
motion, graph depth one, exact strides/counts, nonzero buffer and traversable
identities, and equal host/device fingerprints. A different native DSO,
different target version, stale plan, altered wrapper/PTX, or altered static or
query bytes changes identity or fails.

### Status/lifecycle attack

Status is downloaded and accepted before six application output columns.
Receipts record one status D2H, zero output-after-status-failure, and six output
D2Hs only on success. The prepared owner is process/thread bound,
nonserializable, nonreentrant, repeatable before close, and rejects use after
close. The tangent and axial negatives do not increment the execution count.

### Shared-code regression attack

Goal5834 factored the trusted First Contact wrapper and NVRTC helper out of the
sphere path. That could have silently broken Goal5833. The full 70-test
Goal5833 local set passes, and a fresh Home sphere execution using the exact
new native DSO is independently exact. This is functional regression evidence,
not a performance comparison.

## Remaining limitations, not defects hidden by the result

1. Only static, constant-radius-per-segment round-linear curves are supported.
   Tapered widths, other curve bases, motion blur, instancing, multiple GASes,
   multiple ray types, continuation, and deeper trace/callable graphs remain
   unsupported.
2. The numeric domain deliberately rejects near tangency, contacts near trace
   endpoints, starts inside a capsule, and potential near-parallel contacts.
3. The application and fixture are author-designed. This is not prospective
   generalization, an external-user result, or a Paper App.
4. The Home GPU is GTX 1070. The receipt proves OptiX traversal, but not RT-core
   silicon behavior and not performance.
5. The independent oracle is separately implemented and imports no RTDL, but
   it tests the same declared capsule mathematics; it is not a formal proof of
   all floating-point behavior.
6. `4/4` is only leaf-kind presence in the project's pinned taxonomy. It does
   not mean four complete geometry families or complete OptiX coverage.
7. The fresh source directory reused a previously verified dependency venv and
   OptiX SDK rather than provisioning a new operating system image.
8. The Git object database is damaged; no commit or clean-status statement can
   be verified. Hash-bound archives and raw evidence substitute for source
   custody in this goal, not for long-term repository repair.

## Final decision

Goal5834 is genuinely complete for its controlling bounded scope. The result
adds a real public built-in curve route, exact capsule semantics on the accepted
numeric domain, actual OptiX execution, exhaustive leaf liveness, and an
independent recount. It must not be described as general curve support or as
evidence that an unseen RT-repurposed application will work.

The next scientific step is Goal5835: use this app-neutral curve mechanism to
implement the bounded piecewise-linear RT-CCD kernel. That goal must treat the
new near-parallel exclusion as an explicit applicability condition rather than
silently assuming every robot/obstacle configuration is admitted.
