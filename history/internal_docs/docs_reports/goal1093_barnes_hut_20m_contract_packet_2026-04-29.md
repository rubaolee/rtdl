# Goal1093 Barnes-Hut 20M Contract Packet

Date: 2026-04-29

Valid: `true`

Goal1093 prepares a superseding Barnes-Hut contract packet only. It does not run cloud, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.

## Rows

| Phase | Bodies | Nodes | Depth | Threshold | Skip validation | Timing floor | Command |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| `depth8_contract_validation` | `4096` | `65536` | `8` | `4` | `False` | `` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 4096 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --output-json docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_4096_validation.json` |
| `depth8_20m_timing_repeat` | `20000000` | `65536` | `8` | `4` | `True` | `0.100` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 20000000 --iterations 5 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --skip-validation --output-json docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_20m_timing.json` |

## Boundary

Goal1093 prepares a superseding Barnes-Hut contract packet only. It does not run cloud, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.
