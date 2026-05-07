# Goal 1434 v1.5.1 Full Pod Regression

## Verdict

ACCEPTED for the measured full Linux GPU-pod source-tree regression package.

After the collect-k wrapper tests were aligned with the built generic i64 symbol route, the pod checkout was reset to `origin/main`, Embree and OptiX were rebuilt, and full unittest discovery passed.

## Evidence

- Embree rebuild transcript: `docs/reports/goal1434_v1_5_1_full_pod_rebuild_embree_2026-05-07.txt`
- OptiX rebuild transcript: `docs/reports/goal1434_v1_5_1_full_pod_rebuild_optix_2026-05-07.txt`
- Full unittest transcript: `docs/reports/goal1434_v1_5_1_full_pod_unittest_discover_2026-05-07.txt`

## Run Scope

- Host: GPU pod at `root@69.30.85.196`, SSH port `22030`
- GPU: NVIDIA RTX A5000
- Driver: `580.126.09`
- Repository path: `/workspace/rtdl`
- Git HEAD: `bb3fbb317725c0602b7b4313d64162edad0db48c`
- Native setup: `RTDL_FORCE_EMBREE_REBUILD=1` Embree rebuild plus `make build-optix`
- Test command: `PYTHONPATH=src:. RTDL_OPTIX_LIB=/workspace/rtdl/build/librtdl_optix.so python3 -m unittest discover -s tests -p '*_test.py'`

## Result

- Full pod unittest discovery: `Ran 2818 tests in 834.491s`
- Outcome: `OK (skipped=221)`
- Failures: none
- Errors: none

## Claim Boundary

This is full source-tree pod regression evidence only. It does not authorize stable `COLLECT_K_BOUNDED` promotion, public speedup wording, zero-copy wording, whole-app claims, broad workload claims, release tags, or release action.
