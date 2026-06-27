# Goal1670 All External Partner Analysis Consensus

Date: 2026-05-10

Status: consensus over the Goal1669 in-repo design package plus the two
additional external partner analysis reports from `Z:\rtdl-dev`.

## Sources Reviewed

- In-repo design:
  `docs/reports/goal1669_python_partner_rtdl_partner_choice_architecture_2026-05-10.md`
- In-repo Goal1669 3-AI consensus:
  `docs/reviews/goal1669_python_partner_rtdl_partner_choice_3ai_consensus_2026-05-10.md`
- External Claude report copied from `Z:\rtdl-dev`:
  `docs/reviews/goal1669_external_claude_python_partner_rtdl_design_analysis_2026-05-10.md`
- External Gemini/Antigravity report copied from `Z:\rtdl-dev`:
  `docs/reviews/goal1669_external_gemini_v1_7_partner_architecture_analysis_2026-05-10.md`

## Consensus Verdict

All reports agree on the important architecture:

- RTDL must remain an app-agnostic spatial primitive engine.
- The partner mechanism must not become a new app-specific native backdoor.
- RTDL native code must not link directly against PyTorch, CuPy, RAPIDS, JAX,
  or another partner framework.
- The stable design center is standard tensor interop: `__dlpack__`,
  `__dlpack_device__`, and named fallback protocols such as
  `__cuda_array_interface__`.
- Partner selection must be pluggable and switchable from Python.
- True zero-copy is a measured claim boundary, not a default assumption.

The only material disagreement is the first partner priority. The in-repo
Goal1669 design recommended CuPy as the first blessed implementation, with
PyTorch as first follow-up. Both additional external reports recommend PyTorch
as the primary/reference partner and CuPy as secondary validation.

The reconciled consensus is:

```text
Build the protocol and adapter registry first.
Use CuPy as the lightweight conformance and CI validation partner.
Use PyTorch as the primary public/reference partner for the v1.7 prototype.
Do not let either partner define the engine ABI.
```

This keeps the clean CuPy-first engineering advantage while accepting the
external reports' point that PyTorch is the stronger public stress test and
ecosystem target.

## Partner Roles

| Role | Partner | Reason |
| --- | --- | --- |
| Stable contract | DLPack-compatible descriptor protocol | Keeps RTDL independent from any framework |
| Primary public/reference partner | PyTorch | Largest ecosystem, strongest allocator/stream stress test, highest-value spatial ML path |
| Lightweight conformance and CI partner | CuPy | NumPy-like GPU arrays, simple install/test shape, catches PyTorch-specific leakage |
| CPU/Embree partner | NumPy first, Arrow later | Validates host descriptors without GPU zero-copy claims |
| Later specialized partners | Numba, Triton-mediated workflows, RAPIDS/cuDF, JAX | Useful after core handoff, lifetime, and fallback semantics are proven |

## Accepted Architecture

The accepted architecture is protocol-first:

```text
Python app/domain logic
  -> selected partner adapter
  -> generic RTDL tensor/buffer descriptor
  -> app-agnostic RTDL primitive engine
  -> partner-owned or RTDL-owned result descriptor
```

The native engine sees only generic descriptors, primitive packets, traversal
inputs, reductions, access modes, and synchronization metadata. It must not see
domain words such as database, graph, robot, polygon, table, column, BFS, KNN,
Jaccard, or Hausdorff.

The partner adapter layer may know framework mechanics such as PyTorch tensor
ownership, CuPy arrays, DLPack export, CUDA array interface, streams, events,
and fallback copies. It still must not implement app-specific database, graph,
robot, or GIS semantics inside the RTDL engine.

## First Implementation Policy

The first implementation should not start with app demos. It should start with
the interop substrate:

1. `PartnerAdapter` registry and deterministic selection rules.
2. Generic `RtdlTensorDescriptor`.
3. Generic `RtdlOutputSpec`.
4. PyTorch adapter as the primary reference path.
5. CuPy adapter as the conformance and CI validation path.
6. Embree/NumPy host descriptor acceptance path.
7. One OptiX primitive, preferably `ANY_HIT` or `COUNT_HITS`.
8. Strict parity and phase timing.
9. Generated claim-boundary artifact for every run.

The first PyTorch slice must include PyTorch-specific hazards:

- caching allocator behavior;
- stream ordering;
- borrowed output tensors;
- grad-enabled tensors rejected or explicitly detached;
- non-contiguous tensor validation;
- no autograd integration claim.

The first CuPy slice must prove the design is not PyTorch-specific:

- CuPy-owned input tensors;
- CuPy-readable output;
- `__dlpack__` primary path where supported;
- `__cuda_array_interface__` only as a named fallback;
- no hidden host roundtrip under `fallback="error"`.

## Fallback And Claim Boundary

All reports agree that fallback behavior must be explicit.

Recommended modes:

- `error`: required for performance evidence and zero-copy/device-resident
  claims.
- `copy`: allowed for compatibility, never true zero-copy evidence.
- `host_stage`: compatibility only, not performance evidence.

Blocked wording until separately proven:

- "RTDL has general true zero-copy support."
- "RTDL accelerates arbitrary PyTorch/CuPy programs."
- "RTDL optimizes partner code."
- "RTDL native internals are fully app-agnostic."
- "All partners are interchangeable with no performance differences."

Allowed near-term wording:

```text
RTDL is building a protocol-first Python+partner+RTDL track with PyTorch as the
primary reference partner and CuPy as the lightweight conformance partner.
```

## Relationship To Goal1669

This consensus refines, rather than rejects, Goal1669.

Goal1669 remains correct on:

- protocol-first design;
- app-agnostic engine boundary;
- switchable partner registry;
- deterministic `auto` detection;
- `__dlpack__` primary path;
- explicit fallback modes;
- no premature true zero-copy claims.

Goal1670 supersedes Goal1669 only on first-partner priority:

```text
Old Goal1669 priority: CuPy first, PyTorch follow-up.
Reconciled all-report priority: PyTorch primary/reference, CuPy conformance/CI validation.
```

The implementation should still keep the CuPy path early because it is the
simplest way to test that the protocol is not secretly PyTorch-shaped.

## Final Decision

Proceed with Python+partner+RTDL under this rule:

```text
Protocol first. PyTorch reference first. CuPy conformance alongside it.
Engine absolutely app-agnostic throughout.
```

This is the most balanced plan across all reports. It satisfies RTDL's
architecture constraint, gives the public prototype the strongest ecosystem
partner, and keeps a lightweight independent validation path to prevent
framework lock-in.
