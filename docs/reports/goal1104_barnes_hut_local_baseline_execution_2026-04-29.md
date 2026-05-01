# Goal1104 Barnes-Hut Local Baseline Execution

Date: 2026-04-29

## Scope

Goal1104 executes the single local baseline row that Goal1103 marked safe on the current 16 GB Mac:

- `barnes_hut_force_app / node_coverage_prepared_rich`
- backend: `embree`
- body count: `4096`
- tree depth: `8`
- radius: `0.1`
- hit threshold: `4`

## Command

```bash
RTDL_SOURCE_COMMIT=$(git rev-parse HEAD) PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py --scenario barnes_hut_node_coverage --backend embree --body-count 4096 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --output-json docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_4096_embree_validation_baseline.json
PYTHONPATH=src:. python3 scripts/goal1102_current_contract_baseline_intake.py
```

## Result

| Field | Value |
| --- | --- |
| Artifact | `docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_4096_embree_validation_baseline.json` |
| `matches_oracle` | `true` |
| `query_count` | `4096` |
| `node_count` | `65536` |
| `barnes_tree_depth` | `8` |
| `hit_threshold` | `4` |
| `source_commit` | `c500a63fe36efaeac994159e8c37f72797398d85` |
| `native_query_sec.median_sec` | `0.00486608303617686` |

The command sets `RTDL_SOURCE_COMMIT` explicitly because the local untracked `.rtdl_source_commit` file can be stale after pod copyback. The artifact source commit matches the current `HEAD` at execution time.

Follow-up source-stamping hardening was applied after this discovery:

- `scripts/goal887_prepared_decision_phase_profiler.py` now prefers `RTDL_SOURCE_COMMIT`, then `git rev-parse HEAD`, then `.rtdl_source_commit` only as a fallback for archive-style pod checkouts.
- `scripts/goal1101_current_contract_non_optix_baseline_profiler.py` uses the same order.
- the Goal1084, Goal1093, and Goal1101 runner scripts export `RTDL_SOURCE_COMMIT` with the same git-first fallback order.

After rerunning Goal1102 intake:

- `ok_count: 1`
- `missing_count: 3`
- `blocked_count: 0`
- `overall_status: waiting_for_baseline_artifacts`
- `public_speedup_claim_authorized_count: 0`

## Remaining Rows

The three remaining Goal1102 rows are intentionally still missing:

- Facility recentered CPU oracle baseline;
- Facility recentered Embree baseline;
- Barnes-Hut depth-8 20M Embree timing baseline.

These rows were not run on this 16 GB Mac because Goal1103 classifies them as high or very high risk for local execution.

## Boundary

Goal1104 records one local non-OptiX baseline artifact. It does not authorize public RTX speedup claims. The baseline set remains incomplete and not ready for public wording review.
