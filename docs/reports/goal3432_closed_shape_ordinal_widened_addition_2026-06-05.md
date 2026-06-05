# Goal3432 Closed-Shape Ordinal Widened Addition

**Date:** 2026-06-05  
**Status:** implemented and pod-validated
**Scope:** close the residual low-risk arithmetic note from Goal3429 Claude review

## Purpose

Goal3429 accepted Goals 3427 and 3428, but kept one residual low-risk item from the earlier Goal3425 review: the native candidate-column kernel wrote point ordinals with a cast after `uint32_t` addition:

```cpp
(unsigned long long)(params.point_index_offset + pidx)
```

For current launch chunk limits this was not practical overflow risk, but the expression shape was still less precise than the intended 64-bit ordinal contract.

## Change

`src/native/optix/rtdl_optix_workloads.cpp` now widens both terms before addition:

```cpp
(unsigned long long)params.point_index_offset + (unsigned long long)pidx
```

This changes only the optional `point_ordinal` device column. Public `point_id` output remains unchanged.

## Test Coverage

`tests/goal3424_closed_shape_instance_identity_refinement_test.py` now asserts that the widened expression appears in the native workloads source.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3424_closed_shape_instance_identity_refinement_test tests.goal3427_prepared_cupy_refiner_timing_test tests.goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test
```

Result:

```text
Ran 14 tests in 0.035s
OK (skipped=1)
```

Pod validation on `root@69.30.85.203:22057`, clean `origin/main` checkout at commit `118ba948`:

```bash
export OPTIX_PREFIX=/root/vendor/optix-sdk
make build-optix
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so
python3 -m unittest \
  tests.goal3424_closed_shape_instance_identity_refinement_test \
  tests.goal3427_prepared_cupy_refiner_timing_test \
  tests.goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test
python3 examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
  --workload pip \
  --execution-route prepared_optix_cupy_refined_pip \
  --result-mode count \
  --candidate-max-rows 60000 \
  --dataset data/rayjoin_public_cdb/br_county.cdb \
  --no-rows
```

Result:

```text
Ran 14 tests in 0.678s
OK
route smoke produced valid JSON
```

## Boundary

This is a correctness hardening patch only. It does not authorize release, public speedup, RayJoin reproduction, broad RT-core speedup, true zero-copy, hidden dispatch, automatic retry, or native default-route claims.
