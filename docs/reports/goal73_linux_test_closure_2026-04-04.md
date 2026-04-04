# Goal 73 Report: Linux Test Closure

Date: 2026-04-04

Status:
- complete
- internal review package ready
- do not publish yet

## Goal

Goal 73 closed the Linux validation path after Goals 71 and 72. The target was
not just to run tests on an existing working tree, but to validate the current
published state on a clean Linux clone and repair any Linux-specific breakage
found there.

## Clean Validation Workspace

Host:
- `lestat-lx1` (`192.168.1.20`)

Clean clone used for validation:
- `/home/lestat/work/rtdl_goal73_clean`

Published base commit cloned:
- `af2ddf7`

## Linux-Specific Regressions Found

The first clean-clone run exposed three real Linux issues:

1. `src/native/rtdl_oracle.cpp`
- duplicate `bounds` declaration in `oracle_pip`
- this blocked native oracle builds in the clean clone

2. `src/rtdsl/oracle_runtime.py`
   and `src/rtdsl/embree_runtime.py`
- runtime-side GEOS pkg-config handling was too brittle
- clean Linux clones could miss the right GEOS pkg-config name and fail native
  library builds

3. `apps/goal15_pip_native.cpp`
- stale native ABI declaration for `rtdl_embree_run_pip`
- missing `positive_only` argument caused Linux native PIP smoke binaries to
  segfault

Goal 73 repaired all three issues before the final rerun.

## Final Linux Validation Results

### Full Matrix

Command:

```bash
cd /home/lestat/work/rtdl_goal73_clean
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group full
```

Result:
- `288` tests
- `1` skip
- `OK`

### Targeted GPU Slice

Command:

```bash
cd /home/lestat/work/rtdl_goal73_clean
PYTHONPATH=src:. python3 -m unittest \
  tests.rtdsl_vulkan_test \
  tests.goal71_prepared_backend_positive_hit_county_test \
  tests.goal69_pip_positive_hit_performance_test
```

Result:
- `18` tests
- `OK`

### Goal 51 Vulkan Validation

Command:

```bash
cd /home/lestat/work/rtdl_goal73_clean
PYTHONPATH=src:. RTDL_OPTIX_PTX_COMPILER=nvcc RTDL_NVCC=/usr/bin/nvcc \
python3 scripts/goal51_vulkan_validation.py \
  --output build/goal73_goal51_validation/summary.json
```

Result:
- all `8` validation targets parity-clean
- summary written successfully

## Imported Artifacts

- `docs/reports/goal73_linux_test_closure_artifacts_2026-04-04/full_matrix.log`
- `docs/reports/goal73_linux_test_closure_artifacts_2026-04-04/targeted_gpu.log`
- `docs/reports/goal73_linux_test_closure_artifacts_2026-04-04/goal51_validation.log`
- `docs/reports/goal73_linux_test_closure_artifacts_2026-04-04/goal51_summary.json`

## Accepted Meaning

Goal 73 establishes that the repo is again clean on the Linux validation path
after applying the Linux-specific repair patches above:

- clean clone validation works
- full matrix passes
- targeted GPU-sensitive tests pass
- Goal 51 Vulkan validation still passes

## Non-Claims

- Goal 73 does not claim that every historical scratch Linux workspace is clean
- Goal 73 does not claim that the unpublished paper work is finalized
- Goal 73 does not replace broader audit review; that remains the next goal
