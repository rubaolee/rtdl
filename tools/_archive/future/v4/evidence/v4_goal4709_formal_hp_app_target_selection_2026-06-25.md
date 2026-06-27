# V4 Goal4709 Formal High-Performance App Target Selection

- validation: `passed`
- selected app: `ray_triangle_custom_scored_accumulation`
- POD authorized: `False`
- next goal: `Goal4710 ray-triangle custom scored accumulation app-level protocol freeze`

## Selected Target Contract

- app family: ray/triangle custom scored accumulation
- generic feature: specialized Tier-3 scalar callback fusion for ray/triangle hit reduction
- not app-specific kernel: `True`
- minimum scale: >=262144 rays with dense and sparse hit regimes; larger row optional if POD budget allows

## Rejected Existing Targets

| target | reason |
|---|---|
| `rt_dbscan` | Goal4670/4671 found modest/no-go second-win evidence; component union is not solved by scalar callback fusion. |
| `raydb_style` | Goal4655 app row is parity; no clean new V4 runtime lever identified. |
| `triangle_counting` | Large V2.14 ratio is historical route evolution; V4-over-V3 increment is modest and not a clean new V4 feature proof. |
| `librts_spatial_index` | Goal4655 app row is parity; no current V4 lever moves it. |
| `hausdorff_xhd` | Current blocker is correctness/normalization, not proven V4 performance. |
| `rtnn` | Ranked-summary/top-k candidate was deferred for serious-scale parity or below-parity rows. |

## Boundary

Goal4709 selects a target and authorizes only Goal4710 protocol freeze. It does not authorize POD spend, app-level speed claims, release wording, or public Tier-3 support.
