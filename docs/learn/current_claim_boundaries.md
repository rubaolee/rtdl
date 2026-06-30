# Current Claim Boundaries

Status: current learner-facing boundary page.

This page is the short source of truth for how to read RTDL capability and
performance claims in the current public docs.

## Product Surface

The current learner-facing milestone is the v2.14 source-tree
Python+partner+RTDL surface. It keeps the v2.11/v2.12 Python+partner+RTDL
programming model, preserves the Embree CPU plus partner reference lane, and
publishes the refreshed row-scoped RT-core versus Embree CPU comparison
evidence plus the app-author strategy for primitive-first, explicit-partner
implementation.

Use RTDL from the repository source tree:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

Optional editable checkout is a local developer convenience, not a package
distribution promise.

## What RTDL Claims

RTDL claims only the primitive contract that it ships, tests, measures, and
reviews.

Allowed claims must name the exact:

- primitive or benchmark row;
- backend;
- partner, when one is used;
- hardware;
- command shape;
- output contract;
- reviewed artifact path.

If those details are missing, use compatibility, preview, or internal-evidence
wording instead of performance wording.

## What RTDL Does Not Claim

The current public docs do not authorize these claims; in short, RTDL does not authorize:

- package-install or PyPI support wording;
- automatic partner selection;
- arbitrary CuPy or Numba acceleration;
- broad RT-core acceleration;
- whole-application speedup;
- RTDL-beats-RayJoin wording;
- paper reproduction;
- general zero-copy or device-residency;
- AMD/HIPRT or Intel-GPU performance claims.

Selecting `--backend optix` means the OptiX backend was selected. It is not by
itself a public RT-core speedup claim.

The v2.14 evidence supports path-specific wording only. In particular, the
refreshed packet keeps every speedup tied to a row, contract, direction, and
caveat. Mixed rows remain explicit: Spatial RayJoin PIP is near parity and
slightly Embree-faster in the refreshed human-scale public CDB slice, stricter prepared-executor evidence
separately records an OptiX-over-Embree exact PIP engineering win that still does
not beat RayJoin RT, RayJoin overlay reports the available 2/8 exact CDB subset,
and RTNN remains blocked as an RT-core neighbor-search claim.

## Partner Rule

Use fused RTDL primitives first when they exactly express the work.

Choose a partner explicitly when custom continuation logic is needed:

- CuPy is the mature CUDA-array and library-continuation partner.
- Numba is the Python-source custom CUDA-style continuation lane for selected
  measured contracts.

User-owned partner code is allowed, including CuPy RawKernel and Numba CUDA
kernels. That code belongs to the user's application unless RTDL ships,
measures, and reviews that exact continuation contract.

## Related Reference Pages

- [Capability Boundaries](../capability_boundaries.md)
- [Partner Acceleration Boundaries](../partner_acceleration_boundaries.md)
- [Performance Model](../performance_model.md)
- [Benchmark Evidence Index](benchmark_evidence_index.md)
- [RT-Core Evidence Matrix](rt_core_evidence_matrix.md)
- [Choosing A Partner For Custom Logic](partner_choice_for_custom_logic.md)
