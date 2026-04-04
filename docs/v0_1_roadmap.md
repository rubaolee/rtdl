# RTDL v0.1 Roadmap

## v0.1 Goal

RTDL v0.1 should be able to re-implement all RayJoin workloads through the new Python-hosted DSL and generated RayJoin-style backend path, without yet reproducing RayJoin's most advanced precision machinery such as 64-bit precision extension.

This means v0.1 is:

- an initial version of RayJoin through RTDL,
- functionally capable across the RayJoin workload surface,
- backend-driven through the current controlled native/oracle and GPU runtime paths, and
- explicit about simplified precision limitations.

## What v0.1 Should Deliver

At the end of v0.1, the system should provide:

- a Python-hosted DSL that can express every workload RayJoin supports,
- a compiler IR that represents those workloads cleanly,
- a RayJoin-oriented lowering path for each workload,
- trusted runnable execution paths across the accepted current backends,
- a cross-vendor Vulkan KHR backend kept honest about its current provisional boundary, and
- a runnable execution path for each accepted workload slice, and
- validation against reference outputs on representative datasets.

## v0.1 Precision Policy

The project makes this limitation explicit:

- v0.1 does not attempt to reproduce RayJoin's precision extension to 64 bits,
- GPU backends (OptiX, Vulkan) use float32-based precision,
- the CPU backend (Embree) provides a higher-precision reference,
- v0.1 documents where the simplified model is acceptable, and
- v0.1 identifies numerical edge cases deferred to later releases.

## Scope Breakdown

### In Scope

- All six RayJoin workloads (LSI, PIP, etc.)
- Multi-backend target support (Embree, OptiX, Vulkan)
- Python DSL for kernel authoring
- Bounded real-data validation (County/Zipcode)

### Out of Scope

- Paper-scale GPU reproduction (deferred to v0.2)
- High-precision GPU extension (deferred to v0.2)
- Multi-GPU/Distributed execution
