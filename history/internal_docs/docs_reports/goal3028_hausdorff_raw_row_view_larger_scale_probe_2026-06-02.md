# Goal3028: Hausdorff Raw Row-View Larger-Scale Probe

Date: 2026-06-02

## Purpose

Goal3028 extends the Goal3026 same-contract measurement to larger dense 2D
Hausdorff point sets on the L4 pod. The question is whether the generic
raw-row-view RTDL/OptiX method begins to close the dense CuPy grouped-grid
reference gap as the input grows.

The methods are unchanged:

- Old RT path: `rtdl_rt_grouped_adaptive_nearest_witness`
- New RT path: `rtdl_rt_grouped_adaptive_raw_nearest_witness`
- Dense CUDA-core partner reference: `cupy_grouped_grid_rawkernel`

No native Hausdorff-specific ABI or kernel was added.

## Pod Environment

- GPU: `NVIDIA L4, 565.57.01`
- CUDA toolchain used for OptiX PTX: `/usr/local/cuda-12.6`
- Source commit: `ee44ee06d296c1f206f1e3b5d3047bec8fb0e522`
- Dirty source list: empty
- Warmup: 1
- Repeats per row: 3

Artifacts:

- `docs/reports/goal3028_hausdorff_raw_row_view_larger_scale_probe_2026-06-02.json`
- `docs/reports/goal3028_hausdorff_raw_row_view_32768_probe_2026-06-02.json`
- `docs/reports/goal3028_hausdorff_raw_row_view_65536_probe_2026-06-02.json`

## Results

| Points | Old adaptive RT median sec | Raw row-view RT median sec | CuPy grouped-grid median sec | Raw / old | Raw / CuPy |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 8192 | 0.14274848625063896 | 0.11719213053584099 | 0.00689195841550827 | 0.8209693399485448x | 17.00418422028425x |
| 16384 | 0.2977694161236286 | 0.23207217827439308 | 0.024793460965156555 | 0.7793687521556639x | 9.36021713953269x |
| 32768 | 0.6276213750243187 | 0.5054505690932274 | 0.07275710254907608 | 0.8053479208379095x | 6.947095794761343x |
| 65536 | 1.3800964392721653 | 1.113086674362421 | 0.23465874046087265 | 0.8065281934199902x | 4.743426599986384x |

## Interpretation

The raw row-view method remains a stable current-basis RTDL/OptiX improvement:
across 8192 through 65536 points, it is about 18-22% faster than the old
adaptive RT row path.

The dense CuPy grouped-grid reference still wins on all measured rows. The gap
narrows with scale, from about `17.00418422028425x` at 8192 points to about
`4.743426599986384x` at 65536 points, but no crossover appears in this probe.

This reinforces the v2.6 design direction:

- Keep `rtdl_rt_grouped_adaptive_raw_nearest_witness` as the current preferred
  exact RTDL/OptiX Hausdorff path.
- Keep `cupy_grouped_grid_rawkernel` as the dense exact performance reference
  for this point-set shape.
- Pursue a generic device-resident active-set / candidate-frontier /
  nearest-witness continuation before expecting the RT path to beat optimized
  dense CUDA-core partner code.

## Boundaries

This report does not authorize:

- v2.6 release
- public speedup wording
- broad RT-core speedup wording
- whole-app speedup wording
- true zero-copy wording
- package-install claims
- app-specific native-engine behavior

The evidence is internal benchmark-app tuning evidence on one L4 pod. It should
not be presented as an RTDL-vs-X-HD or RTDL-vs-CUDA victory claim.
