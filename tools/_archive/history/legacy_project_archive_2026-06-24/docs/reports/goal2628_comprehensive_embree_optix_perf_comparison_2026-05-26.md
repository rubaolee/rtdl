# Goal2628 Comprehensive Embree vs OptiX/RT Benchmark Comparison

Date: 2026-05-26

This is an internal RTDL engineering performance report. It is not a public
speedup claim. The purpose is to establish an Embree-vs-OptiX baseline across
the promoted benchmark-app portfolio before the next Python+partner+RTDL work.

## Environment And Reproducibility

- Pod SSH: `ssh root@203.57.40.101 -p 10165 -i ~/.ssh/id_ed25519`
- Working local key on this Mac: `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`
- GPU: NVIDIA RTX A5000, driver `565.57.01`, 24564 MiB
- Embree on pod: `4.3.0`
- OptiX SDK: `/root/vendor/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64`
- CUDA runtime used for OptiX runs: CUDA 12.6 via:
  `LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH`
- PTX policy used after investigation:
  `RTDL_OPTIX_PTX_COMPILER=nvcc`,
  `RTDL_NVCC=/usr/local/cuda-12.6/bin/nvcc`,
  `RTDL_OPTIX_PTX_ARCH=compute_86`
- CuPy was installed in pod-local venv:
  `/root/rtdl_goal2627/venv`
- Final source commit for calibrated runner:
  `06b32d9863de416d58a25b93342cffd453b7895d`

Primary artifacts:

- Full calibrated all-app run:
  `docs/reports/goal2628_calibrated_standard_all_pod/summary_compact.json`
- RayDB cap-fixed rerun:
  `docs/reports/goal2628_raydb_standard_capfixed_pod/summary.json`
- RT-DBSCAN calibration:
  `docs/reports/goal2628_rt_dbscan_calibration_pod/`
- LibRTS calibration:
  `docs/reports/goal2628_librts_calibration_pod/`
- Hausdorff larger calibration:
  `docs/reports/goal2628_hausdorff_calibration_pod/`
- RTNN large run:
  `docs/reports/goal2628_rtnn_large_envfixed_pod/summary.json`

## Main Performance Matrix

The table uses app-internal timings when available. `process_wall` rows are
weaker because they include Python process startup, import, setup, or compilation
effects.

| Benchmark app | Workload / metric | Embree sec | OptiX sec | OptiX speedup | Verdict |
| --- | --- | ---: | ---: | ---: | --- |
| Hausdorff / X-HD | threshold decision, standard | 0.0956 | 0.0301 | 3.17x | OptiX win |
| Hausdorff / X-HD | threshold decision, 262144 copies | 7.694 | 4.954 | 1.55x | OptiX win at second-scale |
| RT-DBSCAN | clustered3d, 8192 points | 20.364 | 1.197 | 17.0x | OptiX win after calibrated scale |
| Robot collision | prepared collision flags | 0.00959 | 0.00147 | 6.51x | OptiX win, app setup dominates wall time |
| LibRTS AABB index | 1024 boxes, 512 queries | 21.738 | 1.015 | 21.4x | OptiX win |
| RTNN | 65536 points, ranked summary | 0.279 | 0.00163 | 171x | OptiX win |
| RTNN | 262144 points, ranked summary | 3.057 | 0.00975 | 314x | OptiX win at second-scale |
| Contact manifold | native `COLLECT_K_BOUNDED` i64 | 0.0128 | 0.0117 | 1.09x | Slight OptiX win; app oracle dominates wall time |
| RayDB-style count | 960K rows, grouped count query | 0.189 | 0.736 | 0.257x | OptiX loss; see investigation |
| RayDB-style sum | 960K rows, grouped sum query | 0.190 | 0.652 | 0.291x | OptiX loss; see investigation |
| Barnes-Hut | current node/candidate coverage row | 0.615 | 1.414 | 0.435x | Not a valid final same-contract RT comparison |
| Spatial RayJoin | current generic all-workload route | 0.0215 | 1.041 | 0.0207x | Not a valid final RT claim path |
| Triangle counting | current native graph summary row | 0.612 | 1.496 | 0.409x | OptiX fallback, not RT-core accelerated |

## Investigation Notes

RT-DBSCAN initially looked bad at tiny scale because the OptiX path paid
CuPy/adapter/setup overhead. At 2048 points, OptiX was slower (`4.67s` vs
`1.05s`). At 4096 points, OptiX became `3.85x` faster, and at 8192 points it
became `17.0x` faster. This is the expected scaling direction for the RT-shaped
grouped-stream path.

LibRTS initially looked close at quick scale. With calibrated workloads, OptiX
wins clearly: `512x256` gives `2.54s` Embree vs `0.726s` OptiX, and `1024x512`
gives `21.74s` Embree vs `1.015s` OptiX. The previous standard size
`32768x8192` was pathological for the generic Embree columnar path and ran for
minutes.

RayDB remains a real runtime gap. The first-wave columnar payload path copies
six host columns and is capped at 1,000,000 rows per RT job. At 960K rows,
Embree query time is about `0.19s`, while OptiX query time is `0.65-0.74s`.
The partner-resident experimental probe improves total preparation cost
(`~0.29-0.33s` query), but it is not RT-core accelerated and still does not beat
Embree. Next work should target typed/partner-resident column buffers, chunked
execution past 1M rows, and a device-resident grouped reduction path.

Spatial RayJoin is not yet a fair OptiX loss. The full matrix uses the generic
OptiX route on a tiny fixture, where setup dominates. The prepared OptiX route
for PIP/LSI has microsecond query phases, but overlay continuation is still
unsupported by that route. The required next primitive is generic
device-resident row-stream continuation for prepared spatial joins.

Triangle counting is currently a fallback gap. The payload classifies the OptiX
path as `host_indexed_fallback` and `rt_core_accelerated=false`; therefore the
loss is not evidence that RT cores are slower. To make this a real OptiX
benchmark claim, we need a native RT-core graph triangle-count path rather than
the current host-indexed correctness path.

Barnes-Hut is also not a clean same-contract comparison yet. The Embree row is
a candidate-summary path, while the OptiX row is a prepared node-coverage
decision over only four quadtree nodes. The current loss is dominated by
process/setup and contract mismatch. The next engine work is a same-contract
generic hierarchical aggregate-frontier primitive for both Embree and OptiX.

Contact manifold validates the generic native bounded collector, but the app
generates witness rows through app-owned Python oracle logic. At larger grid
sizes, wall time is dominated by that oracle; the native collector itself is
only milliseconds. This app is useful for `COLLECT_K_BOUNDED` semantics, not as
a clean RT traversal throughput benchmark until witness discovery is also moved
onto generic RT primitives.

## Conclusions

OptiX/RT wins the workloads that currently have a true, calibrated RT-shaped
path: Hausdorff, RT-DBSCAN, robot collision, LibRTS AABB, RTNN, and slightly
contact collector native copy/sort. The wins are especially strong for
fixed-radius neighbor/ranked-summary workloads and high-volume AABB queries.

The remaining losses identify concrete runtime work, not reasons to abandon RT:
RayDB needs device-resident typed columnar reduction; Spatial RayJoin needs
device-resident continuation; Triangle Counting needs a real RT-core graph path;
Barnes-Hut needs same-contract hierarchical aggregate-frontier parity.

For the next version, the performance target should be: every promoted
benchmark has a same-contract Embree row and OptiX row, and any OptiX loss must
be either fixed or explicitly demoted from benchmark-claim status until the
missing generic primitive exists.
