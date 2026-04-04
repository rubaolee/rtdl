# Goal 66 Vulkan Correctness Closure

Date: 2026-04-04
Host: `192.168.1.20`

## Summary

Goal 66 repaired Vulkan correctness on the accepted bounded Linux comparison
surface from Goal 65.

The Vulkan backend now matches the native C oracle across the full accepted
Goal 65 surface:

- `County ⊲⊳ Zipcode` bounded ladder:
  - `1x4`
  - `1x5`
  - `1x6`
  - `1x8`
  - `1x10`
  - `1x12`
- `BlockGroup ⊲⊳ WaterBodies` bounded ladder:
  - `county2300_s04`
  - `county2300_s05`
- bounded `LKAU ⊲⊳ PKAU` `sunshine_tiny` `overlay-seed analogue`

## Code changes

Files changed:

- [Makefile](../../Makefile)
- [rtdl_vulkan.cpp](../../src/native/rtdl_vulkan.cpp)

What changed:

- Vulkan now links GEOS so it can use the same prepared-polygon `covers`
  semantics already accepted in the oracle and OptiX backends.
- Vulkan `pip` now overwrites GPU results with exact host-side truth:
  - GEOS-backed where available
  - exact inclusive point-in-polygon fallback otherwise
- Vulkan `overlay` now adds the accepted host-side `requires_pip` supplement
  and computes final `requires_lsi` from exact host-side segment intersections.
- Vulkan `lsi` final truth now comes from exact host-side segment intersection
  rows in original row order, rather than trusting raw GPU records as final
  output.

## Validation

Local:

- `python3 -m py_compile scripts/goal65_vulkan_optix_linux_comparison.py tests/goal65_vulkan_optix_linux_comparison_test.py tests/rtdsl_vulkan_test.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal65_vulkan_optix_linux_comparison_test tests.rtdsl_vulkan_test`
- `PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group full`

Result:

- full matrix: `273` tests, `1` skip, `OK`

Remote on `192.168.1.20`:

- `make build-vulkan`
- `PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test`
- `PYTHONPATH=src:. RTDL_OPTIX_PTX_COMPILER=nvcc RTDL_NVCC=/usr/bin/nvcc python3 scripts/goal51_vulkan_validation.py --output build/goal66_preflight_goal51.json`
- full rerun of `scripts/goal65_vulkan_optix_linux_comparison.py`

Remote results:

- `tests.rtdsl_vulkan_test`: `12` tests, `OK`
- Goal 51 Vulkan validation: `8/8` parity-clean
- Goal 65 bounded rerun: parity-clean for Vulkan across the full accepted
  surface

Supporting rerun artifacts:

- [goal66_goal65_rerun_summary.json](../../build/goal66/goal66_goal65_rerun_summary.json)
- [goal66_goal65_rerun_summary.md](../../build/goal66/goal66_goal65_rerun_summary.md)

## Performance reading

After the correctness repair, Vulkan is parity-clean on the accepted bounded
surface, but OptiX remains the faster GPU backend on the same host for these
accepted comparisons.

Examples from the final rerun:

- County/Zipcode `1x12` `lsi`
  - OptiX warm: `0.001186195 s`
  - Vulkan warm: `0.006408974 s`
- County/Zipcode `1x12` `pip`
  - OptiX warm: `0.002231416 s`
  - Vulkan warm: `0.006674321 s`
- `LKAU ⊲⊳ PKAU` bounded `overlay-seed analogue`
  - OptiX warm: `0.083731031 s`
  - Vulkan warm: `0.090084720 s`

So Goal 66 closes correctness on the accepted bounded surface, but it does not
change the current ranking:

- OptiX is still the accepted faster GPU backend on `192.168.1.20`
- Vulkan remains a bounded, correctness-repaired path

## Boundary

Goal 66 does **not** prove that Vulkan is fully mature.

The following Goal 65 boundaries still apply:

- whole `County ⊲⊳ Zipcode top4` `lsi` is still blocked by the current
  `uint32` output-capacity contract
- larger `BlockGroup ⊲⊳ WaterBodies` `lsi` slices still hit the current
  `512 MiB` Vulkan guardrail

So the honest new state is:

- Vulkan is now parity-clean on the accepted bounded Goal 65 surface
- Vulkan is still not ready for unbounded promotion alongside OptiX
