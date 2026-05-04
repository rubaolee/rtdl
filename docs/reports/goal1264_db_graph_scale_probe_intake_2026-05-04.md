# Goal1264 DB/Graph Scale Probe Intake

Date: 2026-05-04

Valid: `True`
Public wording authorized: `False`
Release gate authorized: `False`

This report records a small follow-up RTX A5000 pod probe after Goal1263. Its
purpose was to test whether larger scale changes the v1.1 interpretation for
`database_analytics` and `graph_analytics`.

## Artifact

- archive: `docs/reports/goal1264_db_graph_scale_probe_2026-05-04/goal1264_db_graph_scale_probe.tgz`
- sha256: `889ab909d936ffaeff4c1eba16949a4797a20167dc42da9116dfb8bab994b507`
- extracted directory: `docs/reports/goal1264_db_graph_scale_probe_2026-05-04/goal1264_db_graph_scale_probe/`
- pod GPU: NVIDIA RTX A5000
- driver: `580.126.09`
- CUDA: `13.0`

An initial DB `scenario=all --copies 300000` attempt failed before artifact
archive creation because the unified DB scenario still exceeded the native
`1000000` row-per-RT-job contract. The retained probe therefore uses the
narrower `sales_risk` compact-summary scenario at 300k copies.

## Results

Ratios are `OptiX / Embree`; values below `1.0` mean OptiX is faster.

### DB Sales Risk 300k

| Phase | Embree sec | OptiX sec | Ratio |
| --- | ---: | ---: | ---: |
| one-shot total | `15.580044` | `13.427887` | `0.862` |
| prepared-session prepare total | `13.613990` | `9.668694` | `0.710` |
| warm query median | `1.405388` | `1.538033` | `1.094` |

Interpretation:

- The narrower DB compact-summary path scales beyond 100k and remains
  execution-unblocked.
- OptiX improves one-shot and prepare time at 300k.
- Warm-query median still favors Embree, so DB remains mixed evidence and not
  public-speedup-ready.
- The failed `scenario=all` 300k attempt confirms the DB contract still needs
  either stricter scale boundaries or true streaming/chunked native processing
  before broader DB wording.

### Graph Visibility 120k

| Phase | Embree sec | OptiX sec | Ratio |
| --- | ---: | ---: | ---: |
| Embree query vs OptiX visibility record total | `3.945987` | `4.951439` | `1.255` |
| OptiX any-hit query kernel | n/a | `0.000386` | n/a |

OptiX visibility record phase split:

| Phase | Sec |
| --- | ---: |
| input construction | `1.437959` |
| scene prepare | `0.694626` |
| ray prepare | `1.064284` |
| ray pack | `1.612400` |
| query any-hit count | `0.000386` |

Interpretation:

- The RT any-hit kernel remains extremely fast.
- Total OptiX path is still slower than Embree at 120k because input/scene/ray
  preparation and packing dominate.
- This reinforces the v1.5 architecture direction: reduce host-side prepare and
  pack overhead around generic primitives instead of claiming graph speedup now.

## Decision

- `database_analytics`: `scale_extended_but_still_mixed`
- `graph_analytics`: `larger_scale_still_total_path_slower`

No new public wording is authorized.

## Next Work

1. Keep polygon-pair as the only currently accepted bounded positive v1.1
   OptiX performance candidate.
2. Treat DB streaming/chunked processing and graph prepare/pack reduction as
   v1.2/v1.5 engineering inputs.
3. Do not spend more pod time on broad DB/graph sweeps until local design work
   changes the expected bottleneck.

## Boundary

This is Codex intake of a diagnostic pod probe. It is not 3-AI consensus and
does not authorize public speedup wording.
