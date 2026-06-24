# Goal 464: v0.7 Linux Fresh-Checkout Validation

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Verdict

The current v0.7 DB package was synced to a fresh Linux validation directory,
brought up from source, and validated with DB correctness tests, app demos,
backend probes, PostgreSQL connectivity, fresh performance artifacts, and 2-AI
consensus.

No staging, commit, tag, push, merge, or release action was performed.

## Linux Host And Checkout

- host: `lestat-lx1`
- fresh checkout path: `/home/lestat/work/rtdl_goal464_fresh`
- source sync: rsync from `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
- excluded from sync: `.git/`, `__pycache__/`, `*.pyc`, `build/`, `.venv/`,
  `rtdsl_current.tar.gz`
- PostgreSQL: `PostgreSQL 16.13`
- PostgreSQL readiness: local socket accepting connections
- Python PostgreSQL driver: `psycopg2 ok`
- GPU: `NVIDIA GeForce GTX 1070`, driver `580.126.09`

Hardware caveat: the GTX 1070 has no NVIDIA RT cores. This validation proves
fresh-checkout backend functionality and Linux performance on this machine, but
it is not an RT-core hardware-speedup measurement.

## Fresh-Checkout Bring-Up

Initial runtime probe:

- `rtdsl` import: OK
- Embree: available immediately, version `[4, 3, 0]`
- OptiX: missing fresh-checkout runtime library before build
- Vulkan: missing fresh-checkout runtime library before build

Fresh-checkout backend builds run:

```bash
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
```

Post-build runtime probe:

- Embree version: `[4, 3, 0]`
- OptiX version: `[9, 0, 0]`
- Vulkan version: `[0, 1, 0]`

## Correctness Tests

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal461_v0_7_db_app_demo_test \
  tests.goal462_v0_7_db_kernel_app_demo_test \
  tests.goal423_v0_7_postgresql_db_correctness_test \
  tests.goal424_v0_7_postgresql_db_grouped_correctness_test \
  tests.goal429_v0_7_rt_db_cross_engine_postgresql_correctness_gate_test
```

Result:

- `Ran 13 tests`
- `OK (skipped=2)`

Prepared-dataset and columnar-transfer command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal432_v0_7_rt_db_phase_split_perf_test \
  tests.goal434_v0_7_embree_native_prepared_db_dataset_test \
  tests.goal435_v0_7_optix_native_prepared_db_dataset_test \
  tests.goal436_v0_7_vulkan_native_prepared_db_dataset_test \
  tests.goal440_v0_7_embree_columnar_prepared_db_dataset_transfer_test \
  tests.goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_test \
  tests.goal442_v0_7_vulkan_columnar_prepared_db_dataset_transfer_test \
  tests.goal445_v0_7_high_level_prepared_db_columnar_default_test
```

Result:

- `Ran 29 tests`
- `OK`

## Demo Validation

Commands:

```bash
PYTHONPATH=src:. python3 examples/rtdl_v0_7_db_app_demo.py --backend auto
PYTHONPATH=src:. python3 examples/rtdl_v0_7_db_kernel_app_demo.py --backend auto
```

Results:

- app demo selected backend: `embree`
- kernel-form demo selected backend: `embree`
- both demos returned promo rows `3`, `4`, `5`, `7`

Saved demo outputs:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_linux_fresh_app_demo_output_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_linux_fresh_kernel_demo_output_2026-04-16.json`

## Fresh Performance Artifacts

Saved raw artifacts:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_linux_fresh_columnar_repeated_query_perf_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_linux_fresh_postgresql_index_audit_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_linux_fresh_rtdl_vs_postgresql_rebase_2026-04-16.json`

Configuration:

- rows: `200000`
- repeated queries: `10`
- RTDL transfer mode: `columnar`
- PostgreSQL DSN: `dbname=postgres`

Fresh RTDL columnar repeated-query summary:

| workload | backend | prepare s | median query s | total repeated s | PG setup s | PG median query s | query speedup vs PG | total speedup vs PG | hash |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| conjunctive_scan | embree | 0.983 | 0.0183 | 1.165 | 12.265 | 0.0383 | 2.10x | 10.86x | match |
| conjunctive_scan | optix | 1.134 | 0.0127 | 1.700 | 12.265 | 0.0383 | 3.02x | 7.44x | match |
| conjunctive_scan | vulkan | 1.176 | 0.0141 | 1.659 | 12.265 | 0.0383 | 2.72x | 7.62x | match |
| grouped_count | embree | 0.966 | 0.0160 | 1.125 | 11.159 | 0.0220 | 1.38x | 10.12x | match |
| grouped_count | optix | 0.936 | 0.0053 | 0.989 | 11.159 | 0.0220 | 4.19x | 11.51x | match |
| grouped_count | vulkan | 0.958 | 0.0073 | 1.032 | 11.159 | 0.0220 | 3.00x | 11.03x | match |
| grouped_sum | embree | 0.959 | 0.0333 | 1.296 | 14.251 | 0.0383 | 1.15x | 11.30x | match |
| grouped_sum | optix | 0.938 | 0.0111 | 1.050 | 14.251 | 0.0383 | 3.44x | 13.94x | match |
| grouped_sum | vulkan | 0.933 | 0.0129 | 1.062 | 14.251 | 0.0383 | 2.97x | 13.78x | match |

Fresh PostgreSQL index audit summary:

| workload | best query mode | best total mode | output rows |
|---|---|---|---:|
| conjunctive_scan | composite | covering | 22268 |
| grouped_count | composite | composite | 8 |
| grouped_sum | no_index | composite | 8 |

Goal452 rebase summary against best tested PostgreSQL modes:

| workload | backend | hash match | query speedup | total speedup |
|---|---|---|---:|---:|
| conjunctive_scan | embree | true | 0.98x | 8.61x |
| conjunctive_scan | optix | true | 1.44x | 5.88x |
| conjunctive_scan | vulkan | true | 1.20x | 6.19x |
| grouped_count | embree | true | 0.92x | 9.04x |
| grouped_count | optix | true | 2.71x | 10.25x |
| grouped_count | vulkan | true | 1.82x | 9.91x |
| grouped_sum | embree | true | 1.02x | 7.84x |
| grouped_sum | optix | true | 3.08x | 9.84x |
| grouped_sum | vulkan | true | 2.53x | 9.53x |

## Interpretation

The strongest claim supported by this fresh Linux run is:

- v0.7 DB examples and focused correctness tests run from a fresh synced
  checkout on Linux after building missing backend libraries
- Embree, OptiX, and Vulkan backend runtime probes succeed
- RTDL/PostgreSQL output hashes match for the measured workloads
- RTDL prepared columnar repeated-query total time is materially faster than
  PostgreSQL setup plus repeated-query time on this bounded benchmark

The report does not claim:

- arbitrary SQL support
- DBMS functionality
- exhaustive PostgreSQL tuning
- RT-core hardware acceleration on this GTX 1070 machine

## Release Boundary

- staging performed: `false`
- release authorization: `false`
- git index staged path count after validation: `0`
- do not stage until the user explicitly approves
- do not merge to main
- do not tag or release

## External Review

External review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_external_review_2026-04-16.md`

Verdict: ACCEPT.

Consensus record:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal464-v0_7-linux-fresh-checkout-validation.md`
