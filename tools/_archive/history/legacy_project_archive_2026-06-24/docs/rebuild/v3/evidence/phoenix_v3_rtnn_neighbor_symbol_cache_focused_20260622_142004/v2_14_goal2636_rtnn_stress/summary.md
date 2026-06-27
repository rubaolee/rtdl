# Goal2636 Strengthened Benchmark Rows

This artifact strengthens the weaker Goal2634 rows with scale ladders or larger fixtures.
It is internal engineering evidence only, not public speedup wording.

- Tier: `stress`
- Case repeat: `5`
- Generated: `2026-06-22T14:26:59+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| rtnn | rtnn_clustered_262144_ranked_summary | 11.9983 | 1.38005 | 8.69x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_clustered_65536_ranked_summary | 0.640965 | 0.171046 | 3.75x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_shell_262144_ranked_summary | 1.62169 | 0.548288 | 2.96x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_shell_65536_ranked_summary | 0.12075 | 0.108046 | 1.12x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_uniform_262144_ranked_summary | 0.462165 | 0.421333 | 1.1x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_uniform_65536_ranked_summary | 0.114483 | 0.105459 | 1.09x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| rtnn | rtnn_embree_uniform_65536_ranked_summary | embree | ok | 0.114483 | `elapsed_sec` |
| rtnn | rtnn_optix_uniform_65536_ranked_summary | optix | ok | 0.105459 | `elapsed_sec` |
| rtnn | rtnn_embree_clustered_65536_ranked_summary | embree | ok | 0.640965 | `elapsed_sec` |
| rtnn | rtnn_optix_clustered_65536_ranked_summary | optix | ok | 0.171046 | `elapsed_sec` |
| rtnn | rtnn_embree_shell_65536_ranked_summary | embree | ok | 0.12075 | `elapsed_sec` |
| rtnn | rtnn_optix_shell_65536_ranked_summary | optix | ok | 0.108046 | `elapsed_sec` |
| rtnn | rtnn_embree_uniform_262144_ranked_summary | embree | ok | 0.462165 | `elapsed_sec` |
| rtnn | rtnn_optix_uniform_262144_ranked_summary | optix | ok | 0.421333 | `elapsed_sec` |
| rtnn | rtnn_embree_clustered_262144_ranked_summary | embree | ok | 11.9983 | `elapsed_sec` |
| rtnn | rtnn_optix_clustered_262144_ranked_summary | optix | ok | 1.38005 | `elapsed_sec` |
| rtnn | rtnn_embree_shell_262144_ranked_summary | embree | ok | 1.62169 | `elapsed_sec` |
| rtnn | rtnn_optix_shell_262144_ranked_summary | optix | ok | 0.548288 | `elapsed_sec` |

## Boundary

- Hausdorff exact-witness rows are OptiX-only and are not ratioed.
- Spatial RayJoin rows use derived tiled fixtures, but still do not materialize full polygon overlay.
- RTNN rows are distribution-sensitive; clustered rows are the density-risk signal.
- Barnes-Hut rows are node-coverage only, not force aggregation.
- Triangle-counting rows are synthetic RT-2A1 backend-query ladders; paper datasets still require segmented/streamed lowering.
