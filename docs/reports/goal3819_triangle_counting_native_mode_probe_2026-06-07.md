# Goal3819 Triangle Counting Native-Mode Probe

Date: 2026-06-07

## Purpose

Follow up the Goal3818 benchmark smoke packet after noticing that the triangle
counting row used `--optix-graph-mode auto` and the app reported a
host-indexed fallback. This goal probes the explicit current native mode and
updates the benchmark README so users do not accidentally measure the
conservative fallback when they intend to test the native summary path.

## Pod Command

```bash
export PYTHONPATH=.pydeps_goal3788_numba:src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
python examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py \
  --mode run \
  --backend optix \
  --output-mode summary \
  --optix-graph-mode native \
  --copies 128 \
  --repeat 2 \
  --warmup 1
```

Artifact:

`docs/reports/goal3819_triangle_counting_native_mode_probe_a5000/triangle_native.stdout.txt`

## Result

The explicit native mode passed on the A5000 pod.

Compared with the Goal3818 smoke command on the same commit and same
`copies=128` fixture:

| Route | Reported `optix_graph_mode` | `query_raw_view_sec` | App RT-core status |
| --- | --- | ---: | --- |
| `--optix-graph-mode auto` | `auto` | `6.018893013708293` | `rt_core_accelerated=false` |
| `--optix-graph-mode native` | `native` | `0.9871935369446874` | `rt_core_accelerated=false` |

Interpretation:

- Explicit `native` mode is the better current command for the synthetic
  triangle-count summary route in this packet.
- The app still classifies this path as `host_indexed_fallback` and keeps
  `triangle_count_rt_core_claim_authorized=false`.
- Therefore this is route-selection evidence and internal performance hygiene,
  not public RT-core triangle-count evidence.

## Documentation Action

`examples/v2_0/research_benchmarks/triangle_counting/README.md` now includes
the explicit native-mode command and the claim boundary for this route.

## Boundary

This does not authorize release action, public speedup wording, broad RT-core
wording, triangle-count RT-core wording, whole-app acceleration wording,
paper-reproduction wording, AMD hardware/performance wording, automatic partner
selection, true-zero-copy wording, or app-specific native-engine logic.
