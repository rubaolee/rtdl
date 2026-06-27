# Goal4021 Partition Convergence Component Reference

Date: 2026-06-08

## Purpose

Goal4021 adds the first full correctness oracle for the `partition_convergence_hybrid` candidate strategy:

`build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(...)`.

It consumes the Goal4016/4017 partition-summary stream, checks it with the Goal4019 same-contract validator, then applies the intended hybrid logic:

- skip `near_pair_status = 0` partition pairs;
- union all points for safe-full partition pairs (`near_pair_status = 1`);
- enumerate only ambiguous pairs (`near_pair_status = 2`) and union exact point pairs within radius;
- compare the resulting component labels against a brute-force all-pairs fixed-radius graph.

## Why This Matters

The current executable grouped-union route is correct but root-read heavy on dense inputs. The partition-convergence direction should reduce that work by handling large safe partition regions as grouped summaries while preserving exactness at ambiguous boundaries.

This reference gives future native or partner producers a precise target: they must match the same component labels as the all-pairs fixed-radius graph before any performance evidence can be considered.

## Boundary

This goal does not add a native ABI. It does not make `partition_convergence_hybrid` an executable runtime route. It does not authorize public speedup wording, RT-core speedup wording, whole-app benchmark wording, release wording, or true zero-copy wording.

The next implementation step is a narrow native or partner producer for the partition-summary columns that passes Goal4019 and this Goal4021 oracle on deterministic small cases before any large-scale pod timing.

