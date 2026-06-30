# Goal919: Event Hotspot RTX Readiness Promotion

Date: 2026-04-25

## Purpose

Resolve the remaining hold on `event_hotspot_screening` after Goal917. Goal917
already ingested a real RTX artifact for the bounded prepared count-summary
path, but the app was not promoted because the committed Embree baseline was
at `copies=2000` while the RTX artifact used `copies=20000`.

## Evidence Used

| Evidence | Path | Result |
| --- | --- | --- |
| RTX artifact | `docs/reports/cloud_2026_04_25/goal811_event_hotspot_rtx.json.gz` | `copies=20000`, `event_count=120000`, `hotspot_count=99999`, `optix_prepare=6.69359050039202s`, `optix_query=1.1063673989847302s`, `python_postprocess=0.11933588702231646s` |
| Same-scale Embree baseline | `docs/reports/goal919_event_hotspot_same_scale_embree_baseline_2026-04-25.json` | `copies=20000`, `iterations=3`, `event_count=120000`, `hotspot_count=99999`, `summary_sha256=35666dd007dfa50658cfb7e1d472ff804571c5128b5c6bf4ffc14b613facc976`, `optix_query` field used as backend-query median `0.3169813749846071s` |
| Exact parity check | local JSON comparison | Embree hotspot list exactly matches the RTX hotspot list. |

The new baseline is intentionally added as a Goal919 artifact instead of
mutating the older Goal835 committed baseline file. Existing unrelated dirty
Goal835 files are left untouched.

## Promotion Decision

`event_hotspot_screening` is promoted only for the bounded prepared
count-summary path:

- `optix_app_benchmark_readiness`: `ready_for_rtx_claim_review`
- `rt_core_app_maturity`: `rt_core_ready`
- Active manifest entry: `scripts/goal811_spatial_optix_summary_phase_profiler.py --scenario event_hotspot_screening --mode optix --copies 20000`

## Boundaries

- This is not a whole-app hotspot analytics speedup claim.
- This is not a neighbor-row output claim.
- The claim path is only prepared OptiX fixed-radius count traversal for
  compact hotspot summaries.
- No new paid pod is needed only for this app; future reruns should happen
  only inside a consolidated regression batch.

## Files Updated

- `src/rtdsl/app_support_matrix.py`
- `docs/app_engine_support_matrix.md`
- `scripts/goal759_rtx_cloud_benchmark_manifest.py`
- `scripts/goal849_spatial_promotion_packet.py`
- generated Goal759, Goal848, and Goal849 report artifacts
- focused contract tests for readiness, maturity, manifest, and promotion packet
