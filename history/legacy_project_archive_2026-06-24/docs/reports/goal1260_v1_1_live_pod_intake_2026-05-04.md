# Goal1260 v1.1 Live Pod Intake

Date: 2026-05-04

Valid: `True`
Public wording authorized: `False`
Release gate authorized: `False`

This report interprets the first live Goal1257 RTX pod run for v1.1 Embree/OptiX
work. It records execution evidence only. Any public wording, release gate,
architecture commitment, or major performance conclusion remains a key goal and
requires 3-AI consensus unless the user explicitly classifies it lower.

## Source And Artifact

- source packet: `docs/reports/goal1257_v1_1_embree_optix_pod_packet_2026-05-04.md`
- source archive: `docs/reports/goal1257_rtdl_source_2026-05-04.tar.gz`
- source archive sha256: `0c455b4190955292bf46cb9ed41e9600ed17132356bc5e7f7cb5e82046211048`
- pod result archive: `docs/reports/goal1257_live_pod_2026-05-04/goal1257_v1_1_embree_optix_pod_results.tgz`
- pod result sha256: `f97f35c5f947aea5f62809379dd0bddaf9043a0a6db04a6e1f19f7e125018dc5`
- extracted results: `docs/reports/goal1257_live_pod_2026-05-04/docs/reports/goal1257_v1_1_embree_optix_pod_results/`

## Pod Environment

- host: `1db59abf42db`
- GPU: NVIDIA RTX A5000, 24564 MiB
- driver: `580.126.09`
- CUDA: `13.0`
- `nvcc`: `/usr/local/cuda/bin/nvcc`, release `13.0`
- Python: `3.12.3`
- OS: Linux `5.15.0-102-generic`
- OptiX headers: `NVIDIA/optix-dev` `v8.0.0`

The first executor attempt stalled on default Ubuntu mirrors. The pod was
reconfigured to use `azure.archive.ubuntu.com`, then the required Embree, GEOS,
Python, CMake, pkg-config, NVRTC, and CUDA development packages were installed.
The successful executor rerun built `build/librtdl_optix.so`.

## Execution Summary

- status count: `17`
- failed count: `3`
- failed labels:
  - `db_embree_100000`
  - `db_optix_100000`
  - `polygon_jaccard_optix_8192`

## Intake Decisions

| App row | Decision | Reason |
| --- | --- | --- |
| `database_analytics` | `partial_same_machine_evidence_only` | 30k passes both backends; 100k fails both backends on explicit `250000` candidate ceiling. |
| `graph_analytics` | `valid_but_total_optix_slower` | Graph visibility passes both 30k and 60k; OptiX kernel is very fast, but total OptiX path is slower than Embree because prepare/pack dominates. |
| `polygon_pair_overlap_area_rows` | `partial_candidate_speedup_at_40000` | 10k OptiX is slower; 40k OptiX is modestly faster than Embree with parity. |
| `polygon_set_jaccard` | `blocked_by_optix_parity_at_8192` | 4096 passes but OptiX is slower; 8192 fails parity. |

## Timing Table

Ratios below are `OptiX / Embree`; values below `1.0` mean OptiX is faster.

| Row | Scale | Embree sec | OptiX sec | Ratio | Correctness |
| --- | ---: | ---: | ---: | ---: | --- |
| DB prepared compact summary, one-shot | 30000 | `11.178304` | `4.525733` | `0.405` | pass |
| DB prepared compact summary, warm query median | 30000 | `0.281665` | `0.360036` | `1.278` | pass |
| Graph visibility, total OptiX path vs Embree query | 30000 | `1.071272` | `1.862499` | `1.739` | pass |
| Graph visibility, total OptiX path vs Embree query | 60000 | `2.178960` | `5.391286` | `2.474` | pass |
| Polygon pair candidate discovery | 10000 | `1.525968` | `2.374388` | `1.556` | pass |
| Polygon pair candidate discovery | 40000 | `6.585602` | `6.033040` | `0.916` | pass |
| Polygon pair total observed pipeline | 10000 | `3.419095` | `4.038887` | `1.181` | pass |
| Polygon pair total observed pipeline | 40000 | `13.020443` | `11.939686` | `0.917` | pass |
| Polygon Jaccard candidate discovery | 4096 | `0.563793` | `1.454789` | `2.580` | pass |
| Polygon Jaccard candidate discovery | 8192 | `0.929184` | `1.729681` | `1.862` | fail |
| Polygon Jaccard total observed pipeline | 4096 | `0.993915` | `2.616353` | `2.632` | pass |
| Polygon Jaccard total observed pipeline | 8192 | `2.017153` | `3.937931` | `1.952` | fail |

## Sub-Path Observations

Graph visibility exposes the core v1.1 performance problem. The OptiX any-hit
kernel itself is extremely fast:

| Scale | Embree query sec | OptiX any-hit kernel sec | Embree / kernel |
| ---: | ---: | ---: | ---: |
| 30000 | `1.071272` | `0.000217` | `4942.5x` |
| 60000 | `2.178960` | `0.000262` | `8320.8x` |

This is not an app-level speedup because the OptiX total path includes scene
prepare, ray prepare, and ray packing. The result supports the v1.5 direction:
remove per-app custom paths and reduce host-side prepare/pack overhead around
general primitives.

## Failure Details

### Database 100000

Both Embree and OptiX fail for the same contract reason:

```text
RuntimeError: first-wave Embree DB lowering exceeded the 250000-candidate ceiling
RuntimeError: first-wave OptiX DB lowering exceeded the 250000-candidate ceiling
```

This is not an OptiX performance failure. It is a current DB lowering/contract
ceiling. What would unblock it: either raise and validate the candidate ceiling,
or redesign the compact-summary lowering to stream/chunk native candidate
processing without violating memory and correctness contracts.

### Polygon Jaccard 8192

The OptiX path fails parity:

```text
cpu intersection_area: 40960
optix intersection_area: 30720
cpu jaccard_similarity: 0.263157894737
optix jaccard_similarity: 0.185185185185
```

The candidate diagnostics also report mismatch:

```text
expected_or_cpu_candidate_row_count: 24576
optix_candidate_row_count: 12288
candidate_count_matches_expected: false
```

What would unblock it: fix OptiX chunked Jaccard candidate coverage at `8192`
copies, then rerun parity before interpreting speed.

## Immediate Next Work

1. Keep the copied pod artifacts as raw evidence.
2. Do not promote public RTX wording from this intake.
3. Locally investigate `polygon_set_jaccard` OptiX chunk coverage at `8192`.
4. Locally inspect DB candidate-ceiling policy and decide whether v1.1 should
   raise, chunk, or explicitly bound the DB scale.
5. If the pod remains available, use it only for targeted reruns after local
   fixes, not broad exploratory work.

## Boundary

This report is a Codex intake of a live pod execution. It is not a release
authorization and does not replace 3-AI consensus for key performance claims.
