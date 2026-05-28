# Goal2660: v2.4 Phase Timing Metadata

Status: implementation slice, local-test backed.

Date: 2026-05-27

## Purpose

The v2.4 roadmap requires user-friendly partner paths without hiding overhead.
This slice adds a small machine-readable phase-timing helper and attaches it to
the prepared benchmark paths already carrying v2.4 protocol descriptors.

## Implemented Surface

New shared helper:

- `rtdsl.v2_4_phase_timing_metadata(phases_sec, ...)`

The helper records:

- `phases_sec`;
- whether the row is a promoted performance path;
- whether it preserves the accepted benchmark phase contract;
- the `rtdl.partner.v2.4` contract version;
- the result of `validate_phase_timing_record()`.

Benchmark integrations:

- RayDB paper-shaped native result path records query preparation, scene build,
  RT traversal, and materialization phases.
- Contact-manifold bounded witness paths record materialization for collect-k
  and split AABB broadphase, Python exact refinement, and bounded row
  materialization for the AABB path.
- Triangle-counting RT-2A1 and RT-1A2 paths record geometry/query preparation,
  scene build, RT traversal, and materialization phases.

## Boundary

This is metadata only. It does not replace benchmark timing evidence, add a new
native path, or authorize public speedup wording. Its role is to prevent future
Triton/Numba convenience paths from collapsing RT traversal and partner/Python
continuation into one opaque number.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2659_v2_4_benchmark_protocol_integration_test \
  tests.goal2658_v2_4_partner_protocol_test
```

Expected result:

```text
OK
```

Optional local CUDA/NumPy/CuPy tests may still skip on this Mac.
