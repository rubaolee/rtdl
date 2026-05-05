# Goal1272 v1.2 Targeted Pod Intake

Date: 2026-05-05

Valid: `False`
Public wording authorized: `False`
Environment status: `env_probe_missing`
Build status: `build_ok`
Execution status: `environment_blocked`

Goal1272 intakes copied Goal1267 v1.2 pod artifacts only. It does not run cloud work and does not authorize public RTX speedup wording.
Any public wording, release gate, architecture commitment, or major performance conclusion remains a key-goal decision and requires 3-AI consensus unless the user explicitly classifies it lower.

## Status

- failed count: `9`
- missing artifacts: `5`

## Environment

| OS | Package manager | CUDA prefix | NVCC | OptiX prefix | OptiX header |
| --- | --- | --- | --- | --- | --- |
| `None` | `None` | `None` | `None` | `None` | `None` |

## Decisions

- `graph_analytics`: `baseline_contract_incomplete`
- `graph_prepared_repeat`: `baseline_contract_incomplete`
- `database_analytics`: `baseline_contract_incomplete`
- `polygon_pair_overlap_area_rows`: `baseline_contract_incomplete`
- `polygon_set_jaccard`: `baseline_contract_incomplete`

## Graph

| Copies | Embree sec | OptiX total | Repeat mean | Total ratio | Repeat ratio |
| ---: | ---: | ---: | ---: | ---: | ---: |
| `30000` | `n/a` | `1.61979` | `n/a` | `n/a` | `n/a` |
| `60000` | `n/a` | `1.41444` | `n/a` | `n/a` | `n/a` |

## Database

| Copies | Embree warm | OptiX warm | Ratio | OptiX native counters |
| ---: | ---: | ---: | ---: | --- |
| `100000` | `n/a` | `0.508756` | `n/a` | `exported` |
| `300000` | `n/a` | `1.50224` | `n/a` | `exported` |

## Polygon Pair

| Copies | Ratio | Parity | Positive-pair parity | Candidate delta |
| ---: | ---: | --- | --- | ---: |
| `40000` | `n/a` | `True` | `None` | `n/a` |
| `80000` | `n/a` | `True` | `None` | `n/a` |
| `160000` | `n/a` | `True` | `None` | `n/a` |

## Jaccard

| Copies | Chunk | Safe | Ratio | Positive-pair parity |
| ---: | ---: | --- | ---: | --- |
| `4096` | `1024` | `True` | `n/a` | `None` |
| `8192` | `1024` | `True` | `n/a` | `None` |

## Boundary

This intake does not authorize public RTX speedup wording.
Any public wording or major performance conclusion requires a separate reviewed packet and 3-AI consensus.
