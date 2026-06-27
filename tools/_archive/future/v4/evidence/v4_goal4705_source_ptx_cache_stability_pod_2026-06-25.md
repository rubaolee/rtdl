# V4 Goal4705 Source-Level PTX Cache Stability

- status: `source_ptx_cache_stability_measured_not_public_support`
- classification: `pass_source_level_cache_stability_gate_not_public_support`
- rows checked: `4`
- stable source cache keys: `True`

| variant | raw PTX equal | canonical PTX equal | cache key stable | changed PTX changes key | changed toolchain changes key |
|---|---|---|---|---|---|
| `custom_scalar_reduce_weighted_sum` | `False` | `True` | `True` | `True` | `True` |
| `custom_score_affine` | `False` | `True` | `True` | `True` | `True` |
| `custom_threshold_flag` | `False` | `True` | `True` | `True` | `True` |
| `custom_minmax_score` | `False` | `True` | `True` | `True` | `True` |

## Boundary

This gate hardens cache behavior only. It does not authorize public Tier-3 support, release wording, or performance claims.
