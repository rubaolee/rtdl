# Goal4466 V3.0 M70 Triangle Ray-Batch Cap Tuning

Goal4466 tunes the `segment-max-two-hop-rows` cap for the Triangle Counting
segmented-scene RT-2A1 route on `com-orkut`.

The purpose is narrow: reduce duplicate-ray batch overhead without crossing the
GPU memory boundary. This is not a new default and not a public speedup claim.

## Planner Sweep

Planner-only sweep, fixed `--scene-max-directed-edges 2000000`:

| Ray cap | Planned ray segments | Planner time |
| ---: | ---: | ---: |
| 5,000,000 | 1,744 | 4.027s |
| 10,000,000 | 885 | 3.712s |
| 20,000,000 | 456 | 3.631s |
| 40,000,000 | 246 | 3.645s |
| 80,000,000 | 147 | 3.958s |

The planner can describe larger batches, but that does not mean the runtime can
execute them safely. The memory boundary appears during ray query execution.

## Full Probes

All successful full probes used warmup 0 and repeat 1 on the RTX 4000 Ada pod.

| Ray cap | Status | Ray segments | Total | Ray build | RT query | Count |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 5,000,000 | ok | 1,744 | 35.409s | 6.725s | 19.032s | 627,584,181 |
| 10,000,000 | ok | 885 | 35.077s | 6.009s | 19.139s | 627,584,181 |
| 15,000,000 | ok | 600 | 34.231s | 5.629s | 19.153s | 627,584,181 |
| 18,000,000 | failed | n/a | n/a | n/a | n/a | CUDA OOM during query |
| 20,000,000 | failed | n/a | n/a | n/a | n/a | CUDA OOM during query |

The useful finding is bounded: 15M is the best measured explicit cap for this
pod and dataset, reducing the full probe by about `1.178s` versus the 5M M69
probe. Larger caps are not safe on this hardware. Therefore the conservative
default remains smaller, while `15,000,000` becomes a documented RTX 4000 Ada
`com-orkut` tuning value.
It is not a universal default.

## Interpretation

The tuning mainly reduces duplicate-ray build time by lowering the number of
ray batches. RT query time stays around 19.0s because the logical workload is
still 8.58B duplicate two-hop rays. That means M70 is a modest route-level
optimization, not a solution to the main traversal cost.

Next work should not keep blindly increasing batch size. The better target is a
different duplicate-ray representation or a same-contract comparison packet
that makes clear how much of the remaining time belongs to RT traversal versus
app/partner lowering.

## Claim Boundary

Allowed:

- Internal tuning wording for `com-orkut` on the RTX 4000 Ada pod.
- Explicit user guidance: 5M is conservative, 15M is the measured tuned cap for
  this row/hardware, and 18M/20M are unsafe.

Blocked:

- Making 15M the universal default.
- Public RT-core speedup wording.
- RTDL beats cuGraph/authors wording.
- Paper-system reproduction wording.
- Automatic hidden partner or cap selection.

## Evidence

- `docs/reports/goal4466_v3_0_m70_triangle_ray_batch_cap_planner_sweep_com_orkut_2026-06-16.json`
- `docs/reports/goal4466_v3_0_m70_triangle_segmented_scene_com_orkut_probe_10m_2026-06-16.json`
- `docs/reports/goal4466_v3_0_m70_triangle_segmented_scene_com_orkut_probe_15m_2026-06-16.json`
- `docs/reports/goal4465_v3_0_m69_triangle_segmented_scene_com_orkut_probe_2026-06-16.json`
