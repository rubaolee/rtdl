# RTDL v0.1 Reproduction And Verification

Date: 2026-04-05
Status: release candidate

## Purpose

This document gives the shortest reviewer path for understanding and verifying
the RTDL v0.1 package.

## Canonical evidence docs

### Release scope and architecture

- `/Users/rl2025/rtdl_python_only/docs/v0_1_final_plan.md`
- `/Users/rl2025/rtdl_python_only/docs/architecture_api_performance_overview.md`
- `/Users/rl2025/rtdl_python_only/docs/current_milestone_qa.md`

### Core backend status

- `/Users/rl2025/rtdl_python_only/docs/reports/goal84_exact_source_long_backend_summary_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal89_backend_comparison_refresh_2026-04-05.md`

### Oracle trust

- `/Users/rl2025/rtdl_python_only/docs/reports/goal75_oracle_trust_envelope_2026-04-04.md`

### Milestone audit/tests/docs

- `/Users/rl2025/rtdl_python_only/docs/reports/goal90_code_review_and_process_audit_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal91_test_expansion_for_rayjoin_reproduction_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal92_architecture_api_and_performance_docs_2026-04-05.md`

## Canonical artifact summaries

### OptiX

- `/Users/rl2025/rtdl_python_only/docs/reports/goal82_optix_pre_embree_audit_artifacts_2026-04-04/prepared/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal81_optix_long_exact_raw_input_win_artifacts_2026-04-04/optix/summary.json`

### Embree

- `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/prepared/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/raw/summary.json`

### Vulkan

- `/Users/rl2025/rtdl_python_only/docs/reports/goal87_vulkan_long_exact_source_artifacts_2026-04-05/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal88_vulkan_long_exact_raw_input_artifacts_2026-04-05/summary.json`

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
cd /home/lestat/work/rtdl_goal94_clean
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group full
```

```bash
cd /home/lestat/work/rtdl_goal94_clean
PYTHONPATH=src:. python3 -m unittest \
  tests.goal91_backend_boundary_support_test \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test \
  tests.goal76_runtime_prepared_cache_test \
  tests.rtdsl_py_test.RtDslPythonTest.test_rayjoin_cdb_parser_and_views
```

```bash
cd /home/lestat/work/rtdl_goal94_clean
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
- the bounded package is the v0.1 trust anchor
- the strongest current performance claim is the long exact-source
  `county_zipcode` positive-hit `pip` surface
- Vulkan is a supported backend, but not a competitive performance backend on
  that surface
