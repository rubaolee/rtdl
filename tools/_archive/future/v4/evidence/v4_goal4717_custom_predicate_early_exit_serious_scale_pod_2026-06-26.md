# V4 Goal4715 Custom Predicate Early-Exit Timing

- status: `goal4715_custom_predicate_early_exit_timing_measured_not_release`
- classification: `pass_focused_timing_gate_not_release`
- primary geomean V3 speedup: `4.632757911153888`
- min primary V3 speedup: `2.054686620906942`

| scale | regime | role | ok | V4 s | fallback s | fallback/V4 | V4 invocations | fallback invocations |
|---:|---|---|---|---:|---:|---:|---:|---:|
| 262144 | `dense_early_accept_k8` | `primary` | true | 0.000284384 | 0.000584320 | 2.055x | 262144 | 2097152 |
| 262144 | `dense_early_accept_k32` | `primary` | true | 0.000329184 | 0.002931650 | 8.906x | 262144 | 8388608 |
| 262144 | `sparse_early_accept_k32` | `primary` | true | 0.000129888 | 0.000606880 | 4.672x | 65536 | 2097152 |
| 262144 | `dense_late_accept_k32` | `control` | true | 0.001534270 | 0.002928990 | 1.909x | 8388608 | 8388608 |
| 262144 | `dense_reject_all_k32` | `control` | true | 0.001402240 | 0.002764350 | 1.971x | 8388608 | 8388608 |
| 262144 | `no_hit_empty` | `control` | true | 0.000062336 | 0.000071968 | 1.155x | 0 | 0 |
| 524288 | `dense_early_accept_k8` | `primary` | true | 0.000508160 | 0.001117090 | 2.198x | 524288 | 4194304 |
| 524288 | `dense_early_accept_k32` | `primary` | true | 0.000591360 | 0.005720420 | 9.673x | 524288 | 16777216 |
| 524288 | `sparse_early_accept_k32` | `primary` | true | 0.000196768 | 0.001069980 | 5.438x | 131072 | 4194304 |
| 524288 | `dense_late_accept_k32` | `control` | true | 0.002978590 | 0.005723260 | 1.921x | 16777216 | 16777216 |
| 524288 | `dense_reject_all_k32` | `control` | true | 0.002665660 | 0.005362720 | 2.012x | 16777216 | 16777216 |
| 524288 | `no_hit_empty` | `control` | true | 0.000088544 | 0.000099008 | 1.118x | 0 | 0 |

## Boundary

This gate compares V4 any-hit predicate early termination against a materialized-device fallback that traces the same geometry, writes all hit layers to device memory, then evaluates the predicate and reduces accepted flags in separate device kernels. It does not authorize release, public Tier-3 support, arbitrary callback support, raw OptiX callback support, or all-app claims.
