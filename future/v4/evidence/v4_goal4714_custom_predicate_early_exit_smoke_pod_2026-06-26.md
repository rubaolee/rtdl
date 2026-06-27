# V4 Goal4714 Custom Predicate Early-Exit Smoke

- status: `goal4714_custom_predicate_early_exit_smoke_measured_not_timing`
- classification: `pass_smoke_gate_not_timing_not_release`
- correctness all passed: `True`
- early termination primary passed: `True`

| regime | role | correctness | v4 invocations | fallback invocations | early termination |
|---|---|---|---:|---:|---|
| `dense_early_accept_k8` | `primary` | `True` | 4096 | 32768 | `True` |
| `dense_early_accept_k32` | `primary` | `True` | 4096 | 131072 | `True` |
| `dense_reject_all_k32` | `control` | `True` | 131072 | 131072 | `False` |
| `no_hit_empty` | `control` | `True` | 0 | 0 | `False` |

This smoke does not authorize POD timing, release, public Tier-3 support, or performance claims.
