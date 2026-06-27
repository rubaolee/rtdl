# Goal2636 Strengthened Benchmark Rows

This artifact strengthens the weaker Goal2634 rows with scale ladders or larger fixtures.
It is internal engineering evidence only, not public speedup wording.

- Tier: `standard`
- Case repeat: `3`
- Generated: `2026-06-06T12:02:51+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| spatial_rayjoin | rayjoin_lsi_authored_tiled_x512 | 0.0129416 | 0.000102108 | 127x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_overlay_seed_authored_tiled_x512 | 0.349695 | 0.000357255 | 979x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_pip_authored_tiled_x512 | 0.0108311 | 0.00211587 | 5.12x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| spatial_rayjoin | rayjoin_embree_pip_tiled_x512 | embree | ok | 0.0108311 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_pip_tiled_x512 | optix | ok | 0.00211587 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_lsi_tiled_x512 | embree | ok | 0.0129416 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_lsi_tiled_x512 | optix | ok | 0.000102108 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_overlay_seed_tiled_x512 | embree | ok | 0.349695 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_overlay_seed_tiled_x512 | optix | ok | 0.000357255 | `phases_sec.prepared_query_sec` |

## Boundary

- Hausdorff exact-witness rows are OptiX-only and are not ratioed.
- Spatial RayJoin rows use derived tiled fixtures, but still do not materialize full polygon overlay.
- RTNN rows are distribution-sensitive; clustered rows are the density-risk signal.
- Barnes-Hut rows are node-coverage only, not force aggregation.
- Triangle-counting rows are synthetic RT-2A1 backend-query ladders; paper datasets still require segmented/streamed lowering.
