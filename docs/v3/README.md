# RTDL V3.0

RTDL V3 is a compiler-supported, finite Action language for non-graphical
ray-tracing workloads.  An application chooses its algorithm and states a
typed semantic contract.  The compiler resolves the one registered canonical
physical provider for that statement and target contract, validates its proof
and resource obligations, materializes it, and fails closed if any identity or
obligation does not match.

V3 is deliberately **not** a general query optimizer and does not synthesize
arbitrary OptiX callback programs.  It supports a reviewed universe of Action
contracts and generic physical families.  Extending that universe is an
explicit compiler-development operation, not an application callback escape
hatch.

## Read in this order

1. [Architecture](architecture.md)
2. [Correctness and extension model](correctness_and_extension.md)
3. [Nine-application support matrix](support_matrix.md)
4. [V3 release and installation](release.md)
5. [Canonical lowering tutorial](../../tutorials/v3_canonical_lowering.md)
6. [GitHub release-surface audit](release_audit_20260810.md)

## Release guarantees

- One clean portable source artifact can rebuild its target-native OptiX
  library instead of carrying a foreign prebuilt binary.
- Nine applications pass exact-output functional qualification on Home Linux.
- All required physical regions carry behavior-level OptiX traversal receipts;
  names such as `backend="optix"` are not accepted as proof.
- Canonical resolution binds semantic statement, backend contract, provider
  source, ABI, proof, resource bounds, target identity, and the materialized
  plan.
- Missing, ambiguous, forged, stale, or resource-ineligible mappings fail
  before execution.

## What is not claimed

- completeness for arbitrary Python or arbitrary user-defined callbacks;
- discovery of a globally fastest plan;
- universal no-slower performance against V2 or author code;
- hardware RT-core utilization inferred from an OptiX label alone;
- universal performance superiority, arbitrary physical-plan synthesis, or a
  managed binary service.

The precise qualification identity and installation path are in
[V3 release and installation](release.md). See also the
[V3.0.0 release notes](release_notes_3_0_0.md).
