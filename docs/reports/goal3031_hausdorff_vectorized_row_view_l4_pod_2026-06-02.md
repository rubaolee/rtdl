# Goal3031: Hausdorff Vectorized Row-View L4 Pod Probe

Date: 2026-06-02

## Purpose

Goal3031 measures the Goal3030 row-stream consumer change for the exact
RTDL/OptiX Hausdorff benchmark path. Goal3030 added a generic borrowed
structured NumPy view for `OptixRowView` host rows and changed
`rtdl_rt_grouped_adaptive_raw_nearest_witness` to reduce nearest-witness rows
with columnar NumPy operations instead of looping through ctypes rows.

This is still a generic host row-buffer consumer improvement. No native Hausdorff-specific ABI was added, and this does not create a device-memory or zero-copy partner handoff claim.

## Pod Environment

- GPU: `NVIDIA L4, 565.57.01`
- CUDA toolchain used for OptiX PTX: `/usr/local/cuda-12.6`
- Source commit: `f1ac3efb4177c3bd7edf0044da2491645dcb43cb`
- Dirty source list recorded by the artifact before writing: empty
- Warmup: 1
- Repeats per row: 3

Artifact:

- `docs/reports/goal3031_hausdorff_vectorized_row_view_l4_pod_2026-06-02.json`

Focused pod tests:

```text
python3 -m unittest \
  tests.goal3030_optix_row_view_numpy_reducer_test \
  tests.goal3026_hausdorff_adaptive_raw_row_view_test

Ran 10 tests in 0.359s
OK
```

## Results

| Points | Old adaptive RT median sec | Vectorized raw row-view RT median sec | CuPy grouped-grid median sec | Raw / old | Raw / CuPy |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4096 | 0.06497778743505478 | 0.050724875181913376 | 0.0037251412868499756 | 0.7806494678294922x | 13.616899675987039x |
| 8192 | 0.1458849236369133 | 0.1102646216750145 | 0.00687030702829361 | 0.7558328779020879x | 16.049446003056012x |
| 16384 | 0.2935662791132927 | 0.21562739461660385 | 0.02473144233226776 | 0.7345100917854029x | 8.718755328526438x |

## Interpretation

The vectorized row-view reducer is a real current-basis RTDL/OptiX improvement
for this exact Hausdorff path. On the measured L4 rows it is about 22-27%
faster than the older adaptive RT row path.

The dense CuPy grouped-grid reference still wins on all measured rows. This
confirms the same design conclusion as Goal3028: the remaining leap cannot come
from another Python row-materialization tweak. The next useful RTDL runtime work
is a generic device-resident active-set, sparse candidate-frontier, and
nearest-witness continuation contract that avoids repeatedly copying and
reducing witness rows on the host.

## Boundaries

This report does not authorize:

- v2.6 release
- public speedup wording
- broad RT-core speedup wording
- whole-app speedup wording
- true zero-copy wording
- package-install claims
- app-specific native-engine behavior

The evidence is internal benchmark-app tuning evidence on one L4 pod. It should
not be presented as an RTDL-vs-X-HD or RTDL-vs-CUDA victory claim.
