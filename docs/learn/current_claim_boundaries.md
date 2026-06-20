# Current Claim Boundaries

Status: current learner-facing boundary page.

This page is the short source of truth for how to read RTDL capability and
performance claims in the current public docs.

## Product Surface

The current learner-facing milestone is the V4.0.0 source-tree Python GPU
operator surface. Its first public route is
`fixed_radius_count_threshold_2d`: CuPy, Numba, or PyTorch owns CUDA arrays;
RTDL borrows the named device columns; the OptiX-backed route writes
caller-owned `query_ids`, `neighbor_counts`, and `threshold_flags`.

The V3.0.2 Python+partner+RTDL benchmark-app surface remains documented and
usable, but it is now the previous release line.

Use RTDL from the repository source tree:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --include-v4-active --json
make build-optix
PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_cupy_hello.py
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
- stable SDK or generated binding package wording;
- automatic partner selection;
- arbitrary CuPy, Numba, PyTorch, or DLPack acceleration;
- broad RT-core acceleration;
- whole-application speedup;
- RTDL-beats-RayJoin wording;
- paper reproduction;
- public true-zero-copy, general zero-copy, or device-residency;
- async or nonblocking completion;
- device-buffer C ABI query execution;
- external CUDA stream ordering;
- AMD/HIPRT or Intel-GPU performance claims.

Selecting `--backend optix` means the OptiX backend was selected. It is not by
itself a public RT-core speedup claim.

The V4.0.0 evidence supports one route-specific operator claim only. It does
not turn every CUDA array, PyTorch tensor, Numba program, OptiX call, or RTDL
benchmark app into a public speedup claim. Mixed V3 rows remain explicit:
Spatial RayJoin, RT-DBSCAN, Barnes-Hut, RTNN, and Triangle Counting all require
route, partner, output-contract, and timing-basis wording before any
performance sentence is public-safe.

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
- [RTDL V4.0.0 Release Package](../release_reports/v4_0_0/README.md)
- [RTDL v3.0.2 Release Package](../release_reports/v3_0_2/README.md)
