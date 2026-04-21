# RTDL v0.9.6 Release Statement

Status: released as `v0.9.6`.

RTDL `v0.9.6` is the prepared/prepacked repeated visibility/count optimization
release.

The correct release statement is:

> RTDL `v0.9.6` packages prepared/prepacked repeated 2D
> visibility/count improvements across Apple RT, OptiX, HIPRT, and Vulkan.
> It keeps the `v0.9.5` any-hit, visibility-row, and `reduce_rows` surface,
> adds native/native-assisted any-hit coverage for Vulkan and
> Apple RT after backend rebuild, and adds backend-specific prepared or
> prepacked paths for repeated visibility/count workloads.

## What This Release May Claim

- Vulkan supports native early-exit any-hit after rebuilding the
  Vulkan backend library.
- Apple RT supports 3D MPS RT any-hit and 2D MPS-prism
  native-assisted any-hit after rebuilding the Apple RT backend library.
- Apple RT has a fast scalar blocked-ray count path for prepared 2D scenes and
  prepacked rays on the tested Apple M4.
- OptiX has a strong prepared/prepacked scalar count path for repeated 2D
  any-hit visibility queries on the tested Linux NVIDIA host.
- HIPRT has prepared 2D any-hit reuse on the HIPRT/Orochi CUDA path.
- Vulkan has prepared 2D any-hit plus packed-ray support, with measured wins
  only when prepacked rays avoid repeated Python packing.
- Public docs, history, local tests, Linux backend tests, and AI consensus have
  been refreshed through Goal684.

## What This Release Must Not Claim

- broad speedup across all RTDL workloads;
- DB or graph speedup from the visibility/count optimization evidence;
- one-shot-call speedup from prepared/prepacked evidence;
- full emitted-row Apple RT speedup from the scalar count path;
- RT-core speedup from the GTX 1070 Linux evidence;
- AMD GPU validation for HIPRT;
- HIPRT CPU fallback;
- Apple MPS ray-tracing traversal for DB or graph workloads;
- release scope beyond the audited `v0.9.6` support matrix.

## Evidence

- `/Users/rl2025/rtdl_python_only/docs/reports/goal676_677_consensus_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal678_679_consensus_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal680_consensus_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal681_consensus_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal683_consensus_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal684_consensus_2026-04-21.md`
