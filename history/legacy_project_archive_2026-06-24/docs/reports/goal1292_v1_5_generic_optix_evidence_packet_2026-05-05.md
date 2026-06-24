# Goal1292 v1.5 Generic OptiX Evidence Packet

Date: 2026-05-05
Source commit: `f5464d36b2f068683e15a7bb92988d65e33bcb80`
Result dir: `docs/reports/goal1292_v1_5_generic_optix_pod_results`

## Scope

- Active backends: `embree, optix`
- Frozen before v2.1: `vulkan, hiprt, apple_rt`
- Public wording authorized: `False`

## Pod Commands

```bash
mkdir -p docs/reports/goal1292_v1_5_generic_optix_pod_results
```
```bash
OUTPUT_JSON=docs/reports/goal1292_v1_5_generic_optix_pod_results/rtdl_pod_env.json OUTPUT_ENV=docs/reports/goal1292_v1_5_generic_optix_pod_results/rtdl_pod_env.sh bash scripts/rtdl_pod_env_probe.sh
```
```bash
. docs/reports/goal1292_v1_5_generic_optix_pod_results/rtdl_pod_env.sh
```
```bash
make build-optix
```
```bash
PYTHONPATH=src:. python3 -m unittest tests.goal1288_v1_5_generic_anyhit_count_test tests.goal1290_v1_5_generic_prepared_anyhit_count_test tests.goal1291_v1_5_embree_prepared_parity_status_test
```
```bash
PYTHONPATH=src:. python3 scripts/goal1292_v1_5_generic_optix_evidence_runner.py --copies 256 --query-repeats 100 --output docs/reports/goal1292_v1_5_generic_optix_pod_results/generic_optix_evidence.json
```
```bash
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py --backend optix --scenario visibility_edges --output-mode summary --copies 30000 --visibility-query-repeats 100 > docs/reports/goal1292_v1_5_generic_optix_pod_results/graph_visibility_optix_repeats.json
```

## Required Artifacts

- `docs/reports/goal1292_v1_5_generic_optix_pod_results/rtdl_pod_env.json`
- `docs/reports/goal1292_v1_5_generic_optix_pod_results/generic_optix_evidence.json`
- `docs/reports/goal1292_v1_5_generic_optix_pod_results/graph_visibility_optix_repeats.json`
- `docs/reports/goal1292_v1_5_generic_optix_pod_results/rtdl_pod_env.sh`

## Success Criteria

- Environment probe is preserved before any failure interpretation.
- Primitive runner records CPU oracle rows and OptiX direct ANY_HIT plus COUNT_HITS parity.
- Primitive fixture scale remains bounded because the CPU oracle is O(rays*triangles).
- Prepared OptiX COUNT_HITS hit_count matches CPU oracle hit_count.
- Graph wrapper artifact preserves visibility_query_repeats=100 and run_phases query mean/min/first timings.
- If OptiX remains slower than Embree, classify as optix_still_slower_with_reason only when correctness and bottleneck evidence are present.

## Known Gap

Embree prepared-scene parity for generic prepared ANY_HIT plus COUNT_HITS is not implemented yet; Goal1291 records it as blocked pending a scene/probe split or reviewed fallback.

## Boundary

This is an internal v1.5 NVIDIA evidence packet. It does not authorize public release wording, whole-app speedup claims, or new Vulkan/HIPRT/Apple RT implementation before v2.1.
