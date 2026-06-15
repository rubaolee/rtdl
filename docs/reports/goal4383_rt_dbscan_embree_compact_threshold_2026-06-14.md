# Goal4383 RTDBSCAN Embree Compact Threshold P0

Date: 2026-06-14

## Verdict

P0 is implemented and measured. RTDBSCAN no longer has the old Embree fairness blocker where the CPU side materialized threshold-capped neighbor rows while the OptiX side emitted compact device columns.

The new Embree side uses a generic prepared 3D fixed-radius count-threshold primitive:

- prepared Embree 3D point scene;
- query points, radius, and threshold;
- one compact per-query count/flag row;
- threshold-capped early exit;
- no neighbor-row materialization;
- no scene setup in the measured threshold phase;
- same Numba component-continuation path as the OptiX comparison.

This makes the comparison much closer to the intended hardware question: OptiX RT-core threshold output versus Embree CPU threshold output, with the same app continuation after that point. It does not make RTDBSCAN a strong public paper-scale claim yet, because the large rows are still synthetic clustered data and the shared Numba continuation dominates total time.

## Toolchain Fix

The pod driver is CUDA 12.4, while `/usr/local/cuda` points at CUDA 12.8. Numba was therefore emitting PTX 8.7, but the driver JIT only accepted PTX 8.4. This was solved by running Numba with the already-installed CUDA 12.4 Python NVCC package:

```bash
export CUDA_HOME=/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc
export CUDA_PATH=$CUDA_HOME
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/nvvm/lib64:${LD_LIBRARY_PATH:-}
```

A Numba CUDA smoke test then passed on the pod.

## Performance Matrix

Dataset: `clustered3d`. Radius: `0.055`. `min_neighbors`: `12`. Partner continuation: Numba prepared grid column signature. The 4,096-point row was validated against the app reference. Larger rows use `--no-validation` to avoid validation dominating memory/runtime; they are performance-scale rows under the same mode contract.

| Points | Embree CPU total | OptiX RT total | Embree / OptiX | Embree threshold phase | OptiX threshold phase | Shared Numba continuation | Validation |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 4,096 | 0.0266s | 0.0126s | 2.12x | 0.0196s | 0.0060s | 0.0043s | yes |
| 65,536 | 0.3431s | 0.2911s | 1.18x | 0.1683s | 0.1198s | 0.1376s | no |
| 131,072 | 0.8713s | 0.7894s | 1.10x | 0.3497s | 0.2677s | 0.4496s | no |
| 262,144 | 2.6670s | 2.4572s | 1.09x | 0.7872s | 0.5767s | 1.7293s | no |
| 524,288 | 8.8345s | 8.4297s | 1.05x | 1.6292s | 1.1931s | 6.9218s | no |

## Explanation

The result is reasonable and explainable.

The RT threshold phase is faster on OptiX, but it is not the whole app. At 524,288 points, the OptiX threshold phase is 1.193s and the Embree compact threshold phase is 1.629s, a 1.37x threshold-stage advantage. But the shared Numba continuation costs about 6.92s on both sides, so the full app speedup compresses to 1.05x.

That is not evidence that RT cores cannot help RTDBSCAN. It is evidence that this RTDBSCAN app path has moved its bottleneck away from the fixed-radius threshold query and into the shared connected-component continuation. The next performance question is therefore not another Embree fairness fix; it is whether RTDL should add a more fused/device-side DBSCAN continuation primitive or a better generic graph-component partner path.

The current public wording should be:

> RTDBSCAN now has a fairer same-continuation OptiX-vs-Embree engineering comparison. The RT threshold stage is faster on OptiX, but total speedup is small at large scale because both sides share a dominant Numba component-continuation phase.

The current public wording should not be:

> RT cores accelerate full RTDBSCAN by a large factor.

## Evidence Files

- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14/embree_compact_4096_r3.json`
- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14/optix_device_4096_r3.json`
- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14/embree_compact_65536_r5_no_validation.json`
- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14/optix_device_65536_r5_no_validation.json`
- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14/embree_compact_131072_r5_no_validation.json`
- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14/optix_device_131072_r5_no_validation.json`
- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14/embree_compact_262144_r3_no_validation.json`
- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14/optix_device_262144_r3_no_validation.json`
- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14/embree_compact_524288_r3_no_validation.json`
- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14/optix_device_524288_r3_no_validation.json`

## Remaining Debt

RTDBSCAN is no longer red for Embree threshold materialization fairness. It remains yellow for public benchmark-app wording:

- data is large synthetic clustered data, not the RTDBSCAN paper datasets;
- large rows are performance-scale no-validation rows, with correctness validated at 4,096 points;
- full-app speedup is limited by shared Numba component continuation;
- OptiX emits device columns, while Embree emits compact host rows plus a measured host-to-device upload, which is legitimate for CPU-vs-GPU comparison but must be stated.

Next action: decide whether v2.14 keeps RTDBSCAN as a narrow engineering row, or whether v2.14 also takes on a fused/device-side component-continuation primitive before close.
