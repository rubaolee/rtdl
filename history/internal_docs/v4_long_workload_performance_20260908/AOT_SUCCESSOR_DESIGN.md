# AOT successor design after the first frozen long-workload transaction

Date: 2026-09-08, America/New_York. Status: implemented and formally evaluated;
the text below preserves the pre-implementation design record. This document
does not authorize a public or manuscript claim or convert any predecessor
failure into passing evidence.

## Observed problem

The first complete Particle subset at source `f8dcd81da...` produced identical
outputs in all arms but failed the registered RTDL/PyOptiX performance target.
Its eight paired new-RTDL/PyOptiX block ratios have median `10.239579777` and
maximum `11.397902695`. Phase records show that RTDL spends approximately
25--27 seconds in preparation, which recompiles the restricted callback in
every fresh worker, while the competent PyOptiX arm consumes preregistered
prebuilt PTX. The matching prepared subset passes all eight blocks: median
`0.896053812`, maximum `0.926278816`.

This separates two questions. The repaired public RT execution path has
acceptable steady cost. The paper-app measurement path does not yet use RTDL's
compile-once, verify-and-load deployment lifecycle, so its complete endpoint is
not deployment-competent.

## Required successor architecture

1. Build RTDL executable artifacts outside every measurement transaction from
   a clean, exact source/native/toolchain identity. Preserve the compiler,
   verifier, typed physical schema, callback ABI, target, and native hashes in
   the artifact and detached authority or equivalent deployment record.
2. Freeze the artifact, authority/trust material, and every SHA-256 in the new
   formal config before worker zero. A missing, extra, mutated, or wrong-target
   artifact must fail closed.
3. Make the public new-RTDL arm use the same artifact for both endpoints. The
   complete endpoint starts from in-memory domain input and includes verified
   artifact admission, native/provider binding, static/dynamic input
   deployment, prepare, one natural execute, result construction, and close.
   It excludes offline source compilation just as the PyOptiX arm excludes PTX
   compilation. Artifact verification remains included and separately timed.
4. The prepared endpoint reuses the resulting owner exactly as before: one
   untimed warmup followed by the frozen natural-call count. It must not gain
   extra warmups, checker-off behavior, or a different kernel from complete.
5. Preserve old-v4 unchanged as an adverse predecessor arm. Preserve PyOptiX's
   prebuilt PTX, device continuation, output contract, and lifecycle; do not
   weaken C to manufacture parity.

## Application-neutral boundaries

- Particle may use the existing verified strict-interior built-in-triangle
  specialization only when its declared unique-hit, positive-barycentric,
  query-count, output, and fail-closed domain preconditions are proven. The
  dispatch key is the verified physical contract, never the application name,
  dataset hash, expected answer, or benchmark size. Inputs outside that domain
  must reject or use the existing general path.
- Graph RT-2A1 should use the generic `builtin_triangle_reduction_v1` family.
  The executable may be reused across segments, while segment-specific GAS and
  dynamic columns remain correctly rebuilt or rebound. Graph orientation,
  segmentation, checked-U64 accumulation, and final oracle remain app-owned.
- LibRTS should change only if its completed formal phase evidence identifies
  the same compile/deployment debt. Any AOT route must be the existing generic
  bounded-relation or reviewed shape-level AABB-count contract, not an
  operation-name branch in the engine.

## Mandatory correctness and safety gates

- Exact output parity among old RTDL, successor RTDL, PyOptiX, and the frozen
  independent oracle for every registered unit and endpoint.
- Artifact, authority, native library, source tree, target, SDK, compiler, and
  GPU identity rejection tests.
- Wrong artifact family, wrong physical schema, wrong native image, malformed
  inputs, overflow, close-after-use, repeated close, process drift, and
  reentrancy tests for every affected lifecycle.
- Actual native/OptiX execution receipts and device status remain mandatory.
  No cached expected answer, host-only shortcut, or checker-off result is
  admissible.
- For segmented graph execution, test immutable executable reuse separately
  from mutable per-segment geometry and query data; stale GAS/data reuse must
  fail or be structurally impossible.

## Successor measurement gate

After implementation and local/pod regression tests, create a new commit,
native build, AOT artifact set, config, 15-worker dry run, preregistration, and
wholly fresh 240-worker transaction. Do not reuse any formal row from
`f8dcd81da...`. Each of the ten unit/endpoint evaluations must retain eight
paired blocks, paired new-RTDL/PyOptiX median `<= 1.20`, every block `<= 1.35`,
identical outputs, and zero retry/discard. All adverse successor rows remain
reportable.

## Claim boundary

Passing this successor would show that the measured restricted callback
programs can be deployed once and then loaded for application execution at the
registered costs. It would not establish arbitrary topology support, universal
language overhead, all nine applications, all GPUs, or zero-cost verification.

## Post-implementation disposition

The design was realized by the successor ending at commit `02e84374f...` and
evaluated in a wholly fresh affinity-controlled transaction. All ten registered
unit-endpoint rows passed the stated thresholds; a project-independent recount
returned `PASS__METHOD_AND_TARGET`. Exact results and custody are in
`RESULTS.md` and `EVIDENCE_INDEX.json`.

The realized scope remains narrower than the architecture ideal above.
Particle uses an existing fixed 5,000-query, strict-interior, app-shaped native
standard-library specialization. Graph uses the generic verified
`builtin_triangle_reduction_v1` family, and LibRTS uses typed AABB count
families. Accordingly, the result supports bounded-family deployment for the
registered routes, not arbitrary callback or application-neutral-engine
performance.
