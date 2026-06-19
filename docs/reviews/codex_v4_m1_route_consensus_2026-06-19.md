# Codex V4.0 M1 Route Consensus

Date: 2026-06-19.
Status: accepted for M1 freeze.

## Question

What is the first benchmark-valuable V4.0 Python GPU operator route?

V4.0 is now scoped as Python actors only: CuPy, Numba, and PyTorch call RTDL on
caller-owned CUDA device arrays. Non-Python hosts and public multi-language SDK
packaging are V4.x.

## Reviewer Inputs

### Reviewer A: Fixed-Radius Route

Verdict: accept fixed-radius first, but narrow it to fixed-size device-column
outputs.

Recommended route:

`fixed_radius_count_threshold_2d`

Shape:

- caller-owned CUDA point columns in;
- prepared OptiX fixed-radius scene;
- caller-owned CUDA `query_ids`, `neighbor_counts`, and `threshold_flags` out;
- no variable-length neighbor rows in M1.

Primary rationale:

- the repo already has OptiX-native fixed-radius device-column machinery;
- the route is benchmark-valuable and app-agnostic;
- it avoids variable cardinality and truncation semantics in the first proof;
- existing partner/device-column evidence can be promoted behind V4 wording
  gates.

Risks called out before implementation:

- caller-stream propagation was not complete for the active 2-D path;
- zero-copy wording must remain exact;
- V4 front door and legacy partner adapters are still split;
- full neighbor rows are a later route.

### Reviewer B: Ray/Triangle Route

Verdict: do not make ray/triangle the lowest-risk first route.

Primary rationale:

- ray/triangle is feasible and naturally RT-core-shaped;
- the repo has device ray and same-stream pieces;
- but no single current route yet combines Python device arrays in, RT-core
  execution, device array out, caller stream, and zero-copy evidence;
- any-hit flags are safer than hit streams, but still require composition work.

Recommended placement:

- keep ray/triangle any-hit immediately behind M1 as the next RT-core proof.

## Decision

V4.0 M1 freezes the first product route as:

`fixed_radius_count_threshold_2d`

This route means fixed-radius count/threshold over 2-D point columns, not full
neighbor-row enumeration.

The first public-facing operator target is:

`CuPy/Numba/PyTorch CUDA point columns -> RTDL OptiX fixed-radius count/threshold -> CUDA output columns`

## Enforcement Gates

M1/M2 gate:

- expose a V4-prefixed Python operator surface;
- accept borrowed CUDA columns through `__cuda_array_interface__`/partner
  descriptors;
- validate dtype, rank, stride, shape, and device;
- route nonzero caller streams through the native on-stream symbol, synchronizing
  that stream before return and making no async claim;
- keep true-zero-copy and speed claims blocked at V4 level until the M4 evidence
  packet is complete.

M3/M4 gate:

- native device-buffer route runs end to end;
- output remains fixed-size device columns;
- no host-stage query path is used;
- pointer identity and transfer-counter/equivalent evidence are recorded;
- caller-stream ordering is proven;
- correctness parity is documented;
- unsupported backends, layouts, and host-only fallbacks fail closed.

## Non-Decisions

- Ray/triangle any-hit is not rejected; it is the next route after the
  fixed-radius count/threshold proof.
- Variable-length fixed-radius neighbor rows are not M1; they require capacity
  and truncation semantics.
- Non-Python C/C++/Rust/Julia hosts remain V4.x.
- The existing C ABI AABB2 route remains Phase 2 substrate, not the product
  headline.
