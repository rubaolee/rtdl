# RTDL v0.1 Reproduction And Verification

Date: 2026-04-05
Status: released

## Purpose

This document gives the shortest reviewer path for understanding and verifying
the RTDL v0.1 package.

## Canonical evidence docs

### Release scope and architecture

- [v0.1 Final Plan](v0_1_final_plan.md)
- [Architecture, API, And Performance Overview](architecture_api_performance_overview.md)
- [Current Milestone Q&A](current_milestone_qa.md)
- [v0.1 Release Notes](v0_1_release_notes.md)
- [Future Ray-Tracing Directions](future_ray_tracing_directions.md)

### Current release validation

- [Goal 100 Release Validation Rerun](reports/goal100_release_validation_rerun_2026-04-05.md)

### Core backend status

- [Goal 84 Exact Source Long Backend Summary](reports/goal84_exact_source_long_backend_summary_2026-04-04.md)
- [Goal 89 Backend Comparison Refresh](reports/goal89_backend_comparison_refresh_2026-04-05.md)

### Oracle trust

- [Goal 75 Oracle Trust Envelope](reports/goal75_oracle_trust_envelope_2026-04-04.md)

### Milestone audit/tests/docs

- [Goal 90 Code Review And Process Audit](reports/goal90_code_review_and_process_audit_2026-04-05.md)
- [Goal 91 Test Expansion For RayJoin Reproduction](reports/goal91_test_expansion_for_rayjoin_reproduction_2026-04-05.md)
- [Goal 92 Architecture API And Performance Docs](reports/goal92_architecture_api_and_performance_docs_2026-04-05.md)

## Canonical artifact summaries

### OptiX

- [Goal 99 OptiX Cold Prepared Run-1 Win Summary](reports/goal99_optix_cold_prepared_run1_win_artifacts_2026-04-05/summary.json)
- [Goal 100 OptiX Raw Summary](reports/goal100_release_validation_rerun_artifacts_2026-04-05/optix_raw/summary.json)

### Embree

- [Goal 83 Embree Prepared Summary](reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/prepared/summary.json)
- [Goal 83 Embree Raw Summary](reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/raw/summary.json)

### Vulkan

- [Goal 87 Vulkan Long Exact Source Summary](reports/goal87_vulkan_long_exact_source_artifacts_2026-04-05/summary.json)
- [Goal 88 Vulkan Long Exact Raw Input Summary](reports/goal88_vulkan_long_exact_raw_input_artifacts_2026-04-05/summary.json)

## Recommended local verification

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal76_runtime_prepared_cache_test \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test \
  tests.goal91_backend_boundary_support_test

PYTHONPATH=src:. python3 -m unittest \
  tests.rtdsl_py_test.RtDslPythonTest.test_rayjoin_cdb_parser_and_views
```

## Recommended Linux verification

```bash
cd /home/lestat/work/rtdl_goal100_clean
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group full
```

```bash
cd /home/lestat/work/rtdl_goal100_clean
PYTHONPATH=src:. python3 -m unittest \
  tests.goal91_backend_boundary_support_test \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test \
  tests.goal76_runtime_prepared_cache_test \
  tests.rtdsl_py_test.RtDslPythonTest.test_rayjoin_cdb_parser_and_views \
  tests.goal99_optix_cold_prepared_run1_win_test
```

```bash
cd /home/lestat/work/rtdl_goal100_clean
make build-vulkan
PYTHONPATH=src:. python3 -m unittest \
  tests.rtdsl_vulkan_test \
  tests.goal71_prepared_backend_positive_hit_county_test \
  tests.goal69_pip_positive_hit_performance_test
```

## Reviewer notes

- timing boundaries must remain separate:
  - prepared
  - repeated raw-input
  - bounded validation
- RayJoin should always be identified explicitly as:
  - Liang Geng, Rubao Lee, and Xiaodong Zhang,
    *RayJoin: Fast and Precise Spatial Join*,
    ICS 2024,
    DOI `10.1145/3650200.3656610`
- the bounded package is the v0.1 trust anchor
- the strongest current performance claim is the long exact-source
  `county_zipcode` positive-hit `pip` surface
- Vulkan is a supported backend, but not a competitive performance backend on
  that surface
