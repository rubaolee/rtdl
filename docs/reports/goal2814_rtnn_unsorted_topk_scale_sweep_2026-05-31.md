# Goal2814 RTNN Unsorted Top-K Scale Sweep

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2814 records a larger same-contract RTNN scale sweep for the Goal2813
unsorted bounded top-k summary path. Goal2813 showed strong wins on clustered
and shell rows at 32K and 65K points, but both uniform rows were still slower
than the CuPy grid opponent. The open question was whether that uniform weakness
was a primitive design problem or small-row overhead.

The larger sweep answers that question in favor of the primitive design:
with 131K and 262K points, RTDL is faster than the CuPy grid opponent in all 6
large-scale rows while preserving exact aggregate agreement with the CuPy grid
baseline. The remaining weakness is best described as small-row overhead, not a
failure of the generic fixed-radius ranked-summary primitive.

## Evidence Setup

Clean-from-Git pod:

```text
commit: 8db92cafaf8b054dcaed67a40b9fa6ca31828066
source_dirty: []
GPU: NVIDIA RTX A5000, 570.211.01
OptiX SDK: /root/vendor/optix-sdk
OptiX library: /root/rtdl_goal2785_work/build/librtdl_optix.so
```

Final clean-head guard after report/artifact commit:

```text
commit: 1551b8bfdd0fe9f326351ba896738f3b3a6c929b
source_dirty: []
focused tests: 10 passed
```

Harness:

```text
scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py
harness_version: rtdl.goal2800.rtnn_v2_5_live_ranked_summary_harness.v5.prepared_query_aggregate_float32_median
repeat: 3
query_batch_size: point_count
radius: 0.02
k_max: 50
```

Artifacts:

- `docs/reports/goal2814_rtnn_unsorted_topk_scale_sweep_pod/rtnn_unsorted_topk_scale_131072.json`
- `docs/reports/goal2814_rtnn_unsorted_topk_scale_sweep_pod/rtnn_unsorted_topk_scale_262144.json`

## Median Timing Results

| Points | Distribution | RTDL median (s) | CuPy grid median (s) | CuPy/RTDL |
| ---: | --- | ---: | ---: | ---: |
| 131072 | uniform | 0.000302740 | 0.000576740 | 1.905x |
| 131072 | clustered | 0.067074863 | 0.150910448 | 2.250x |
| 131072 | shell | 0.002534534 | 0.028577222 | 11.275x |
| 262144 | uniform | 0.000965423 | 0.003626705 | 3.757x |
| 262144 | clustered | 0.224376351 | 0.439262436 | 1.958x |
| 262144 | shell | 0.033773679 | 0.144271217 | 4.272x |

All six rows have:

- `status: pass`
- `source_dirty: []`
- median RTDL and CuPy timing
- `ranked_aggregate_matches_cupy_grid: true`
- `upload_sec: 0.0` inside the RTDL timed phase

## Interpretation

Goal2814 does not add new code. It clarifies where the Goal2813 primitive is
strong and where the remaining overhead lives.

At 32K and 65K points, uniform rows are sparse enough that kernel launch, native
call overhead, aggregate-buffer setup, and scalar result download are a large
share of the total RTDL time. At 131K and 262K points, useful traversal and
summary work dominate those fixed costs, and the same generic RTDL path moves
ahead of the CuPy grid opponent on uniform data too.

This is important for v2.5 design: the next improvement should not be a
RTNN-specific shortcut. The reusable target is a lower-overhead small-row
execution contract, such as reusable aggregate workspaces or an event/batched
summary API that amortizes launch/setup overhead across repeated small queries.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized before external review.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No package-install claim is authorized.
- No native app-specific engine customization is introduced.

The internal engineering conclusion is strong: for sufficiently large
same-contract RTNN rows, the v2.5 generic fixed-radius ranked-summary path is no
longer merely closing the gap; it is faster than the CuPy grid opponent on every
tested distribution. Public wording still requires external review.
