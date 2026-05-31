# Goal2758: Reusable Hit-Stream Buffer Perf Probe

Date: 2026-05-31

Status: pod-measured internal optimization probe

## Purpose

Goal2756 added caller-owned reusable CUDA output buffers for the generic OptiX
ray/triangle hit-stream columns. Goal2758 measures the narrow effect of that
allocation strategy:

- old path: native-owned output columns allocated/released per run;
- new path: caller-owned reusable `torch.int64` output columns passed into the
  native OptiX hit-stream ABI.

This is not a whole-app benchmark. It is a generic primitive/runtime probe for
one overhead source identified after Goal2754.

## Environment

- Host: `69.30.85.171`
- GPU: NVIDIA RTX A5000
- Commit: `2f7579e8`
- OptiX library: `/root/rtdl/build/librtdl_optix.so`
- Script: `scripts/goal2758_reusable_hit_stream_buffer_perf_probe.py`

Artifacts:

- `docs/reports/goal2758_pod_artifacts/goal2758_reusable_hit_stream_buffer_perf_69_30_85_171_2026-05-31.json`
- `docs/reports/goal2758_pod_artifacts/goal2758_reusable_hit_stream_buffer_perf_large_69_30_85_171_2026-05-31.json`

## Results

Median total time includes the Python call into the prepared scene method and
the native synchronized return. Median native-call time is the method's recorded
native call phase.

| rows | native-owned total s | reusable total s | reusable/native total | native-owned native-call s | reusable native-call s | reusable/native native-call |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1,024 | 0.000178 | 0.000161 | 0.904x | 0.000136 | 0.000139 | 1.017x |
| 8,192 | 0.000325 | 0.000315 | 0.969x | 0.000275 | 0.000279 | 1.017x |
| 32,768 | 0.000996 | 0.000948 | 0.952x | 0.000921 | 0.000886 | 0.962x |
| 131,072 | 0.003267 | 0.002399 | 0.734x | 0.003197 | 0.002439 | 0.763x |
| 524,288 | 0.009341 | 0.008444 | 0.904x | 0.009269 | 0.008833 | 0.953x |

Interpretation:

- Reusable output buffers reduce total measured time in all rows.
- The effect is modest at small sizes where launch/host overhead dominates.
- The strongest observed row is 131,072 outputs, where reusable total time is
  about `0.734x` of native-owned total time.
- The native-call phase is noisy at tiny sizes, but improves at larger sizes.
- This confirms reusable output buffers are a useful generic building block, but
  it does not close the much larger Goal2754 gap between generic hit-stream
  continuation and fused prepared grouped primitives.

## Boundary

This goal authorizes only an internal statement:

> For the generic OptiX ray/triangle hit-stream output-column path, caller-owned
> reusable output buffers reduce one measured overhead source relative to
> per-run native-owned output allocation/release on the RTX A5000 pod.

This goal does not authorize:

- public speedup claims;
- true zero-copy claims;
- no-sync producer/consumer claims;
- a claim that generic hit-stream continuation is faster than fused primitives;
- release promotion.

The next useful work remains event/same-stream ordering, fused gather plus
continuation, and device-resident row-count/overflow handling.
