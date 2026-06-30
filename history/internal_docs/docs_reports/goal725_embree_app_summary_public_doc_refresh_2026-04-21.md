# Goal725 Embree App Summary Public Doc Refresh

Date: 2026-04-21

## Scope

This goal refreshes public-facing documentation after the recent Embree app
optimization work:

- `README.md`
- `examples/README.md`
- `docs/application_catalog.md`
- `scripts/goal410_tutorial_example_check.py`
- regenerated Goal515 public-command audit artifacts

## Changes

- Documented bounded Embree summary modes for selected apps:
  - Hausdorff: `--embree-result-mode directed_summary`
  - Event hotspot screening: `--embree-summary-mode count_summary`
  - Service coverage gaps: `--embree-summary-mode gap_summary`
- Preserved the existing OptiX summary-mode wording for outlier detection and
  DBSCAN so public tests continue to protect the original honesty boundary.
- Added Goal410 harness coverage for the public Embree polygon commands:
  - `python examples/rtdl_polygon_pair_overlap_area_rows.py --backend embree`
  - `python examples/rtdl_polygon_set_jaccard.py --backend embree`
- Regenerated Goal515 command audit artifacts. The current audit reports:
  - valid: `true`
  - public docs scanned: `14`
  - runnable public commands found: `248`
  - uncovered commands: `0`

## Boundaries

- The new Embree summary modes are app-output-specific compact modes, not
  replacements for row modes.
- Service coverage `gap_summary` intentionally omits clinic ids, distances, and
  clinic-load counts.
- Event hotspot `count_summary` intentionally omits neighbor-pair rows and
  distances.
- Hausdorff `directed_summary` intentionally omits full KNN rows.
- No universal Embree speedup claim is introduced here; performance claims
  remain bounded to the individual Goal722, Goal723, and Goal724 reports.

## Verification

Commands run from `/Users/rl2025/rtdl_python_only`:

```bash
git diff --check
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal512_public_doc_smoke_audit_test \
  tests.goal686_app_catalog_cleanup_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal700_fixed_radius_summary_public_doc_test \
  tests.goal724_service_coverage_embree_summary_test \
  tests.goal723_event_hotspot_embree_summary_test \
  tests.goal722_embree_hausdorff_summary_test \
  tests.goal720_embree_prepared_knn_rows_test \
  tests.goal718_embree_prepared_app_modes_test \
  tests.goal515_public_command_truth_audit_test
```

Results:

- `git diff --check`: pass
- Goal515 script: `valid: true`, `command_count: 248`
- Focused unittest set: `28` tests passed

## Verdict

ACCEPT. Public docs are consistent with the recent Embree app optimization
work, and the public command audit has no uncovered commands.
