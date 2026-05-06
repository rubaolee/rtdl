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
- Refactored `collect_k_bounded_candidate_pairs(...)` to delegate to the
  v1.5.1 app-generic `collect_k_bounded_rows(..., row_width=2)` reference
  contract while preserving the old `candidate_pairs` transition field.
- Added `tests/goal1411_v1_5_1_polygon_collect_k_helper_bridge_test.py`.
- Updated the generic Jaccard score-reduction bridge to consume
  `candidate_id_rows` directly, with `candidate_pairs` retained only as a
  transition fallback.
- Added `tests/goal1412_v1_5_1_jaccard_consumes_generic_collect_rows_test.py`.
- Added `validate_collect_k_bounded_result(...)`, a reusable v1.5.1 validator
  for completed app-generic bounded collection buffers.
- Updated the Jaccard continuation bridge to validate `candidate_id_rows`
  through that shared result validator.
- Added `tests/goal1413_v1_5_1_collect_k_result_validator_test.py`.
- Updated the legacy `candidate_pairs` transition fallback so it is
  normalized through the same `collect_k_bounded_rows(..., row_width=2)`
  contract before Jaccard scoring, instead of bypassing canonical row-buffer
  semantics.
- Added
  `tests/goal1414_v1_5_1_legacy_candidate_pairs_contract_bridge_test.py`.

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

Additional Windows command after bridging the polygon-pair helper to the
app-generic row-buffer contract:

```cmd
set PYTHONPATH=src;.
py -3 -m unittest tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1410_v1_5_1_native_collect_k_row_buffer_surface_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test tests.goal1318_v1_5_jaccard_native_collection_routing_test tests.goal1399_collect_k_bounded_resolution_test
```

Result:

```text
Ran 34 tests in 0.044s
OK
```

Additional Windows command after making Jaccard continuation consume generic
`candidate_id_rows` directly:

```cmd
set PYTHONPATH=src;.
py -3 -m unittest tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test tests.goal1412_v1_5_1_jaccard_consumes_generic_collect_rows_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test tests.goal1318_v1_5_jaccard_native_collection_routing_test
```

Result:

```text
Ran 26 tests in 0.012s
OK
```

Additional Windows command after adding the shared completed-result validator:

```cmd
set PYTHONPATH=src;.
py -3 -m unittest tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test tests.goal1412_v1_5_1_jaccard_consumes_generic_collect_rows_test tests.goal1413_v1_5_1_collect_k_result_validator_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test
```

Result:

```text
Ran 29 tests in 0.010s
OK
```

The Windows Python startup warning `Could not find platform independent
libraries <prefix>` was observed and was non-fatal.

Additional Windows command after hardening the legacy `candidate_pairs`
transition fallback:

```cmd
set PYTHONPATH=src;.
py -3 -m unittest tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1410_v1_5_1_native_collect_k_row_buffer_surface_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test tests.goal1412_v1_5_1_jaccard_consumes_generic_collect_rows_test tests.goal1413_v1_5_1_collect_k_result_validator_test tests.goal1414_v1_5_1_legacy_candidate_pairs_contract_bridge_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test
```

Result:

```text
Ran 35 tests in 0.015s
OK
```

NVIDIA pod validation, using
`root@213.173.102.217 -p 25443` on Ubuntu Linux with NVIDIA RTX A4500,
driver 550.127.05, CUDA 12.4, and OptiX headers vendored at
`/root/vendor/optix-dev`:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1410_v1_5_1_native_collect_k_row_buffer_surface_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test tests.goal1412_v1_5_1_jaccard_consumes_generic_collect_rows_test tests.goal1413_v1_5_1_collect_k_result_validator_test tests.goal1414_v1_5_1_legacy_candidate_pairs_contract_bridge_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test
```

Result:

```text
Ran 35 tests in 0.005s
OK
```

The same pod also built the native OptiX runtime with:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev CUDA_PREFIX=/usr/local/cuda NVCC=/usr/local/cuda/bin/nvcc
```

Then a small internal OptiX sanity run over generic raw ray/triangle
`ANY_HIT` plus `COUNT_HITS` reported CPU/OptiX row parity, direct hit-count
parity, and prepared OptiX hit-count parity. This sanity run remains internal
evidence only and does not authorize public speedup wording.

## Next Work

The next v1.5.1 slices should make native Embree and OptiX collection paths
return or validate against this app-generic result-buffer contract. Native
promotion, benchmark evidence, public wording, and release decisions still need
the required parity, bounds, and external-review gates.
