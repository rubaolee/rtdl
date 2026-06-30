# RTDL v0.9.4 Release-Level Call For Test

Date: 2026-04-19

Repository under test:

`/Users/rl2025/rtdl_python_only`

Released tag:

`v0.9.4`

GitHub repository:

`https://github.com/rubaolee/rtdl`

## Request

Please perform an independent release-level test of RTDL `v0.9.4` from a fresh
checkout or clean worktree, then write a tester report with a clear `ACCEPT` or
`BLOCK` verdict.

This is not a request to approve new features. It is a release validation
request for the already-tagged `v0.9.4` boundary.

## Main Questions

Please answer these questions directly:

1. Can a new user follow the public docs and run the portable examples without
   hidden local assumptions?
2. Do the advertised RTDL workload families run correctly on the available
   platform/backend set?
3. Are the v0.9.4 backend claims honest, especially for Apple RT, HIPRT,
   OptiX, Vulkan, and Embree?
4. Are there stale docs, stale version statements, dead commands, missing setup
   steps, or misleading performance claims?
5. Is there any code, documentation, or release-flow issue serious enough to
   block the `v0.9.4` release record?

## Required Documents To Inspect

Start with these exact files:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_4/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_4/release_statement.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_4/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_4/audit_report.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_4/tag_preparation.md`

## Existing Release-Gate Evidence To Compare Against

Use these as internal evidence, not as a substitute for your own testing:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal625_v0_9_4_total_test_doc_audit_gate_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal625_external_consensus_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal625_claude_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal625_gemini_flash_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal625_v0_9_4_local_full_unittest_goal_pattern_2026-04-19.txt`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal625_v0_9_4_linux_backend_gate_2026-04-19.txt`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal625_v0_9_4_public_entry_smoke_2026-04-19.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal515_public_command_truth_audit_2026-04-17.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal515_public_command_truth_audit_2026-04-17.md`

## Minimum Portable Test

Run this on any supported OS with Python `3.10+`:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

If testing from a fresh Git checkout instead of this exact path, replace
`/Users/rl2025/rtdl_python_only` with the checkout root and record the commit
hash and tag checkout status.

## Optional Native Backend Tests

Run only what your platform supports. Record skipped backends as skips, not
failures, if the dependency is absent.

### macOS Apple Silicon

```bash
cd /Users/rl2025/rtdl_python_only
make build-apple-rt
PYTHONPATH=src:. python3 examples/rtdl_apple_rt_closest_hit.py
PYTHONPATH=src:. python3 -m unittest tests.goal582_apple_rt_full_surface_dispatch_test -v
PYTHONPATH=src:. python3 -m unittest tests.goal617_apple_rt_db_conjunctive_scan_test tests.goal618_apple_rt_db_grouped_aggregation_test tests.goal619_apple_rt_graph_bfs_test tests.goal620_apple_rt_graph_triangle_match_test -v
```

### Linux With NVIDIA GPU

Adjust dependency prefixes if your local installation differs:

```bash
cd /Users/rl2025/rtdl_python_only
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 -m unittest tests.goal176_linux_gpu_backend_regression_test tests.goal216_fixed_radius_neighbors_optix_test tests.goal218_fixed_radius_neighbors_vulkan_test tests.goal540_hiprt_probe_test tests.goal547_hiprt_correctness_matrix_test tests.goal559_hiprt_db_workloads_test -v
```

### PostgreSQL DB Baseline On Linux

If PostgreSQL is installed and accepting local connections:

```bash
psql --version
pg_isready
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal452_v0_7_db_best_tested_postgresql_comparison_test -v
```

If this exact test name differs in your checkout, search for PostgreSQL tests
and report what you ran:

```bash
cd /Users/rl2025/rtdl_python_only
rg -n "PostgreSQL|postgres|psql|pg_isready" tests docs scripts
```

## Honesty Boundaries To Check

The release must not claim:

- Apple DB or graph workloads are accelerated by Apple ray-tracing hardware.
- Apple RT is broadly faster than Embree.
- HIPRT has AMD GPU validation in this release.
- HIPRT has a CPU fallback.
- GTX 1070 evidence proves RT-core speedups.
- RTDL is a DBMS, renderer, ANN system, graph database, or general application
  framework.
- `v0.9.2` or `v0.9.3` were public releases.

The release may claim:

- `v0.9.4` is the current public release.
- `v0.9.4` absorbs internal untagged `v0.9.2` and `v0.9.3` Apple evidence.
- HIPRT and Apple RT are real bounded RTDL backend families.
- Apple `run_apple_rt` has explicit support-matrix entries for all current
  predicates.
- Apple MPS RT covers the supported geometry and nearest-neighbor slices.
- Apple Metal compute/native-assisted execution covers bounded DB and graph
  slices.
- Embree remains the mature optimized baseline.

## Requested Tester Report Format

Please write a Markdown report with these sections:

1. `Verdict`: `ACCEPT` or `BLOCK`.
2. `Environment`: OS, CPU, GPU, Python, compiler, CUDA/Vulkan/OptiX/HIPRT,
   Apple Metal/MPS, Embree, PostgreSQL as applicable.
3. `Checkout`: repository path, commit hash, tag status, dirty/clean status.
4. `Commands Run`: exact commands and whether each passed, failed, or skipped.
5. `Correctness Findings`: any wrong results, crashes, nondeterminism, or
   backend parity failures.
6. `Documentation Findings`: stale docs, dead commands, missing setup steps, or
   unclear user-facing claims.
7. `Performance Findings`: only measured results; do not infer speedup without
   evidence.
8. `Release-Flow Findings`: tag, history, report, or evidence-chain issues.
9. `Blockers`: exact file path, line number if possible, reproduction steps,
   expected behavior, actual behavior, and severity.
10. `Non-Blocking Notes`: useful improvements that should not block `v0.9.4`.

If writing into this repository, use this preferred output path:

`/Users/rl2025/rtdl_python_only/docs/reports/external_v0_9_4_release_level_test_report_2026-04-19.md`

## Single-Sentence Summary For Reviewer

Please independently test RTDL `v0.9.4` from the public docs and release-gate
evidence, then write an `ACCEPT` or `BLOCK` report identifying any code,
documentation, performance-claim, or release-flow issue that should affect the
release record.
