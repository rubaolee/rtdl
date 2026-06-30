# Goal1076 Barnes-Hut Rich RTX Pod Candidate

Date: 2026-04-28

Valid: `true`

Goal1076 prepares a separate Barnes-Hut rich-contract pod candidate. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

## Rows

| App | Path | Phase | Skip validation | Timing floor | Output | Command |
| --- | --- | --- | --- | ---: | --- | --- |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `correctness_validation` | `False` | `` | `docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate/barnes_hut_rich_node_coverage_validation.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 1024 --iterations 3 --radius 0.1 --barnes-tree-depth 6 --hit-threshold 4 --output-json docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate/barnes_hut_rich_node_coverage_validation.json` |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `large_timing_repeat` | `True` | `0.100` | `docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate/barnes_hut_rich_node_coverage_large_timing.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 1000000 --iterations 5 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --skip-validation --output-json docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate/barnes_hut_rich_node_coverage_large_timing.json` |

## Boundary

Goal1076 prepares a separate Barnes-Hut rich-contract pod candidate. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.
