# Goal2816 Async Aggregate Reset Negative Probe

Date: 2026-05-31

Verdict: reject-for-retention.

Goal2816 tested a narrow hypothesis after Goal2815: perhaps part of the
remaining 32K/65K uniform overhead came from the synchronous CUDA driver memset
used to clear the prepared aggregate workspace before each fixed-radius ranked
summary aggregate call. The probe changed the reset to `cuMemsetD8Async(...)` on
the default stream, rebuilt the OptiX backend on the pod, and reran the same
32K/65K repeat-5 RTNN rows.

The result was negative. The async reset variant was correct, but it did not
produce a meaningful improvement. It was therefore not retained. The current
source keeps the simpler synchronous reset used by Goal2815.

## Evidence

Async-reset probe commit:

```text
commit: b760861b394db709a01804c97f6ccd91a25b3ac2
source_dirty: []
OptiX build: pass
focused tests: 6 passed
```

Final clean-head rollback guard:

```text
commit: 30f06c83951d7ebb755a37ae3e4fcf70a86aa67b
source_dirty: []
OptiX build: pass
focused tests: 12 passed
```

Artifacts:

- `docs/reports/goal2816_rtnn_async_aggregate_reset_negative_probe_pod/rtnn_async_reset_median_f32_32768.json`
- `docs/reports/goal2816_rtnn_async_aggregate_reset_negative_probe_pod/rtnn_async_reset_median_f32_65536.json`

## Timing Against Goal2815

| Points | Distribution | Goal2815 RTDL (s) | Async reset RTDL (s) | Change | Async reset CuPy/RTDL |
| ---: | --- | ---: | ---: | ---: | ---: |
| 32768 | uniform | 0.000095278 | 0.000094890 | 1.004x | 0.731x |
| 32768 | clustered | 0.004706190 | 0.004707874 | 1.000x | 2.541x |
| 32768 | shell | 0.000136988 | 0.000135501 | 1.011x | 1.952x |
| 65536 | uniform | 0.000155801 | 0.000156903 | 0.993x | 0.883x |
| 65536 | clustered | 0.018604644 | 0.018786461 | 0.990x | 2.503x |
| 65536 | shell | 0.000349855 | 0.000350927 | 0.997x | 7.740x |

The small differences are noise-level and do not justify keeping the extra
asynchronous reset path.

## Interpretation

The remaining small-row gap is not primarily the host synchronization behavior
of the tiny aggregate reset. The useful next target is a larger batched or
graph-captured execution contract that amortizes launch/setup overhead across
multiple small aggregate calls, or a deeper small-row partial-output path. That
future work should remain generic and contract-driven.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No native app-specific engine customization is introduced.
