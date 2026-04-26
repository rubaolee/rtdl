# Goal995 Public RTX Fixed-Radius Stale Wording Audit

Date: 2026-04-26

## Scope

Audit current release-facing docs, current scripts, and current tests for stale
fixed-radius RTX wording after the scalar public modes were introduced:

- Outlier claim-facing mode: `--output-mode density_count`
- DBSCAN claim-facing mode: `--output-mode core_count`

Historical cloud artifacts and archived reports were intentionally excluded
from the remediation scope because they preserve what was generated at the time
of older runs.

## Changes

- Tightened public-doc tests so they require the full scalar command shapes:
  - `--backend optix --optix-summary-mode rt_count_threshold_prepared --output-mode density_count`
  - `--backend optix --optix-summary-mode rt_core_flags_prepared --output-mode core_count`
- Updated the optional SciPy DBSCAN baseline note from stale
  `core-threshold` wording to `scalar core-count` wording.

## Verification

Commands run:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal976_optional_scipy_baselines_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal700_fixed_radius_summary_public_doc_test
```

Result: `Ran 24 tests in 0.261s`, `OK`.

Additional checks:

```bash
python3 -m py_compile scripts/goal976_optional_scipy_baselines.py
git diff --check
rg --pcre2 -n "core-threshold|prepared fixed-radius threshold summary|prepared fixed-radius core-flag|density summary traversal|core-flag summary traversal|--backend optix --optix-summary-mode rt_count_threshold_prepared(?! --output-mode density_count)|--backend optix --optix-summary-mode rt_core_flags_prepared(?! --output-mode core_count)" \
  README.md docs/README.md docs/application_catalog.md \
  docs/app_engine_support_matrix.md docs/release_facing_examples.md \
  docs/rtdl_feature_guide.md docs/tutorials examples/README.md \
  scripts src/rtdsl tests
```

Results: compile passed, `git diff --check` passed, and the stale-current-surface
grep returned no matches.

## Boundary

This goal is a current-surface wording/test audit only. It does not rewrite
historical cloud artifacts, does not change backend kernels, and does not
authorize public RTX speedup claims.
