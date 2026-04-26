# Goal992 Two-AI Consensus

Date: 2026-04-26

## Goal

Expose public scalar OptiX prepared output modes for outlier detection and DBSCAN while preserving the existing per-point label modes.

## Codex Verdict

ACCEPT.

Codex implemented:

- `examples/rtdl_outlier_detection_app.py`: new `--output-mode density_count` scalar path using `prepared.count_threshold_reached(...)`.
- `examples/rtdl_dbscan_clustering_app.py`: new `--output-mode core_count` scalar path using `prepared.count_threshold_reached(...)`.
- Prepared session APIs now accept `output_mode="density_count"` and `output_mode="core_count"`.
- Existing `density_summary` and `core_flags` modes remain available for per-point labels.
- Docs now distinguish scalar RT-core claim paths from per-point identity/flag modes, including front-page `README.md` and `examples/README.md` wording.

Focused verification:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal757_prepared_optix_fixed_radius_count_test \
  tests.goal695_optix_fixed_radius_summary_test \
  tests.goal741_embree_compact_app_perf_harness_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal700_fixed_radius_summary_public_doc_test \
  tests.goal952_density_native_continuation_test

Ran 45 tests in 0.019s
OK (skipped=2)
```

Additional checks:

```text
python3 -m py_compile \
  examples/rtdl_outlier_detection_app.py \
  examples/rtdl_dbscan_clustering_app.py \
  tests/goal757_prepared_optix_fixed_radius_count_test.py

git diff --check
```

Both checks passed.

Follow-up public-doc gate after front-page wording refresh:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal700_fixed_radius_summary_public_doc_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal958_public_app_native_continuation_schema_test

Ran 16 tests in 0.134s
OK
```

## Gemini Verdict

ACCEPT.

Gemini review file:

- `docs/reports/goal992_gemini_review_2026-04-26.md`

Gemini confirmed that `density_count` and `core_count` use `prepared.count_threshold_reached(...)`, do not call `prepared.run(...)`, preserve the old per-point modes, keep identity/flag boundaries honest, and have adequate tests/docs. After the front-page docs were refreshed, Gemini performed a follow-up review and again accepted with no blockers.

## Consensus

Goal992 is closed with 2-AI consensus.

No public RTX speedup claim is authorized by this goal.
