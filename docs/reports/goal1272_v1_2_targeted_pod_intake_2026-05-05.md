# Goal1272 v1.2 Targeted Pod Intake

Date: 2026-05-05

Valid: `True`
Public wording authorized: `False`
Environment status: `env_probe_ok`
Build status: `build_ok`
Execution status: `artifact_complete`

Goal1272 intakes copied Goal1267 v1.2 pod artifacts only. It does not run cloud work and does not authorize public RTX speedup wording.
Any public wording, release gate, architecture commitment, or major performance conclusion remains a key-goal decision and requires 3-AI consensus unless the user explicitly classifies it lower.

## Status

- failed count: `0`
- missing artifacts: `0`

## Environment

| OS | Package manager | CUDA prefix | NVCC | OptiX prefix | OptiX header |
| --- | --- | --- | --- | --- | --- |
| `ubuntu` | `apt-get` | `/usr/local/cuda` | `/usr/local/cuda/bin/nvcc` | `/root/vendor/optix-dev` | `True` |

## Decisions

- `graph_analytics`: `optix_improved`
- `graph_prepared_repeat`: `optix_improved`
- `database_analytics`: `optix_improved`
- `polygon_pair_overlap_area_rows`: `optix_improved`
- `polygon_set_jaccard`: `optix_still_slower_with_reason`

## Graph

| Copies | Embree sec | OptiX total | Repeat mean | Total ratio | Repeat ratio |
| ---: | ---: | ---: | ---: | ---: | ---: |
| `30000` | `8.79577` | `1.27866` | `7.22098e-05` | `6.87889` | `121809` |
| `60000` | `2.79877` | `0.993101` | `0.000100736` | `2.81821` | `27783.2` |

## Database

| Copies | Embree warm | OptiX warm | Ratio | OptiX native counters |
| ---: | ---: | ---: | ---: | --- |
| `100000` | `0.636918` | `0.421495` | `1.51109` | `exported` |
| `300000` | `1.75629` | `1.26793` | `1.38517` | `exported` |

## Polygon Pair

| Copies | Ratio | Parity | Positive-pair parity | Candidate delta |
| ---: | ---: | --- | --- | ---: |
| `40000` | `2.20819` | `True` | `True` | `-40000` |
| `80000` | `1.97513` | `True` | `True` | `-80000` |
| `160000` | `2.12326` | `True` | `True` | `-160000` |

## Jaccard

| Copies | Chunk | Safe | Ratio | Positive-pair parity |
| ---: | ---: | --- | ---: | --- |
| `4096` | `1024` | `True` | `0.740851` | `True` |
| `8192` | `1024` | `True` | `0.820336` | `True` |

## Boundary

This intake does not authorize public RTX speedup wording.
Any public wording or major performance conclusion requires a separate reviewed packet and 3-AI consensus.
