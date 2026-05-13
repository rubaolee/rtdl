# Goal1869 - Road Hazard v2 Partner Performance

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1869 adds and validates a timing harness for the Goal1865 road-hazard partner
priority-flag adapter:

`scripts/goal1869_road_hazard_v2_partner_perf.py`

The measured app is `road_hazard_screening`. The comparison is:

- v1.8/current one-shot native OptiX road-hazard hit-count rows:
  `rt.run_optix(road_hazard_hitcount, ...)`
- v1.8/current prepared native OptiX segment/polygon hit-count rows:
  `prepare_optix_segment_polygon_hitcount_2d(...).run(...)`
- v2.0 preview caller-supplied partner-column path:
  `road_hazard_priority_flags_optix_partner_device_columns(...)`

The parity contract is per-road priority flags produced from the same
hit-count threshold.

## Pod Commands

```bash
PYTHONPATH=src:. python3 scripts/goal1869_road_hazard_v2_partner_perf.py \
  --count 512 \
  --threshold 2 \
  --iterations 5 \
  --partners cupy,torch \
  --output docs/reports/goal1869_road_hazard_v2_partner_perf_pod_512.json
```

```bash
PYTHONPATH=src:. python3 scripts/goal1869_road_hazard_v2_partner_perf.py \
  --count 2048 \
  --threshold 2 \
  --iterations 5 \
  --partners cupy,torch \
  --output docs/reports/goal1869_road_hazard_v2_partner_perf_pod_2048.json
```

The runner prints `[setup]`, `[timing]`, and `[artifact]` progress markers for
pod use.

## Pod Evidence

Artifacts:

- `docs/reports/goal1869_road_hazard_v2_partner_perf_pod_512.json`
- `docs/reports/goal1869_road_hazard_v2_partner_perf_pod_2048.json`

Pod:

- SSH: `root@213.192.2.116 -p 40189`
- Key used by Codex: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- GPU: `NVIDIA GeForce RTX 3090, 580.126.20`
- Commit: `0a96e139a7d584e56e6dd05539ad66e3370aa9d7`

## Observed Timing

These timing rows are internal engineering evidence only.

Dataset: 512 synthetic road/hazard rows, threshold 2, 512 priority-flag outputs.

| Path | Median query time (s) | Ratio vs v1.8 one-shot | Ratio vs v1.8 prepared |
| --- | ---: | ---: | ---: |
| v1.8 one-shot native OptiX road-hazard rows | 0.2061413107 | 1.000x | 215.276x |
| v1.8 prepared native OptiX road-hazard rows | 0.0009575686 | 0.0046x | 1.000x |
| v2.0 CuPy priority columns | 0.0015592678 | 0.0076x | 1.628x |
| v2.0 Torch priority columns | 0.0012846882 | 0.0062x | 1.342x |

Dataset: 2048 synthetic road/hazard rows, threshold 2, 2048 priority-flag outputs.

| Path | Median query time (s) | Ratio vs v1.8 one-shot | Ratio vs v1.8 prepared |
| --- | ---: | ---: | ---: |
| v1.8 one-shot native OptiX road-hazard rows | 16.3427473083 | 1.000x | 4523.323x |
| v1.8 prepared native OptiX road-hazard rows | 0.0036129951 | 0.00022x | 1.000x |
| v2.0 CuPy priority columns | 0.0017044870 | 0.00010x | 0.472x |
| v2.0 Torch priority columns | 0.0015918282 | 0.00010x | 0.441x |

The first partner iteration includes framework/kernel startup effects and is
preserved in the artifacts. The median is the working comparison statistic for
this narrow row.

## Boundary

This is a same-contract v2.0-vs-v1.8 timing row for one app path. It is not an
all-app performance table and does not authorize v2.0 release wording.

No whole-app speedup claim, broad RT-core speedup claim, package-install claim,
or v2.0 release claim is authorized by this goal.
