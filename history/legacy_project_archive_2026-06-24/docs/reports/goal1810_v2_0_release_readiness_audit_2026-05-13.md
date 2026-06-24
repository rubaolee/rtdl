# Goal1810: v2.0 Release Readiness Audit

Status: `superseded-by-stricter-v2.0-birth-gate`

Date: 2026-05-13

## Question

When is v2.0 done?

For the earlier bounded-candidate interpretation used by this audit, v2.0 was
considered done when RTDL had a reviewed, documented, source-tree
Python+partner+RTDL release surface where:

- the partner protocol is explicit and protocol-first;
- PyTorch is the primary/reference partner;
- CuPy is the lightweight conformance partner;
- NumPy covers the CPU/Embree partner path;
- Embree and OptiX both execute the first public partner primitive path;
- RTX-class hardware evidence exists for the OptiX path;
- learner docs and examples explain how to use the path without overclaiming;
- the app-agnostic engine boundary remains intact;
- final release consensus is recorded by distinct AI systems.

## Superseding Decision

Goal1814 supersedes this audit's release-readiness conclusion with a stricter
v2.0 birth gate. Under that gate, the current evidence is accepted only as a
Python+partner preview, not as the v2.0 release. v2.0 is not born until the
following blockers are solved or explicitly removed from the v2.0 public claim:

- true zero-copy;
- direct device-pointer handoff;
- broad RT-core speedup evidence;
- whole-application acceleration evidence;
- arbitrary PyTorch/CuPy acceleration boundaries;
- package-install support.

The evidence chain below remains useful, but the release answer at the end of
this file is historical and no longer authorizes v2.0 publication.

## Prior Verdict

`accept-with-boundary`: v2.0 implementation evidence for the first public
partner any-hit path is present. Goal1813 records final 3-AI release-readiness
consensus under the earlier bounded-candidate interpretation.

In practical terms: the engineering proof and final release-readiness consensus
were present only for the bounded candidate. Goal1814 changes the release
standard, so publishing or tagging v2.0 remains blocked.

## Evidence Chain

### Architecture And Protocol

- Goal1670 records the accepted partner design:

```text
Protocol first. PyTorch reference first. CuPy conformance alongside it.
Engine absolutely app-agnostic throughout.
```

- Goal1777 implements and tests the v2.0 partner protocol baseline:
  - `RtdlTensorDescriptor`;
  - `RtdlOutputSpec`;
  - `PartnerAdapter`;
  - PyTorch reference adapter;
  - CuPy conformance adapter;
  - NumPy CPU adapter;
  - explicit fallback modes;
  - `stream_handle` reserved at zero;
  - zero-copy claims blocked until measured evidence exists.

- Goal1780 records 3-AI consensus for the Goal1777 architecture boundary.

### Real Frameworks

- Goal1781 and Goal1785 prove real NumPy, PyTorch CUDA, and CuPy CUDA
  availability in the v2.0 validation lane.
- Goal1786 provides Gemini review of that real-framework validation.

### Backend Execution

- Goal1787 proves the OptiX partner any-hit host-stage bridge.
- Goals1788, 1789, and 1790 provide Claude, Gemini, and 3-AI consensus for
  the OptiX partner bridge.
- Goal1795 proves the Embree partner any-hit host-stage bridge.
- Goals1796, 1798, and 1797 provide Claude, Gemini, and 3-AI consensus for
  the Embree partner bridge.
- Goal1799 adds the public dispatch:

```text
rt.partner.run_ray_triangle_any_hit_2d(..., backend="embree"|"optix")
rt.run_partner_ray_triangle_any_hit_2d(..., backend="embree"|"optix")
```

- Goal1800 provides Gemini review of the public dispatch.

### Learner Docs And Example

- Goal1802 adds the learner-facing partner any-hit example and tutorial.
- Goal1803 provides Gemini review of those docs.
- Current user-facing docs link the partner tutorial from:
  - `README.md`;
  - `docs/README.md`;
  - `docs/tutorials/README.md`;
  - `examples/README.md`.

### Hardware Evidence

- Goal1804 creates the OptiX pod packet.
- Goal1805 reviews the pod packet.
- Goal1806 records a local Linux mechanics dry run.
- Goal1807 reviews the local dry run.
- Goal1808 records RTX-class pod execution on an NVIDIA RTX 4000 Ada pod.
- Goal1809 reviews the pod evidence.

Goal1808 artifact summary:

| Source mode | Device | Protocol | Backend | Hit count | Transfer mode |
| --- | --- | --- | --- | ---: | --- |
| `numpy` | `cpu:0` | `numpy` | `optix` | 1 | `host_stage` |
| `torch-cuda` | `cuda:0` | `torch` | `optix` | 1 | `host_stage` |
| `cupy-cuda` | `cuda:0` | `cupy` | `optix` | 1 | `host_stage` |

All Goal1808 example artifacts preserve:

```text
true_zero_copy_authorized = false
rt_core_speedup_claim_authorized = false
```

## App-Agnostic Boundary

The v2.0 partner path does not add a new native ABI that links against PyTorch,
CuPy, NumPy, RAPIDS, JAX, or other partner frameworks. Partner-specific
behavior remains in Python adapter/runtime code. The native path remains a
generic RTDL primitive execution path.

This audit does not reopen v3.0 custom shader-extension ideas. v3.0 remains
exploratory and separate from v2.0 release closure.

## Release Claims Allowed

After final release consensus, v2.0 may say:

```text
RTDL v2.0 introduces the first Python+partner+RTDL path: partner-owned NumPy,
PyTorch CUDA, and CuPy CUDA columns can be passed through a public Python API
to the RTDL any-hit primitive path, with Embree as the CPU RT fallback and
OptiX validated on RTX-class hardware through the current host-stage bridge.
```

Allowed narrow claims:

- protocol-first partner track;
- PyTorch reference partner;
- CuPy conformance partner;
- NumPy CPU/Embree partner path;
- public partner any-hit dispatch for Embree and OptiX;
- RTX-class OptiX execution evidence for the first partner any-hit packet;
- host-stage transfer mode.

## Claims Still Blocked

Do not claim:

- true zero-copy;
- direct device-pointer handoff;
- arbitrary PyTorch/CuPy program acceleration;
- RTDL optimizing partner code;
- broad RT-core speedup;
- whole-application acceleration;
- all partners have identical performance;
- packaging/install support beyond source-tree execution.

## Release Closure

Goal1810 originally left three release-closure tasks:

1. External final-release reviews:
   - Claude review of Goal1810 and the v2.0 evidence chain;
   - Gemini review of Goal1810 and the v2.0 evidence chain.
2. 3-AI final consensus file for v2.0 release readiness.
3. If both external reviews accept, refresh the release gate status from
   `needs-final-consensus` to release-ready wording and prepare the tag/release
   packet only after explicit user authorization.

Those review and consensus tasks are now complete:

- Claude review:
  `docs/reviews/goal1811_claude_review_goal1810_v2_0_release_readiness_audit_2026-05-13.md`
- Gemini review:
  `docs/reviews/goal1812_gemini_review_goal1810_v2_0_release_readiness_audit_2026-05-13.md`
- 3-AI consensus:
  `docs/reviews/goal1813_3ai_consensus_v2_0_release_readiness_2026-05-13.md`

The remaining action is release publication/tagging, which requires explicit
user authorization.

## Answer

Under the old bounded-candidate definition, v2.0 was release-ready with the
bounded claims in this audit.

Under the superseding Goal1814 definition, v2.0 is not release-ready until the
stricter blockers are resolved.
