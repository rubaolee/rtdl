# Goal 1417 v1.5.1 COLLECT_K_BOUNDED Multi-Environment Benchmark Summary

## Verdict

ACCEPTED for the measured v1.5.1 benchmark package.

This is same-contract `COLLECT_K_BOUNDED` bounded candidate-row benchmark evidence only. It is not a public primitive promotion, not a speedup claim, and not a zero-copy claim.

## Run Scope

- Repository HEAD: `8b8332dd1c8638ef9f539c5ec0fe4ec62d27a4b2`
- Scales: `copies=1`, `copies=16`, `copies=64`
- Contract: row width `2`, exact capacity equals expected candidate-row count, canonical candidate-id rows, complete coverage required
- Windows command: `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1417_v1_5_1_collect_k_benchmark_test tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1413_v1_5_1_collect_k_result_validator_test tests.goal1415_v1_5_1_native_collect_k_zero_capacity_test`
- Windows artifact command: `$env:PYTHONPATH='src;.'; py -3 scripts\goal1417_v1_5_1_collect_k_benchmark.py --copies 1 --copies 16 --copies 64 --repeats 5 --warmups 1`
- Linux command: `PYTHONPATH=src:. python3 -m unittest tests.goal1417_v1_5_1_collect_k_benchmark_test tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1413_v1_5_1_collect_k_result_validator_test tests.goal1415_v1_5_1_native_collect_k_zero_capacity_test && PYTHONPATH=src:. python3 scripts/goal1417_v1_5_1_collect_k_benchmark.py --backend python_reference --backend embree --require-backend embree --copies 1 --copies 16 --copies 64 --repeats 5 --warmups 1`
- NVIDIA pod command: `RTDL_OPTIX_LIB=/root/work/rtdl_v1_5_1_pod/build/librtdl_optix.so LD_LIBRARY_PATH=/root/work/rtdl_v1_5_1_pod/build:$LD_LIBRARY_PATH PYTHONPATH=src:. python3 -m unittest tests.goal1417_v1_5_1_collect_k_benchmark_test tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1413_v1_5_1_collect_k_result_validator_test tests.goal1415_v1_5_1_native_collect_k_zero_capacity_test && PYTHONPATH=src:. python3 scripts/goal1417_v1_5_1_collect_k_benchmark.py --backend python_reference --backend optix --require-backend optix --copies 1 --copies 16 --copies 64 --repeats 5 --warmups 1`

## Benchmark Outcome

- Windows focused unit slice: `Ran 28 tests`, `OK`
- Windows artifact: Python reference `pass=3, fail=0, skipped=0`; Embree `pass=3, fail=0, skipped=0`; OptiX `pass=0, fail=0, skipped=3` because `librtdl_optix` was not present on Windows
- Linux host `192.168.1.20`: Embree required-backend artifact `ACCEPTED`, Python reference `pass=3, fail=0, skipped=0`, Embree `pass=3, fail=0, skipped=0`
- NVIDIA pod `213.173.102.217:25443`: OptiX required-backend artifact `ACCEPTED`, Python reference `pass=3, fail=0, skipped=0`, OptiX `pass=3, fail=0, skipped=0`
- Required backend skips: none in the Linux Embree required run and none in the NVIDIA pod OptiX required run

## Measured Medians

- Windows Embree median seconds: `copies=1` `0.000150300`, `copies=16` `0.002452600`, `copies=64` `0.031193100`
- Linux Embree median seconds: `copies=1` `0.000051770`, `copies=16` `0.000823825`, `copies=64` `0.009634878`
- NVIDIA pod OptiX median seconds: `copies=1` `0.000730745`, `copies=16` `0.001024656`, `copies=64` `0.002125360`
- These are raw same-contract timing observations only. They are not public speedup wording.

## Files

- Harness: `scripts/goal1417_v1_5_1_collect_k_benchmark.py`
- Unit tests: `tests/goal1417_v1_5_1_collect_k_benchmark_test.py`
- Windows generated JSON artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_2026-05-06.json`
- Windows generated Markdown artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_2026-05-06.md`
- Linux Embree generated JSON artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_linux_embree_2026-05-06.json`
- Linux Embree generated Markdown artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_linux_embree_2026-05-06.md`
- NVIDIA pod OptiX generated JSON artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_nvidia_pod_optix_2026-05-06.json`
- NVIDIA pod OptiX generated Markdown artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_nvidia_pod_optix_2026-05-06.md`
- Multi-environment summary: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_multi_env_2026-05-06.md`
