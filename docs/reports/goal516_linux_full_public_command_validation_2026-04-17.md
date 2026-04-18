# Goal 516: Linux Full Public Command Validation

Date: 2026-04-17

Status: accepted with 3-AI consensus

## Scope

Goal516 validates the Goal515 public command truth audit on the primary Linux
host, not just locally on macOS. The goal is to run the refreshed broad
tutorial/example command harness where Embree, OptiX, Vulkan, and PostgreSQL are
available.

## Host

- Host alias: `lestat-lx1`
- Hostname: `lx1`
- Python: `3.12.3`
- PostgreSQL: `16.13`
- PostgreSQL readiness: `/var/run/postgresql:5432 - accepting connections`
- GPU: `NVIDIA GeForce GTX 1070`
- NVIDIA driver: `580.126.09`

## Checkout

Fresh synced checkout:

- `/home/lestat/work/rtdl_goal516_public_command_validation`

The checkout was synced from:

- `/Users/rl2025/rtdl_python_only`
- Source commit before Goal516: `087f76f`

## Backend Bring-Up

Initial probe after fresh sync:

- Oracle: available
- Embree: available
- OptiX: missing RTDL library in the fresh checkout
- Vulkan: missing RTDL library in the fresh checkout

Build commands run on Linux:

```bash
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
```

Post-build runtime probe:

- Oracle: `(0, 1, 0)`
- Embree: `(4, 3, 0)`
- OptiX: `(9, 0, 0)`
- Vulkan: `(0, 1, 0)`

## Public Command Harness Result

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal410_tutorial_example_check.py --machine linux-goal516 --output build/goal516_linux_tutorial_example_check_2026-04-17.json
```

Copied local artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal516_linux_tutorial_example_check_2026-04-17.json`

Result:

- Passed: `73`
- Failed: `0`
- Skipped: `0`
- Total: `73`

Backend status in the harness artifact:

- `cpu_python_reference`: `true`
- `oracle`: `true`
- `cpu`: `true`
- `embree`: `true`
- `optix`: `true`
- `vulkan`: `true`

Note: public commands select the native Oracle runtime with `--backend cpu`.
Goal516 records the same runtime twice in the harness artifact: `oracle` names
the runtime library availability, while `cpu` names the public CLI backend used
by examples.

## PostgreSQL Correctness Gate

Command:

```bash
RTDL_POSTGRESQL_DSN="dbname=postgres" PYTHONPATH=src:. python3 -m unittest \
  tests.goal420_v0_7_rt_db_conjunctive_scan_native_oracle_truth_path_test \
  tests.goal421_v0_7_rt_db_grouped_count_native_oracle_truth_path_test \
  tests.goal422_v0_7_rt_db_grouped_sum_native_oracle_truth_path_test \
  tests.goal423_v0_7_postgresql_db_correctness_test \
  tests.goal424_v0_7_postgresql_db_grouped_correctness_test -v
```

Result:

- Ran: `17` tests
- Result: `OK`

## Current Verdict

Goal516 is accepted. The full public command harness passed on Linux with
Oracle, Embree, OptiX, Vulkan, and PostgreSQL available.

## AI Review Consensus

- Claude review: `PASS`; accepted the Linux host evidence, 73/73 public command
  harness result, backend availability, and 17/17 PostgreSQL correctness gate.
- Gemini Flash review: initially blocked because the harness did not explicitly
  name Oracle in `backend_status`; after the harness artifact was regenerated
  with both `oracle: true` and `cpu: true`, Gemini returned `ACCEPT`.
- Codex conclusion: `ACCEPT`; Goal516 closes the Linux validation pass for the
  public command surface created by Goals 513-515.
