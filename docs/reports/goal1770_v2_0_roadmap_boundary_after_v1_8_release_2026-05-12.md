# Goal1770: v2.0 Roadmap Boundary After v1.8 Release

Status: `v2_0_partner_track_active_v3_0_extensions_parked`

Date: 2026-05-12

## Context

RTDL v1.8 is published as the first source-tree Python+RTDL language release.
The next active roadmap target is v2.0: Python+partner+RTDL.

The long-horizon v3.0 custom-engine-extension concept remains valuable, but it
must not absorb v2.0 scope. The v3.0 idea is about device/shader extensibility:
user-provided OptiX PTX, Vulkan SPIR-V, Apple Metal artifacts, extension payload
schemas, shader ABI versioning, and per-backend conformance. That is a separate
future lane.

## Roadmap Separation

| Milestone | Active meaning | Boundary |
| --- | --- | --- |
| v1.8 | Python+RTDL source-tree language release | Published; no package-install, partner, or universal speedup claim |
| v2.0 | Python+partner+RTDL | Host/tensor interop, PyTorch reference first, CuPy conformance alongside it |
| v3.0 | Custom engine extensions | Exploratory only; device/shader injection and extension ABI work |

## v2.0 Principle

v2.0 is not custom shader injection. It is the host/tensor partner layer around
the app-agnostic RTDL engine.

Accepted design:

```text
Protocol first. PyTorch reference first. CuPy conformance alongside it.
Engine absolutely app-agnostic throughout.
```

Partner frameworks own tensor memory, allocation behavior, stream semantics,
and framework-side compute around RTDL. RTDL owns generic descriptors, RT-shaped
kernel dispatch, synchronization metadata, fallback policy, and claim-boundary
artifacts.

The native engine must not link directly against PyTorch, CuPy, RAPIDS, JAX, or
another framework. Partner mechanics stay in Python adapter code and generic C
descriptor bridges.

## v3.0 Parking Rule

The v3.0 concept is strategically sound but still exploratory. Before it can
move out of the parking lane, it needs at least:

- a device-side `RtdlExtensionPayload` schema distinct from host-side
  partner descriptors and `RtdlPayloadField`;
- per-backend shader entry signatures and payload/stack budget documentation;
- shader artifact loading with version pinning and hash-pinned cache;
- engine extension ABI versioning policy;
- safety and isolation rules for faulty user shaders;
- per-backend conformance tests;
- distinct-AI review, at minimum Claude plus Gemini, not Codex plus Codex.

The Python-to-shader JIT idea should be split into a later concept note. It is
not part of the v2.0 partner track.

## How To Reach v2.0

The v2.0 path should move in narrow, auditable slices:

1. Freeze the partner vocabulary and claim boundary.
   - First implementation baseline: [Goal1777 v2.0 Partner Protocol
     Baseline](goal1777_v2_0_partner_protocol_baseline_2026-05-12.md).
2. Extend `RtdlTensorDescriptor` and `RtdlOutputSpec` only where v2.0 evidence
   requires it, not for speculative v3.0 shader injection.
3. Make PyTorch the reference adapter with real framework tests:
   grad-enabled rejection or explicit detach, contiguous/non-contiguous policy,
   dtype/device validation, allocator-owned output allocation, and stream-order
   behavior.
4. Make CuPy the conformance adapter with tests proving the protocol is not
   PyTorch-shaped: CuPy-owned input, CuPy-readable output, DLPack path where
   supported, and CUDA-array-interface fallback only when explicitly named.
5. Add NumPy/Embree host descriptor acceptance for CPU/Embree partner parity.
6. Wire one narrow OptiX primitive path first, preferably `ANY_HIT` or
   `COUNT_HITS`, through partner descriptors.
7. Produce phase-timing artifacts that separate device-resident handoff,
   reduced-copy handoff, fallback copy, and host staging.
8. Run hardware/pod validation for PyTorch and CuPy on the same primitive path.
9. Add distinct-AI review and a final v2.0 consensus report.

## Non-Claims

Until v2.0 evidence exists, do not claim:

- general true zero-copy support;
- arbitrary PyTorch/CuPy program acceleration;
- partner framework code optimization;
- interchangeable partners with no performance differences;
- v3.0 custom shader extension support;
- Python-to-PTX/SPIR-V/Metal JIT support.

## Verdict

`accept`: v2.0 should now become the active roadmap lane. Keep v3.0 as a
documented exploratory future, but protect v2.0 from extension/JIT scope creep.
