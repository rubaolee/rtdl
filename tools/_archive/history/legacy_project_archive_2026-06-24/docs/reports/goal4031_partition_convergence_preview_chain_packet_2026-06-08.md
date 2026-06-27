# Goal4031 Partition Convergence Preview Chain Packet

Date: 2026-06-08

## Scope

This packet summarizes the v2.8 fixed-radius partition-convergence work from Goal4019 through Goal4032.

## What Is Proven

- Goal4019 adds `validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(...)`, a same-contract validator for partition-summary columns.
- Goal4021 adds `build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(...)`, a component-label oracle that checks safe-skip, safe-full, and ambiguous partition pairs against brute-force all-pairs fixed-radius labels.
- Goal4023 makes overflow and `complete_candidate_coverage` fail closed.
- Goal4024 strengthens single-point, safe-skip/safe-full/ambiguous, and floating-point tolerance edge cases.
- Goal4027 adds a CuPy executable preview that passed pod validation.
- Goal4029 adds a Numba CUDA device-column preview that passed pod validation.
- Goal4030 records both previews in candidate metadata while keeping the strategy unpromoted.
- Goal4032 strengthens the CuPy preview with a `device_bounded_offsets` pair-enumeration mode that passed pod same-contract validation.

## Diagnostic Root-Work Opportunity

Goal4026 estimates potential root-read work reduction using Goal4014 partition enumeration and Goal4007 grouped-union root-read telemetry. This is diagnostic, not a timing claim.

At 65,536 points, the conservative model estimates:

| Profile | Current Root Finds | Estimated Partition Route Root Upper | Estimated Root-Read Reduction |
| --- | ---: | ---: | ---: |
| clustered3d | 548,003,862 | 215,732,147 | 60.63% |
| road3d | 171,688,664 | 67,242,368 | 60.83% |
| ngsim_dense | 24,764,290 | 21,778,905 | 12.06% |

The model charges two root reads per safe-full partition pair and ambiguous root reads from the measured ambiguous-of-near-pair ratio. It is intentionally conservative.

## What Is Not Proven

- No fast native partition-summary producer exists yet.
- `partition_convergence_hybrid` remains `candidate_requires_native_implementation`.
- CuPy and Numba previews are executable bridges, not final fast native producers.
- The CuPy device-bounded pair preview removes host pair enumeration for the small same-contract preview path, but it is not a timed large-scale producer and does not promote the strategy.
- No speedup, release, broad RT-core, whole-app benchmark, or true-zero-copy wording is authorized.

## Next Engineering Target

The next real performance step is a native or fully device-resident producer that fills the partition-summary columns without host pair enumeration, then passes:

- Goal4019 same-contract validator;
- Goal4021 component-label oracle;
- Goal4023 complete coverage invariant;
- Goal4024 edge cases;
- pod execution on CuPy and Numba preview-compatible device columns.

Only after that should large timing runs compare it against the current grouped-stream route.
