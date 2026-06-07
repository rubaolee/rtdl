# Goal3788 Hausdorff Generic Alias And Metadata Audit

Status: implemented and pod-validated.

## Purpose

Goal3788 closes a stale planning note rather than changing runtime behavior.
The future-version to-do list still described the Hausdorff partner adapter's
generic naming as future work, but Goal3160 had already introduced the generic
front door:

`directed_max_of_nearest_distance_2d_partner_columns`

The older `directed_hausdorff_2d_partner_columns` compatibility adapter remains
available. The benchmark app now uses the generic front door and reports
`generic_directed_max_of_nearest_distance_2d` as the reference contract.

## Findings

- The generic front door is exported from `rtdsl`.
- The Hausdorff benchmark app calls the generic front door, not the older
  compatibility name.
- The compatibility adapter remains available for existing users.
- The Numba metadata now reports
  `v2_8_partner_continuation_operations_semantics:
  executed_operations_this_call`.
- `sqrt_f64` is listed only when
  `materialize_nearest_distances=True` and the nearest-distance column is
  actually materialized.
- Goal3143 and Goal3160 tests already cover the executable Numba CUDA path
  when a CUDA-capable Numba environment is available.

## Action

The stale `Generic Adapter Naming` item was removed from:

`docs/research/future_version_to_do_list.md`

No runtime code or native code was changed.

## Boundary

Goal3788 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, true-zero-copy wording, automatic partner selection,
paper-reproduction wording, or app-specific native-engine logic.

It is a roadmap-cleanup and regression-audit goal only.

## Validation

Focused validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3788_hausdorff_generic_alias_and_metadata_audit_test tests.goal3143_hausdorff_partner_exact_numba_front_door_test tests.goal3160_hausdorff_generic_max_nearest_front_door_alias_test
```

Local result:

```text
Ran 14 tests in 0.039s
OK (skipped=4)
```

Pod result:

```text
Pod: root@69.30.85.203 -p 22057
Workdir: /root/rtdl_goal3788_clean_1780857956
Commit: 0d1be8e7
GPU: NVIDIA RTX A5000
Numba installed into checkout-local target: .pydeps_goal3788_numba
Numba CUDA available: True
Ran 14 tests in 0.920s
OK
```
