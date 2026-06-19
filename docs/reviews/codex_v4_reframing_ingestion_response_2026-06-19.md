# Codex V4 Reframing Ingestion Response

Date: 2026-06-19
Input: `docs/reviews/v4_reframing_note_rt_core_operator_for_python_gpu_ecosystem_2026-06-19.md`

## Bottom Line

Accepted. The reframing note is a P0 design input for V4.0.

The V4.0 headline is no longer "make RTDL embeddable through a public C ABI."
The headline is:

> RTDL is the missing RT-core lane for the Python GPU ecosystem: CuPy, Numba,
> PyTorch, Triton, and JAX-style programs keep their own device arrays and
> caller streams, then call RTDL as the RT-core spatial/traversal operator.

The C ABI remains important, but it is substrate. It is the basement under the
Python product, not the user-facing product.

## Accepted Scope Decision

V4.0 is Python actors only.

This closes the scope question that previously sized the C ABI work:

- non-Python hosts are V4.x;
- full public multi-language C ABI packaging is V4.x;
- generated C/C++/Rust SDK bindings are V4.x;
- pkg-config/CMake/installable SDK promises are V4.x;
- V4.0 public value is the Python device-array RT-core operator route.

The active `src/v4/` C ABI work remains useful and should continue, but it is
now Phase 2 substrate work. It must not become the V4.0 headline.

## Actions Applied

1. Reframed `docs/engineering/rtdl_v4_0_design_review_packet_2026-06-19.md`
   around the missing RT-core lane pitch.
2. Reordered V4.0 milestones so Phase 1 is the Python device-array RT-core
   operator route with zero-copy evidence.
3. Moved non-Python hosts, public SDK packaging, and generated bindings to
   V4.x under the current scope decision.
4. Reclassified `docs/engineering/rtdl_v4_0_active_abi_slice_2026-06-19.md`
   and `src/v4/README.md` as Phase 2 substrate documentation.
5. Added a regression gate so the design packet cannot quietly slide back to
   C-ABI-first framing.

## Next Gate

M1 should freeze only after selecting the first benchmark-valuable Python
device-array route. The current candidates remain fixed-radius neighbors and
ray/triangle any-hit. Host-only AABB2 is still a useful control-plane proof,
but it is not enough to prove V4.0 product value.
