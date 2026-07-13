# Goal4984 Result: Correctness And Genericity Gate Before Final v2.14.3 Matrix

Date: 2026-07-04

## Verdict

```text
completed_correctness_and_genericity_gate_for_v2_14_3_matrix
```

Goal4984 gates the final v2.14.3 performance matrix. The purpose is to ensure the matrix is not measured on a build that silently regressed RayJoin correctness or turned a generic RTDL capability into a RayJoin-only path.

## Local Compile Gate

Command:

```text
$env:PYTHONPATH='src'; py -m py_compile src/rtdsl/embree_runtime.py src/rtdsl/optix_runtime.py Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

Result:

```text
passed
```

The Python launcher printed the local environment warning:

```text
Could not find platform independent libraries <prefix>
```

but exited `0`.

## v2.14.3 Route / Genericity Tests

Command:

```text
$env:PYTHONPATH='src'; py -m unittest `
  tests.goal4977_fast_scaled_point_pack_test `
  tests.goal4978_grouped_carrier_decomposition_test `
  tests.goal4979_grouped_carrier_side_work_metrics_test `
  tests.goal4981_reversed_side_order_binary_route_test `
  tests.goal4948_non_rayjoin_hit_stream_numba_genericity_test `
  tests.goal4964_exact_lsi_pair_id_device_columns_test `
  tests.goal4968_planar_map_lsi_workspace_contract_test `
  tests.goal4972_bounded_exact_lsi_producer_test `
  tests.goal4973_exact_lsi_cost_decomposition_test `
  tests.goal4974_point_location_device_face_columns_route_test
```

Result:

```text
Ran 27 tests in 0.098s
OK (skipped=1)
```

The skip is the runtime OptiX + Numba CUDA execution subtest on the local Windows machine. Static genericity and CPU-level tests passed.

## RayJoin Correctness Regression Tests

Command:

```text
$env:PYTHONPATH='src'; py -m unittest `
  tests.goal4374_rayjoin_exact_paper_suite_test `
  tests.goal4866_rayjoin_section57_output_contract_test `
  tests.goal4373_rayjoin_cdb_point_location_route_test `
  tests.goal4834_rayjoin_sos_synthetic_contract_test
```

Initial result:

```text
1 failure
```

The failure was not a runtime regression. It was a stale assertion in `tests.goal4374_rayjoin_exact_paper_suite_test` expecting:

```text
RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER = 5
```

The current contract, already covered by `tests.goal4894_directed_point_location_fine_grained_default_test`, is:

```text
RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER = 0
```

Fix applied:

```text
tests/goal4374_rayjoin_exact_paper_suite_test.py
```

The stale expected value was updated from `5` to `0`.

Re-run result:

```text
Ran 54 tests in 2.844s
OK
```

Contract cross-check:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal4894_directed_point_location_fine_grained_default_test
Ran 3 tests in 0.013s
OK
```

## Non-RayJoin Genericity Smoke

Command:

```text
$env:PYTHONPATH='src'; py -m unittest `
  tests.goal4955_projected_descriptor_pipeline_test `
  tests.goal4948_non_rayjoin_hit_stream_numba_genericity_test
```

Result:

```text
Ran 3 tests in 0.105s
OK (skipped=1)
```

This covers:

- non-RayJoin projected descriptor pipeline;
- hit-stream row-buffer adapter genericity;
- absence of RayJoin/overlay/output-chain terms in the generic hit-stream adapter;
- runtime Numba execution subtest skipped locally because OptiX + CUDA is unavailable.

## Interpretation

Goal4984 passes as a local gate:

- the v2.14.3 modified Python files compile;
- the new v2.14.3 helper and route tests pass;
- the RayJoin correctness regression suite passes after updating one stale historical test assertion to the current contract;
- the non-RayJoin genericity smoke passes at the static/CPU level on local Windows.

This is sufficient to authorize the final matrix as a local-source correctness/genericity gate.

It does not prove GPU runtime genericity on this local machine. That remains covered by prior POD evidence and should not be overstated in public text.

## Claim Boundary

Authorized:

- proceed to final v2.14.3 matrix on the verified source state;
- state that local correctness/genericity gate passed;
- state that one stale test expectation was repaired to current Goal4894 contract.

Not authorized:

- no claim that all GPU runtime genericity tests were executed locally;
- no author-performance claim;
- no claim that the writer-free binary route is fully generic merely because RayJoin passes;
- no public exposure of internal goal numbers.

## Next Step

Proceed to Goal4985:

- final v2.14.3 performance matrix;
- fresh and warm/diagnostic columns side by side;
- no warm-only headline;
- top4 author ratio either measured or explicitly absent.
