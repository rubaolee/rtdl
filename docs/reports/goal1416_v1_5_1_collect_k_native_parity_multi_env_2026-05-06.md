# Goal 1416 v1.5.1 COLLECT_K_BOUNDED Multi-Environment Parity Summary

## Verdict

ACCEPTED for the measured v1.5.1 parity package.

This is same-contract `COLLECT_K_BOUNDED` native candidate-row parity evidence only. It is not a public primitive promotion, not a performance claim, and not a zero-copy claim.

## Run Scope

- Repository HEAD: `9813a0b7eea2d7ce1bffcb82159ea81f882f2d3c`
- Cases: `empty_zero_capacity`, `exact_fit_two_rows`, `one_short_fail_closed_overflow`, `zero_capacity_positive_fail_closed_overflow`
- Contract: row width `2`, stable canonical candidate-id rows, exact-fit success, fail-closed overflow when capacity is too small
- Windows command: `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1413_v1_5_1_collect_k_result_validator_test tests.goal1415_v1_5_1_native_collect_k_zero_capacity_test`
- Windows artifact command: `$env:PYTHONPATH='src;.'; py -3 scripts\goal1416_v1_5_1_collect_k_native_parity.py`
- Linux command: `PYTHONPATH=src:. python3 -m unittest tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1413_v1_5_1_collect_k_result_validator_test tests.goal1415_v1_5_1_native_collect_k_zero_capacity_test && PYTHONPATH=src:. python3 scripts/goal1416_v1_5_1_collect_k_native_parity.py --backend embree --require-backend embree`
- NVIDIA pod command: `RTDL_OPTIX_LIB=/root/work/rtdl_v1_5_1_pod/build/librtdl_optix.so LD_LIBRARY_PATH=/root/work/rtdl_v1_5_1_pod/build:$LD_LIBRARY_PATH PYTHONPATH=src:. python3 -m unittest tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1409_v1_5_1_collect_k_bounded_contract_test tests.goal1413_v1_5_1_collect_k_result_validator_test tests.goal1415_v1_5_1_native_collect_k_zero_capacity_test && PYTHONPATH=src:. python3 scripts/goal1416_v1_5_1_collect_k_native_parity.py --backend optix --require-backend optix`

## Parity Outcome

- Windows focused unit slice: `Ran 24 tests`, `OK`
- Windows artifact: Embree `pass=4, fail=0, skipped=0`; OptiX `pass=0, fail=0, skipped=4` because `librtdl_optix` was not present on Windows
- Linux host `192.168.1.20`: Embree required-backend artifact `ACCEPTED`, Embree `pass=4, fail=0, skipped=0`
- NVIDIA pod `213.173.102.217:25443`, RTX A4500 driver `550.127.05`: OptiX required-backend artifact `ACCEPTED`, OptiX `pass=4, fail=0, skipped=0`
- Required backend skips: none in the Linux Embree required run and none in the NVIDIA pod OptiX required run

## Files

- Harness: `scripts/goal1416_v1_5_1_collect_k_native_parity.py`
- Unit tests: `tests/goal1416_v1_5_1_collect_k_native_parity_test.py`
- Windows generated JSON artifact: `docs/reports/goal1416_v1_5_1_collect_k_native_parity_2026-05-06.json`
- Windows generated Markdown artifact: `docs/reports/goal1416_v1_5_1_collect_k_native_parity_2026-05-06.md`
- Linux Embree generated JSON artifact: `docs/reports/goal1416_v1_5_1_collect_k_native_parity_linux_embree_2026-05-06.json`
- Linux Embree generated Markdown artifact: `docs/reports/goal1416_v1_5_1_collect_k_native_parity_linux_embree_2026-05-06.md`
- NVIDIA pod OptiX generated JSON artifact: `docs/reports/goal1416_v1_5_1_collect_k_native_parity_nvidia_pod_optix_2026-05-06.json`
- NVIDIA pod OptiX generated Markdown artifact: `docs/reports/goal1416_v1_5_1_collect_k_native_parity_nvidia_pod_optix_2026-05-06.md`
- Multi-environment summary: `docs/reports/goal1416_v1_5_1_collect_k_native_parity_multi_env_2026-05-06.md`
