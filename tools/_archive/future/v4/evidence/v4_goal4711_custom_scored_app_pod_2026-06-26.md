# V4 Goal4711 Custom Scored App Focused POD Result

- status: `goal4711_custom_scored_app_measured_not_release`
- classification: `fail_focused_app_gate_not_high_performance`
- primary geomean V2 speedup: `1.0289410940907995`
- primary geomean V3 speedup: `1.0289410940907995`
- min primary V3 speedup: `1.0144917291107025`
- denominator quality: `strong_materialized_device_fallback_after_no_custom_repo_route_found`

## Rows

| callback | role | regime | scale | correctness | V4 fused s | fallback s | V3 baseline/V4 |
|---|---|---|---:|---|---:|---:|---:|
| weighted_sum | control | dense_hits | 262144 | true | 0.000241440 | 0.000248832 | 1.031x |
| weighted_sum | control | sparse_hits | 262144 | true | 0.000110368 | 0.000116800 | 1.058x |
| weighted_sum | control | no_hit_empty_reduction | 262144 | true | 0.000055424 | 0.000059424 | 1.072x |
| weighted_sum | control | dense_hits | 524288 | true | 0.000451968 | 0.000458400 | 1.014x |
| weighted_sum | control | sparse_hits | 524288 | true | 0.000196256 | 0.000204064 | 1.040x |
| weighted_sum | control | no_hit_empty_reduction | 524288 | true | 0.000082240 | 0.000087104 | 1.059x |
| affine_score | primary | dense_hits | 262144 | true | 0.000242528 | 0.000248704 | 1.025x |
| affine_score | primary | sparse_hits | 262144 | true | 0.000112704 | 0.000120800 | 1.072x |
| affine_score | primary | no_hit_empty_reduction | 262144 | true | 0.000055584 | 0.000060800 | 1.094x |
| affine_score | primary | dense_hits | 524288 | true | 0.000452672 | 0.000459232 | 1.014x |
| affine_score | primary | sparse_hits | 524288 | true | 0.000201088 | 0.000205056 | 1.020x |
| affine_score | primary | no_hit_empty_reduction | 524288 | true | 0.000083776 | 0.000086752 | 1.036x |
| threshold_score | primary | dense_hits | 262144 | true | 0.000240992 | 0.000247296 | 1.026x |
| threshold_score | primary | sparse_hits | 262144 | true | 0.000108512 | 0.000114752 | 1.058x |
| threshold_score | primary | no_hit_empty_reduction | 262144 | true | 0.000056864 | 0.000064032 | 1.126x |
| threshold_score | primary | dense_hits | 524288 | true | 0.000451072 | 0.000458720 | 1.017x |
| threshold_score | primary | sparse_hits | 524288 | true | 0.000199840 | 0.000204128 | 1.021x |
| threshold_score | primary | no_hit_empty_reduction | 524288 | true | 0.000086336 | 0.000089600 | 1.038x |
| minmax_score | primary | dense_hits | 262144 | true | 0.000243264 | 0.000248768 | 1.023x |
| minmax_score | primary | sparse_hits | 262144 | true | 0.000111904 | 0.000115808 | 1.035x |
| minmax_score | primary | no_hit_empty_reduction | 262144 | true | 0.000056768 | 0.000055296 | 0.974x |
| minmax_score | primary | dense_hits | 524288 | true | 0.000452864 | 0.000460576 | 1.017x |
| minmax_score | primary | sparse_hits | 524288 | true | 0.000201536 | 0.000205728 | 1.021x |
| minmax_score | primary | no_hit_empty_reduction | 524288 | true | 0.000082432 | 0.000088736 | 1.076x |

## Denominator Boundary

V2.14 and V3.0.2 denominator discovery is recorded before V4 timing. If no exact custom-callback route is found, this run uses a strong materialized-device fallback: same OptiX hit discovery, device hit-id materialization, then a separate device callback/reduction kernel. It does not receive V4 callback-in-hit fusion, so the comparison targets the V4 increment while still requiring external denominator review before any public app-level claim.

## Non-Authorization

- V4 release is not authorized.
- Formal high-performance V4 wording is not authorized.
- Public Tier-3 support is not authorized.
- Arbitrary callback or raw OptiX callback support is not authorized.
