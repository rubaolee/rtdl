# Goal2658: v2.4 Partner Protocol Foundation

Status: implementation slice, local-test backed.

Date: 2026-05-27

## Purpose

This implements the first v2.4 roadmap slice after the Goal2657 consensus:
an RTDL-specific typed buffer and prepared-session protocol foundation.

The goal is not to add Triton or Numba yet. The goal is to make sure the next
partner work has a stable, app-agnostic, performance-gated handoff contract
before any new partner is plugged in.

## Implemented Surface

New module:

- `src/rtdsl/partner_protocol.py`

New exported contracts:

- `RtdlBufferDescriptor`
- `RtdlPreparedSessionDescriptor`
- `RtdlBenchmarkBasisRow`
- `RtdlV24PartnerProtocolContract`
- `v2_4_partner_protocol_contract()`
- `validate_v2_4_partner_protocol_contract()`
- `buffer_descriptor_from_tensor_descriptor()`
- `low_margin_benchmark_rows()`
- `validate_phase_timing_record()`

New test:

- `tests/goal2658_v2_4_partner_protocol_test.py`

First benchmark metadata integration:

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
  now emits a v2.4 prepared-session descriptor for the paper-shaped generic
  ray/triangle grouped-reduction path.

## Boundary Decisions

The new descriptor is intentionally not a general-purpose memory manager. It
only records typed buffer metadata needed for RTDL primitive handoff:

- dtype;
- shape;
- strides;
- device type and id;
- observed data pointer when available;
- access mode;
- source protocol;
- lifetime;
- capacity;
- stream field, currently reserved to zero.

The prepared-session descriptor is also protocol-only. It records reusable
scene/query/output-buffer intent and phase-contract metadata, but it does not
authorize a new native execution path by itself.

RayDB integration uses the same boundary: the app can describe the generic
prepared session as `ray_triangle_grouped_i64_reduction_3d`, but RayDB predicate
encoding and result interpretation stay in Python app code.

## Benchmark Basis

The module records the current v2.3-family benchmark basis from Goal2657:

- 10 promoted benchmark apps;
- 11 primary comparison rows;
- NVIDIA RTX A5000 evidence qualifier;
- low-margin protocol-overhead audit targets: Hausdorff, Barnes-Hut, Robot
  collision.

This is not public performance wording. It is regression-gate metadata for
future v2.4/v2.5 work.

## Engine Boundary

The protocol rejects app-specific native vocabulary in prepared-session
primitive names and native symbols. Examples of forbidden native tokens include:

- `raydb`
- `dbscan`
- `barnes`
- `contact`
- `collision`
- `robot`
- `librts`
- `rtnn`
- `triangle_counting`

Generic names such as `grouped_ray_triangle_reduction` remain allowed.

## Phase-Timing Boundary

The new phase validator requires machine-readable phase timing and rejects
collapsed RT/partner timing for promoted performance paths. In particular:

- RTDL/OptiX traversal must be timed separately from partner continuation;
- promoted paths must compare the same phase contract as the accepted benchmark
  basis row.

This follows the Goal2657 consensus that user-friendlier partner paths must not
hide slow Python or partner continuation behind a fast RT traversal.

## Local Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal2658_v2_4_partner_protocol_test
```

Expected result:

```text
Ran 7 tests
OK
```

## Next Work

The next v2.4 slice should connect this protocol to one real prepared path,
preferably RayDB plus one row-heavy benchmark and one bounded-collection
benchmark, while keeping the accepted v2.3 RT-vs-Embree rows as regression
gates.
