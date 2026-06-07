# Goal3758 RT-DBSCAN Numba Repeat Probe Support

Date: 2026-06-07

## Purpose

RT-DBSCAN already had Numba one-shot and prepared app modes, but the repeat
probe harness used for fair steady-state comparisons was still CuPy-centered.
That made it difficult to answer the user-facing question: when a user wants a
no RawKernel partner path, can Numba be measured on the same reuse contract?

Goal3758 adds two explicit repeat-probe modes:

- `partner_numba_prepared_grid_components_3d`
- `optix_rt_core_flags_numba_prepared_grid_components_3d`

## Design

The new modes prepare Numba point columns and grid metadata once, then repeat
only the component-label continuation. The OptiX+Numba mode also prepares the
OptiX fixed-radius threshold scene once and reuses caller-owned Numba-compatible
device output columns for threshold flags and neighbor counts.

The native engine still sees only generic fixed-radius count-threshold
contracts. DBSCAN semantics remain in the benchmark app and partner
continuation.

## Boundary

This goal adds harness support and does not authorize release action, public
speedup wording, broad RT-core wording, paper reproduction wording, automatic
partner selection, true zero-copy wording, or app-specific native engine logic.

The Numba modes are no RawKernel user-reference paths. The A5000 pod evidence
below supports only the prepared-repeat RT-DBSCAN component-labeling contract,
not a whole DBSCAN paper-reproduction claim.

## A5000 Evidence

The repeat probe was run on the A5000 pod with `clustered3d`, five repeats, and
four same-signature modes:

- `partner_cupy_prepared_grid_components_3d`
- `partner_numba_prepared_grid_components_3d`
- `optix_rt_core_flags_cupy_prepared_grid_components_3d`
- `optix_rt_core_flags_numba_prepared_grid_components_3d`

All rows reported matching output signatures.

| Points | Prepared CuPy grid sec | Prepared Numba grid sec | OptiX+CuPy sec | OptiX+Numba sec | Numba vs CuPy | OptiX+Numba vs CuPy | OptiX+Numba vs Numba |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4,096 | 0.015946 | 0.014097 | 0.017580 | 0.016679 | 1.131x | 0.956x | 0.845x |
| 65,536 | 0.479967 | 0.416234 | 0.394027 | 0.351184 | 1.153x | 1.367x | 1.185x |
| 131,072 | 1.517740 | 1.372595 | 1.012686 | 0.868125 | 1.106x | 1.748x | 1.581x |

Interpretation:

- Numba prepared-grid continuation is a measured no-RawKernel reference, not
  merely a compatibility path.
- The mixed OptiX+Numba route is not worthwhile at 4k points, where launch and
  occupancy costs dominate.
- At 65k and 131k points, the OptiX RT-core threshold flags plus Numba prepared
  continuation become the stronger path.

Artifact:

- `docs/reports/goal3758_rt_dbscan_numba_repeat_probe_a5000/summary.json`
