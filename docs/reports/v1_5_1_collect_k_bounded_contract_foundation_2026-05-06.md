# v1.5.1 COLLECT_K_BOUNDED Contract Foundation - 2026-05-06

## Verdict

The first v1.5.1 implementation slice establishes an app-generic Python+RTDL
contract foundation for `COLLECT_K_BOUNDED`.

This is not public promotion, not native Embree/OptiX parity, not a benchmark
claim, and not a zero-copy claim. It creates the stable contract shape that
native Embree and OptiX paths should satisfy next.

## Implemented

- Added `src/rtdsl/v1_5_1_collect_k_bounded.py`.
- Added `collect_k_bounded_rows(...)`, an app-generic Python reference
  materialization path for dense bounded candidate-id rows.
- Added `v1_5_1_collect_k_bounded_contract()` and
  `validate_v1_5_1_collect_k_bounded_contract()`.
- Exported the v1.5.1 contract symbols through `rtdsl`.
- Added `tests/goal1409_v1_5_1_collect_k_bounded_contract_test.py`.
- Updated the existing Embree and OptiX polygon-pair collection Python wrappers
  to expose v1.5.1 app-generic row-buffer metadata while preserving the older
  `candidate_pairs` and `bounded_candidate_pair_ids` fields for transition
  compatibility.
- Added `tests/goal1410_v1_5_1_native_collect_k_row_buffer_surface_test.py`.

## Contract Shape

The v1.5.1 candidate contract defines:

- primitive: `COLLECT_K_BOUNDED`;
- track: `python_rtdl`;
- backend scope: `embree`, `optix`;
- result layout: `dense_candidate_id_rows_with_valid_count`;
- capacity parameter: `k`;
- capacity unit: `candidate_id_rows`;
- ordering policy: stable lexicographic ordering by candidate-id row;
- duplicate policy: deduplicate before capacity check;
- overflow policy: fail closed before result materialization;
- no truncation;
- no partial result on overflow;
- no score or reduction after overflow.

## Bounds Coverage

The new test covers:

- `k=0` with zero results;
- `k=0` overflow with positive results;
- exact-`k` full buffer success;
- `k+1` overflow;
- deterministic ordering;
- duplicate rows deduplicated before capacity check;
- row-width mismatch rejection;
- negative-`k` rejection.

## Validation

Windows command:

```cmd
set PYTHONPATH=src;.
py -3 -m unittest tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test tests.goal1399_collect_k_bounded_resolution_test
```

Result:

```text
Ran 23 tests in 0.030s
OK
```

Additional Windows command after wrapper metadata integration:

```cmd
set PYTHONPATH=src;.
py -3 -m unittest tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1410_v1_5_1_native_collect_k_row_buffer_surface_test tests.goal1315_v1_5_optix_native_candidate_collection_abi_test tests.goal1317_v1_5_embree_native_candidate_collection_abi_test tests.goal1318_v1_5_jaccard_native_collection_routing_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test
```

Result:

```text
Ran 28 tests in 0.020s
OK
```

The Windows Python startup warning `Could not find platform independent
libraries <prefix>` was observed and was non-fatal.

## Next Work

The next v1.5.1 slices should make native Embree and OptiX collection paths
return or validate against this app-generic result-buffer contract. Native
promotion, benchmark evidence, public wording, and release decisions still need
the required parity, bounds, and external-review gates.
