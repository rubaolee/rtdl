# v1.8 / v2.0 Python Partner RTDL Gate

This is the current roadmap and release gate for the track after the v1.6
Python+RTDL architecture milestone.

## Roadmap Rule

The top-level roadmap is:

- `v1.8` finishes Python+RTDL productization.
- `v2.0` finishes Python+partner+RTDL.
- Both milestones require the RTDL engine to stay absolutely app-agnostic.

Python owns application and domain lowering. Partner frameworks own tensor
memory, framework-side allocation mechanics, and optional compute around RTDL.
The RTDL engine owns only generic RT-shaped primitives, primitive packets,
generic reductions, traversal inputs, descriptors, and synchronization metadata.

## Partner Consensus

The accepted partner design is:

```text
Protocol first. PyTorch reference first. CuPy conformance alongside it.
Engine absolutely app-agnostic throughout.
```

This supersedes older first-partner priority wording that chose CuPy as the
first blessed implementation. It does not supersede the protocol-first parts of
Goal1669.

The active partner roles are:

| Role | Accepted choice |
| --- | --- |
| Stable contract | DLPack-compatible descriptor protocol |
| Primary public/reference partner | PyTorch |
| Lightweight conformance and CI partner | CuPy |
| CPU/Embree partner | NumPy first, Arrow later only if app semantics stay outside the engine |

The native engine must not link directly against PyTorch, CuPy, RAPIDS, JAX, or
another partner framework. Partner-specific mechanics belong in Python adapter
code around a generic descriptor contract.

## Implementation Order

The first implementation slice must start with the interop substrate, not app
demos:

1. `PartnerAdapter` registry and deterministic selection rules.
2. Generic `RtdlTensorDescriptor`.
3. Generic `RtdlOutputSpec`.
4. PyTorch adapter as the primary reference path.
5. CuPy adapter as the conformance and CI validation path.
6. Embree/NumPy host descriptor acceptance path.
7. One OptiX primitive path, preferably `ANY_HIT` or `COUNT_HITS`.
8. Strict parity, phase timing, and generated claim-boundary artifacts.

PyTorch tests must cover caching allocator behavior, stream ordering, borrowed
output tensors, grad-enabled tensor rejection or explicit detach behavior,
non-contiguous tensor validation, and no autograd integration claim.

CuPy tests must prove the protocol is not PyTorch-shaped by using CuPy-owned
inputs, CuPy-readable outputs, `__dlpack__` where supported, and
`__cuda_array_interface__` only as a named fallback.

## App-Agnostic Engine Gate

The partner track must not become a new route for app-shaped native code.
Native descriptors and exported callable surfaces must avoid application and
workload vocabulary such as database, graph, robot, polygon, table, column,
BFS, KNN, Jaccard, Hausdorff, agent, or trajectory.

The app-agnostic gate is paired with:

- [v1.7 App-Agnostic Native-Engine Gate](v1_7_app_agnostic_native_gate.md)
- [Goal1668 Native-Engine App-Agnostic Directive Response](../reports/goal1668_native_engine_app_agnostic_directive_response_2026-05-10.md)
- [Goal1670 All External Partner Analysis Consensus](../reviews/goal1670_all_external_partner_analysis_consensus_2026-05-10.md)
- [Goal1675 Partner Protocol Substrate](../reports/goal1675_partner_protocol_substrate_2026-05-10.md)
- [Goal1677 Partner Pod Smoke](../reports/goal1677_partner_pod_smoke_2026-05-10.md)
- [Goal1678 Python RTDL Pod Embree Build](../reports/goal1678_python_rtdl_pod_embree_build_2026-05-10.md)
- [Goal1679 Pod Full-Suite Triage](../reports/goal1679_pod_full_suite_triage_2026-05-10.md)
- [Goal1777 v2.0 Partner Protocol Baseline](../reports/goal1777_v2_0_partner_protocol_baseline_2026-05-12.md)
- [Goal1780 3-AI Consensus for Goal1777](../reviews/goal1780_3ai_consensus_goal1777_v2_0_partner_protocol_baseline_2026-05-12.md)
- [Goal1781 Real-Framework Partner Availability Gate](../reports/goal1781_real_framework_partner_availability_gate_2026-05-12.md)
- [Goal1782 Gemini Review of Goal1781](../reviews/goal1782_gemini_review_goal1781_real_framework_partner_availability_2026-05-12.md)
- [Goal1783 NumPy CPU Partner Adapter](../reports/goal1783_numpy_cpu_partner_adapter_2026-05-12.md)
- [Goal1784 Gemini Review of Goal1783](../reviews/goal1784_gemini_review_goal1783_numpy_cpu_partner_adapter_2026-05-12.md)
- [Goal1785 Linux PyTorch and CuPy Partner Validation](../reports/goal1785_linux_pytorch_cupy_partner_validation_2026-05-12.md)
- [Goal1786 Gemini Review of Goal1785](../reviews/goal1786_gemini_review_goal1785_linux_pytorch_cupy_partner_validation_2026-05-12.md)
- [Goal1787 OptiX Partner Any-Hit Host-Stage Execution](../reports/goal1787_optix_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1788 Claude Review of Goal1787](../reviews/goal1788_claude_review_goal1787_optix_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1789 Gemini Review of Goal1787](../reviews/goal1789_gemini_review_goal1787_optix_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1790 3-AI Consensus for Goal1787](../reviews/goal1790_3ai_consensus_goal1787_optix_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1791 Partner Handoff Phase Timing](../reports/goal1791_partner_handoff_phase_timing_2026-05-12.md)
- [Goal1792 Gemini Review of Goal1791](../reviews/goal1792_gemini_review_goal1791_partner_handoff_phase_timing_2026-05-12.md)
- [Goal1793 Mixed Partner Columns Conformance](../reports/goal1793_mixed_partner_columns_conformance_2026-05-12.md)
- [Goal1794 Gemini Review of Goal1793](../reviews/goal1794_gemini_review_goal1793_mixed_partner_columns_conformance_2026-05-12.md)
- [Goal1795 Embree Partner Any-Hit Host-Stage Execution](../reports/goal1795_embree_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1796 Claude Review of Goal1795](../reviews/goal1796_claude_review_goal1795_embree_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1797 3-AI Consensus for Goal1795](../reviews/goal1797_3ai_consensus_goal1795_embree_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1798 Gemini Review of Goal1795](../reviews/goal1798_gemini_review_goal1795_embree_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1799 Partner Any-Hit Public Dispatch](../reports/goal1799_partner_anyhit_public_dispatch_2026-05-12.md)
- [Goal1800 Gemini Review of Goal1799](../reviews/goal1800_gemini_review_goal1799_partner_anyhit_public_dispatch_2026-05-12.md)
- [Goal1801 v2.0 Embree Partner Linux Closure](../reports/goal1801_v2_0_embree_partner_linux_closure_2026-05-12.md)
- [Goal1802 Partner Any-Hit Learner Docs And Example](../reports/goal1802_partner_anyhit_learner_docs_example_2026-05-12.md)
- [Goal1803 Gemini Review of Goal1802](../reviews/goal1803_gemini_review_goal1802_partner_anyhit_learner_docs_2026-05-12.md)

## Claim Boundary

Allowed near-term wording:

```text
RTDL is building a protocol-first Python+partner+RTDL track with PyTorch as the
primary reference partner and CuPy as the lightweight conformance partner.
```

Blocked wording until separately proven:

- "RTDL has general true zero-copy support."
- "RTDL accelerates arbitrary PyTorch/CuPy programs."
- "RTDL optimizes partner code."
- "RTDL native internals are fully app-agnostic."
- "All partners are interchangeable with no performance differences."

True zero-copy is a measured claim boundary. Device-resident handoff,
reduced-copy, fallback copy, and host staging must be reported separately in
benchmark artifacts and release text.
