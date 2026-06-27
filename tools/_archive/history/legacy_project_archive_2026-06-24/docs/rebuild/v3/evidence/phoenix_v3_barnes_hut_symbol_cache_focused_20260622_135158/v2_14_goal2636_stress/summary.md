# Goal2636 Strengthened Benchmark Rows

This artifact strengthens the weaker Goal2634 rows with scale ladders or larger fixtures.
It is internal engineering evidence only, not public speedup wording.

- Tier: `stress`
- Case repeat: `3`
- Generated: `2026-06-22T13:52:31+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | barnes_hut_node_coverage_bodies_131072 | 0.553822 | 0.29519 | 1.88x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| barnes_hut | barnes_hut_node_coverage_bodies_32768 | 0.12733 | 0.0437095 | 2.91x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_32768 | embree | ok | 0.12733 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_32768 | optix | ok | 0.0437095 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_131072 | embree | ok | 0.553822 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_131072 | optix | ok | 0.29519 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |

## Boundary

- Hausdorff exact-witness rows are OptiX-only and are not ratioed.
- Spatial RayJoin rows use derived tiled fixtures, but still do not materialize full polygon overlay.
- RTNN rows are distribution-sensitive; clustered rows are the density-risk signal.
- Barnes-Hut rows are node-coverage only, not force aggregation.
- Triangle-counting rows are synthetic RT-2A1 backend-query ladders; paper datasets still require segmented/streamed lowering.
