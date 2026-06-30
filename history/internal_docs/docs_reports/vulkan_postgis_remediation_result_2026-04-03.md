# Vulkan And PostGIS Remediation Result

Date: 2026-04-03
Status: complete

## What this round did

- reviewed the unexpected Vulkan backend integration commits that landed after `0b3075b`
- decided to keep Vulkan on `main`, but only as a provisional backend
- found and terminated an invalid remote PostGIS run on `192.168.1.20`
- corrected the project surface so Vulkan status and Goal 50 PostGIS query mode are represented accurately

## Accepted Vulkan changes

- added checked arithmetic and a `512 MiB` output guardrail in:
  - `src/native/rtdl_vulkan.cpp`
- expanded committed Vulkan parity coverage in:
  - `tests/rtdsl_vulkan_test.py`
- downgraded the strongest Vulkan readiness wording in:
  - `docs/goal_51_vulkan_parity_validation.md`
  - `docs/reports/Consensus_Vulkan_Backend_Review_2026-04-02.md`

## Accepted Goal 50 changes

- extracted SQL builders in:
  - `scripts/goal50_postgis_ground_truth.py`
- added direct SQL-shape assertions in:
  - `tests/goal50_postgis_ground_truth_test.py`
- corrected Goal 50 documentation in:
  - `docs/goal_50_postgis_ground_truth.md`
  - `docs/reports/goal50_postgis_ground_truth_2026-04-02.md`

## Remote Linux decision

The live PostGIS `lsi` query observed on `192.168.1.20` did not use the required `geom &&` GiST-index-assisted predicate. That run was terminated and must not be used for correctness or performance conclusions.

## Verification

- `python3 -m py_compile src/rtdsl/vulkan_runtime.py scripts/goal50_postgis_ground_truth.py tests/rtdsl_vulkan_test.py tests/goal50_postgis_ground_truth_test.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal50_postgis_ground_truth_test tests.rtdsl_vulkan_test`
  - result: `OK (skipped=1)`

## Consensus

- Gemini reviewed the draft decision and the final patch and approved both
- Claude reviewed the final patch and approved it
- Codex reviewed both external reviews and accepts the remediation result
