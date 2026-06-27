# Goal1479 GPU Memory Architecture: Python+RTDL vs Python+Partner+RTDL

## Verdict

RTDL should treat Python+RTDL and Python+partner+RTDL as two different GPU
memory architectures.

Python+RTDL makes GPU RT available to normal Python users whose data usually
starts in CPU/main memory. Python+partner+RTDL attaches RTDL to applications
that already manage GPU memory through a partner runtime such as PyTorch, CuPy,
RAPIDS, or custom CUDA.

## Python+RTDL

In Python+RTDL, the default user is not writing a GPU program. The user's data
usually begins as Python objects, NumPy arrays, files, database results, or
other CPU-side structures.

For NVIDIA RT execution, moving that data to GPU memory is unavoidable unless
RTDL itself becomes the memory owner or memory manager. Practical approaches
include:

- RTDL-owned prepared host buffers.
- RTDL-owned pinned or staging buffers.
- RTDL-owned device-resident buffers.
- RTDL-managed unified-memory buffers.
- APIs that load data once into RTDL-managed memory and then run many RTDL
  kernels against the resident representation.

This track can honestly claim reduced-copy, transfer reuse, prepared-buffer
reuse, resident-buffer reuse, or managed-memory behavior when measured. It
cannot honestly claim arbitrary Python-data zero-copy. True zero-copy wording
requires separately measured GPU-resident or externally shareable device-memory
evidence.

## Python+Partner+RTDL

In Python+partner+RTDL, the user is already writing or using explicit GPU
programs. The partner runtime owns memory, lifetime, streams, synchronization,
and often tensor layout.

RTDL should not replace that memory manager. It should interoperate with it.
The likely boundary is descriptor-based attachment to existing GPU memory,
including:

- Device pointer or handle.
- DLPack or CUDA array interface metadata where appropriate.
- Shape, dtype, layout, stride, and byte-count metadata.
- Owner and lifetime rules.
- CUDA stream or synchronization metadata.
- Explicit transfer-count and residency evidence.

This is the architecture where external true zero-copy becomes plausible,
because data may already live on GPU before RTDL sees it. Even here, true
zero-copy is not automatic; it must be measured and reviewed for the exact
subpath.

## Architectural Rule

Python+RTDL should optimize data movement by managing RTDL buffers and reusing
resident representations.

Python+partner+RTDL should optimize data movement by attaching to partner-owned
GPU buffers without taking over memory management.

## Roadmap Consequence

- v1.5.x to v1.6: finish Python+RTDL managed-buffer and reduced-copy/residency
  semantics.
- v1.7 to v2.0: build Python+partner+RTDL external GPU-memory interop, starting
  from a DLPack-compatible tensor handoff unless later consensus changes the
  first partner baseline.

## Claim Boundary

This document is an architecture boundary, not a performance claim. It does not
authorize true zero-copy wording, public speedup wording, whole-app claims,
stable primitive promotion, partner tensor handoff, or release action.
