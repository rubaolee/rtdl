# Goal 36 Linux BlockGroup/WaterBodies Embree Performance

Date: 2026-04-02

## Scope

Goal 36 closed the first serious Linux-host Embree performance characterization round for:

- `BlockGroup ⊲⊳ WaterBodies`

This round intentionally stayed within the exact-source regional boundary already established in Goal 35. It did not attempt nationwide execution. Instead, it built a deterministic ladder by scaling the accepted nontrivial `county2300_bbox` seed region around its center.

## Host

- host: `192.168.1.20`
- OS: Ubuntu 24.04.4 LTS
- CPU: Intel Core i7-7700HQ
- threads: `8`
- memory: about `15 GiB`

## Frozen Ladder

Seed bbox:

- `county2300_bbox`
- `-76.701624,40.495434,-75.757807,40.9497400000001`

Scale factors:

- `0.4`
- `0.5`
- `0.6`
- `0.75`
- `1.0`

Each point is the exact-source bbox obtained by scaling that seed bbox around its center. The harness stages fresh `BlockGroup` and `WaterBodies` pages for each bbox from their live ArcGIS FeatureServer sources, converts them into RTDL logical inputs, then runs both:

- `lsi`
- `pip`

## Runtime Policy

- warmup: `0`
- measured iterations: `1`

This single-pass policy is intentional. On this family, the Python `lsi` oracle already reaches minute-scale cost at the top accepted point, so repeated medians would mostly measure oracle overhead rather than expand the fidelity of the Embree comparison.

## Accepted Points

| Slice | BlockGroup Features | WaterBodies Features | LSI Rows | LSI CPU (s) | LSI Embree (s) | LSI Speedup | PIP Rows | PIP CPU (s) | PIP Embree (s) | PIP Speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `county2300_s04` | `96` | `45` | `8` | `2.325437246` | `0.046488825` | `50.02x` | `4500` | `0.091677384` | `0.016238999` | `5.65x` |
| `county2300_s05` | `118` | `69` | `32` | `5.086650727` | `0.051493691` | `98.78x` | `8487` | `0.183986502` | `0.031371276` | `5.86x` |
| `county2300_s06` | `144` | `88` | `50` | `9.647115205` | `0.069580206` | `138.65x` | `13112` | `0.321222311` | `0.039360554` | `8.16x` |
| `county2300_s075` | `204` | `112` | `79` | `21.660184394` | `0.115359390` | `187.76x` | `24054` | `0.674625069` | `0.073795956` | `9.14x` |
| `county2300_s10` | `279` | `172` | `216` | `139.643181975` | `0.220374381` | `633.66x` | `71176` | `2.215563682` | `0.191312597` | `11.58x` |

## Parity

All five attempted points were parity-clean:

- `lsi`: CPU rows matched Embree rows at every accepted point
- `pip`: CPU rows matched Embree rows at every accepted point
- rejected points: none

## Interpretation

The important result is not just that Embree is faster than the Python oracle. It is that the exact-source `BlockGroup ⊲⊳ WaterBodies` family now behaves coherently across a bounded increasing regional ladder on the Linux host:

- feature counts grow monotonically with the frozen scale factor
- both workloads remain parity-clean across the whole ladder
- `lsi` shows especially large speedups because the Python oracle cost grows quickly with exact-source segment complexity
- `pip` speedups are smaller but still clear and stable

This is the first serious host-backed performance characterization for this family on the current local Embree backend.

## Boundary

Goal 36 does **not** claim:

- nationwide `BlockGroup ⊲⊳ WaterBodies` execution
- full paper-family closure for this dataset pair
- GPU/OptiX equivalence to the original RayJoin environment

The honest closure statement is:

- RTDL now has a parity-clean Linux-host Embree performance ladder for exact-source regional `BlockGroup ⊲⊳ WaterBodies`
- the ladder is deterministic and host-backed
- it materially extends Goal 35 from a single slice into a serious bounded characterization round
