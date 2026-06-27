# Goal1614 v1.6.4 COLLECT_K_BOUNDED Bounds Stress

## Verdict

ACCEPTED as local prepared host-output exact-bounds stress evidence.

## Scope

- Primitive: `COLLECT_K_BOUNDED`
- Scope: `prepared_host_output_exact_bounds_stress`
- Backends: `fake_native`
- Required backends: `fake_native`
- Case count per backend: `9`
- Timing is not performance evidence.

## Outcome

| Backend | Case | Expected | Status | Capacity | Row width |
| --- | --- | --- | --- | ---: | ---: |
| `fake_native` | `empty_zero_capacity` | `pass` | `pass` | `0` | `2` |
| `fake_native` | `exact_fit_unsorted_duplicates` | `pass` | `pass` | `3` | `2` |
| `fake_native` | `duplicate_compression_avoids_overflow` | `pass` | `pass` | `2` | `2` |
| `fake_native` | `k_plus_one_overflow_preserves_output` | `overflow` | `pass` | `2` | `2` |
| `fake_native` | `zero_capacity_positive_overflow` | `overflow` | `pass` | `0` | `2` |
| `fake_native` | `row_width_one_exact` | `pass` | `pass` | `2` | `1` |
| `fake_native` | `row_width_three_exact` | `pass` | `pass` | `2` | `3` |
| `fake_native` | `row_width_mismatch_rejected` | `value_error` | `pass` | `1` | `2` |
| `fake_native` | `negative_capacity_rejected` | `value_error` | `pass` | `-1` | `2` |

## Claim Boundary

Goal1614 stress-tests prepared host-output COLLECT_K_BOUNDED bounds semantics. It is correctness evidence only and does not authorize stable promotion, public speedup wording, true zero-copy wording, whole-app speedup claims, broad RTX/GPU wording, release tags, or release action.
