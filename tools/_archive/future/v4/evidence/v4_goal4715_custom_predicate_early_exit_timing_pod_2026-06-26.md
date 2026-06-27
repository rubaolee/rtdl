# V4 Goal4715 Custom Predicate Early-Exit Timing

- status: `goal4715_custom_predicate_early_exit_timing_measured_not_release`
- classification: `pass_focused_timing_gate_not_release`
- primary geomean V3 speedup: `3.608025018751732`
- min primary V3 speedup: `1.9761904761904763`

| scale | regime | role | ok | V4 s | fallback s | fallback/V4 | V4 invocations | fallback invocations |
|---:|---|---|---|---:|---:|---:|---:|---:|
| 65536 | `dense_early_accept_k8` | `primary` | true | 0.000092736 | 0.000183264 | 1.976x | 65536 | 524288 |
| 65536 | `dense_early_accept_k32` | `primary` | true | 0.000115008 | 0.000770688 | 6.701x | 65536 | 2097152 |
| 65536 | `sparse_early_accept_k32` | `primary` | true | 0.000065312 | 0.000180864 | 2.769x | 16384 | 524288 |
| 65536 | `dense_late_accept_k32` | `control` | true | 0.000426336 | 0.000765920 | 1.797x | 2097152 | 2097152 |
| 65536 | `dense_reject_all_k32` | `control` | true | 0.000387008 | 0.000724128 | 1.871x | 2097152 | 2097152 |
| 65536 | `no_hit_empty` | `control` | true | 0.000040768 | 0.000044288 | 1.086x | 0 | 0 |
| 131072 | `dense_early_accept_k8` | `primary` | true | 0.000161696 | 0.000321280 | 1.987x | 131072 | 1048576 |
| 131072 | `dense_early_accept_k32` | `primary` | true | 0.000182432 | 0.001483330 | 8.131x | 131072 | 4194304 |
| 131072 | `sparse_early_accept_k32` | `primary` | true | 0.000086816 | 0.000323264 | 3.724x | 32768 | 1048576 |
| 131072 | `dense_late_accept_k32` | `control` | true | 0.000782752 | 0.001473540 | 1.883x | 4194304 | 4194304 |
| 131072 | `dense_reject_all_k32` | `control` | true | 0.000708992 | 0.001388540 | 1.958x | 4194304 | 4194304 |
| 131072 | `no_hit_empty` | `control` | true | 0.000057024 | 0.000060704 | 1.065x | 0 | 0 |

## Boundary

This gate compares V4 any-hit predicate early termination against a materialized-device fallback that traces the same geometry, writes all hit layers to device memory, then evaluates the predicate and reduces accepted flags in separate device kernels. It does not authorize release, public Tier-3 support, arbitrary callback support, raw OptiX callback support, or all-app claims.
