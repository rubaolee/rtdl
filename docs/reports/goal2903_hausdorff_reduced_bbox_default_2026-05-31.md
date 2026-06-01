# Goal2903: Hausdorff Exact RT Default Uses Reduced BBox Path

Date: 2026-05-31
Status: implemented pending clean current-commit pod artifact

## Purpose

Goal2902 identified `hausdorff_xhd` as the top current v2.5 performance target. The old canonical entrypoint default used adaptive grouped nearest-witness traversal. That was correct and RT-core accelerated, but it paid repeated OptiX launches to grow the radius until every source point had a witness.

Goal2903 changes the canonical exact Hausdorff RTDL entrypoint to the generic reduced point-group nearest-witness path:

- default method: `rtdl_rt_grouped_reduced_nearest_witness`
- default radius strategy: bbox upper bound, with threshold seeding disabled
- default grouped target size: `2048`
- native engine change: none
- app-specific native logic: none

The design lesson is important: for dense exact Hausdorff, extra RT threshold-search launches are more expensive than using the generic device-side max-distance reduction over a conservative radius.

## Preliminary Pod Probe

The RTX A5000 probe before this report showed:

| Points per side | Best reduced bbox group | CuPy grid median sec | RTDL reduced bbox median sec | RTDL / CuPy |
| ---: | ---: | ---: | ---: | ---: |
| 4096 | 4096 | `0.004501` | `0.004350` | `0.966x` |
| 8192 | 2048 | `0.008021` | `0.007629` | `0.951x` |
| 16384 | 2048 | `0.014204` | `0.014436` | `1.016x` |

The previous canonical adaptive path in Goal2902 was `19.119x` slower than CuPy on the 4096-point packet. The reduced bbox path turns that into near parity or a small win on the measured scales while preserving exact distance.

## Boundary

This is a canonical-path correction for the benchmark app, not a public speedup claim and not a release packet.

It does not claim RTDL beats X-HD, does not claim RTDL beats every optimized CuPy/CUDA implementation, and does not add Hausdorff-specific native engine behavior. The primitive remains generic point-group nearest-witness plus device-side max-distance reduction.

## Next Validation

Run a clean current-commit pod artifact after this code lands, then refresh the v2.5 performance triage if the result is stable.
