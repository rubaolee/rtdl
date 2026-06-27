# Goal994 v1 RTX Status Generator Scalar Sync

Date: 2026-04-26

## Scope

Fix the generated v1.0 RTX app status source of truth after Goal992/Goal993.
The generated Markdown was already manually correct, but
`scripts/goal947_v1_rtx_app_status_page.py` could still regenerate stale
outlier/DBSCAN command rows without `--output-mode density_count` or
`--output-mode core_count`.

## Changes

- Updated `scripts/goal947_v1_rtx_app_status_page.py` claim commands:
  - Outlier: `--output-mode density_count`
  - DBSCAN: `--output-mode core_count`
- Updated generated DBSCAN subpath wording from `core-threshold` to scalar
  `core-count`.
- Updated generated native-continuation text to distinguish OptiX scalar paths
  from Embree/OptiX per-point summary paths.
- Updated `src/rtdsl/app_support_matrix.py` readiness/maturity text so the
  status generator reports Goal992 and the scalar count boundaries.
- Regenerated:
  - `docs/v1_0_rtx_app_status.md`
  - `docs/reports/goal947_v1_rtx_app_status_page_2026-04-25.json`
  - `docs/reports/goal947_v1_rtx_app_status_2026-04-25.json`
- Updated tests to require the scalar output modes and Goal992 evidence.

## Verification

Commands run:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal958_public_app_native_continuation_schema_test \
  tests.goal700_fixed_radius_summary_public_doc_test \
  tests.goal705_optix_app_benchmark_readiness_test
```

Result: `Ran 25 tests in 0.181s`, `OK`.

Additional checks:

```bash
python3 -m py_compile src/rtdsl/app_support_matrix.py scripts/goal947_v1_rtx_app_status_page.py
git diff --check
rg -n 'core-threshold|Goal795 \|' \
  src/rtdsl/app_support_matrix.py docs/v1_0_rtx_app_status.md \
  docs/app_engine_support_matrix.md docs/application_catalog.md README.md \
  examples/README.md scripts/goal947_v1_rtx_app_status_page.py \
  tests/goal947_v1_rtx_app_status_page_test.py \
  tests/goal705_optix_app_benchmark_readiness_test.py
```

Results: compile passed, `git diff --check` passed, and the stale-wording grep
returned only unrelated robot `Goal795` rows, not outlier/DBSCAN scalar rows.

## Boundary

This goal is a generated-status/docs-source sync only. It does not change
backend kernels and does not authorize public RTX speedup claims.
