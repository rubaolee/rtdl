# Goal2030 Large-Scale v2.0 Dev Pod Findings

Date: 2026-05-14

Status: development evidence, not release authorization

## Purpose

Goal2026 gave the current all-app v1.8 vs v2.0 position. The pod then remained
available, so Goal2030 uses it for larger and more diagnostic runs. This is not
a replacement release matrix. It is a development report: what scales, what
breaks, and what the next engineering work should target.

Pod:

- Host: `69.30.85.251:22085`
- GPU: `NVIDIA RTX A5000, 570.211.01, 24564 MiB`
- Checkout: `/root/rtdl_goal2024_936aff2f`
- Source label: `936aff2f1b1d83ee0187c0ef5610db91dd80fd40`
- CUDA toolchain observed by `ldd`: CUDA `13.0`, `libnvrtc.so.13`

Artifact directories:

- `docs/reports/goal2028_large_scale_dev_pod_sweep_936aff2f/`
- `docs/reports/goal2029_targeted_large_dev_pod_sweep_936aff2f/`

## Results

| Area | Size | v1.8 median s | v2 median s | v2/v1.8 | Status | Lesson |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| database analytics | 200k copies | 14.213700 | 2.870273 | 0.202x | pass | Columnar partner continuation scales smoothly. |
| database analytics | 500k copies | 35.113168 | 6.963365 | 0.198x | pass | Ratio improves slightly with size; this is a real large-row v2 win. |
| polygon extent controls | 10k copies | 1.465724 / 1.031353 | 0.337216 / 0.234297 | 0.230x / 0.227x | pass | Current dense extent path remains good at 10k. |
| polygon extent controls | 12k copies | 1.727046 / 1.167387 | 0.342935 / 0.253313 | 0.199x / 0.217x | pass | 12k still works and remains clearly faster. |
| polygon extent controls | 16k copies | n/a | n/a | n/a | OOM | Dense all-pairs CuPy extent discovery hit the A5000 memory ceiling. |
| graph analytics | 5k copies | timed out | n/a | n/a | timeout | v1.8 oracle timing becomes the bottleneck; use bounded/v2-only scale probes above 1k. |
| graph analytics | 100k copies | skipped | 0.000206 | n/a | v2-only pass | Compressed metric-table pattern stays effectively constant-time for this authored row. |
| graph analytics | 1M copies | skipped | 0.000123 | n/a | v2-only pass | Same lesson: graph control row is dominated by fixed compressed pattern cost. |
| segment anyhit rows | 1,048,576 rows, capacity 2x | 6.315167 | n/a | n/a | overflow | `2 * count` witness capacity is still too small. |
| segment anyhit rows | 1,048,576 rows, capacity 3x | 6.131052 | 22.422607 | 3.657x | pass-slow | Materialized witness rows are too expensive at this capacity. |
| segment anyhit rows | 1,048,576 rows, capacity 4x | 6.043373 | 22.664319 | 3.750x | pass-slow | More capacity does not fix the row-materialization cost. |
| robot collision | 4,194,304 poses | 0.303589 | 0.005306 | 0.017x | pass | True zero-copy partner pose flags scale strongly. |
| robot collision | 16,777,216 poses | 1.289325 | 0.019840 | 0.015x | pass | This is one of the cleanest large-scale v2 wins. |
| road hazard prepared-only | 8,192 roads | 0.017377 | 0.003426 | 0.197x | pass | Prepared partner path scales better than the older full harness. |
| road hazard prepared-only | 16,384 roads | 0.041209 | 0.005530 | 0.134x | pass | Strong large-row prepared path; first-run max shows warmup/allocation should be reported separately. |
| fixed-radius partner device scene | default facility probe | n/a | n/a | n/a | PTX failure | CUDA 13 NVRTC/PTX is incompatible with the pod driver path for this generated PTX. |

## Development Findings

### 1. Database Is Healthy

Database analytics is now a credible v2 row at larger sizes. At 500k copies,
v2 is about `5.0x` faster than v1.8. The ratio is stable from 100k to 500k:

- 100k current matrix: `0.235x`
- 200k Goal2030: `0.202x`
- 500k Goal2030: `0.198x`

This supports the current v2 design direction: generic columnar payloads plus
partner-side predicate/reduction continuation.

### 2. Polygon Needs Tiling

The 10k and 12k polygon extent rows are both successful and faster than v1.8.
The 16k row fails with:

`Out of memory allocating 6,442,450,944 bytes (allocated so far: 19,328,991,232 bytes).`

That is a design finding. The current `cupy_extent` path uses dense all-pairs
intermediate arrays. For v2.0 release notes, the row remains bounded to the
measured 8k-12k range. For further dev, the fix is a tiled or chunked extent
candidate discovery contract, not another app-specific native engine hook.

### 3. Graph Needs Better Benchmark Framing

The graph row is fast because the authored app can be expressed as a compressed
metric-table pattern. At 100k and 1M copies, v2 remains around sub-millisecond.
But timing the v1.8 oracle beyond 1k copies becomes unreasonable and timed out
at 5k.

For future reports, graph should have:

- a small same-contract v1.8 vs v2 row for correctness and ratio;
- v2-only scale probes for large repeated-count behavior;
- no broad claim about arbitrary graph traversal acceleration.

### 4. Segment Materialized Rows Are Not The Right Large-Scale Contract

The segment anyhit materialized-row path is the clearest remaining development
warning. At 1,048,576 rows:

- `2 * count` witness capacity overflows;
- `3 * count` and `4 * count` pass, but v2 is about `3.7x` slower than v1.8.

The issue is not correctness; strict rows match. The issue is that materializing
millions of witness rows into partner columns is the wrong large-scale output
contract for this app shape. The next v2 design target should be compact
partner-side summaries: flags, counts, grouped counts, or paged output, selected
by the Python app layer.

### 5. Robot Is The Cleanest Zero-Copy Success

Robot collision is the strongest current evidence for the v2 zero-copy
direction. It passes at 16,777,216 poses with exact pose-flag parity and
`0.015x` v2/v1.8. This is the kind of row that should anchor the final v2.0
story: RTDL emits generic prepared ray/primitive work, and CuPy consumes device
columns/output flags without returning to Python object materialization.

### 6. Road Hazard Prepared Path Scales

The prepared-only road hazard probe avoids the old one-shot timing cost and
shows better ratios as size grows:

- 8,192 roads: `0.197x`
- 16,384 roads: `0.134x`

The emitted witness counts remain compact relative to the large capacity. The
main reporting debt is to separate warmup/allocation outliers from steady-state
median timing.

### 7. Fixed-Radius PTX Is A Pod Toolchain Blocker

The fixed-radius family still fails before timing with:

`CUDA driver error: the provided PTX was compiled with an unsupported toolchain.`

The environment diagnostic shows CUDA `13.0` / `libnvrtc.so.13` on driver
`570.211.01`. This should be treated as a pod toolchain compatibility blocker
for fresh fixed-radius reruns on this pod, not as a performance result.

## Next Engineering Targets

1. Add a tiled/chunked `cupy_extent` candidate-discovery path for polygon
   control rows so 16k+ does not require dense all-pairs matrices.
2. Add a compact segment output contract for large rows: partner flags/counts
   or paged witness materialization, instead of always materializing every
   witness row.
3. Add benchmark modes that separate correctness rows, v1/v2 ratio rows, and
   v2-only scale probes. Graph made this need obvious.
4. Add warmup/allocation phase reporting for road hazard and robot so medians
   cannot hide first-run costs.
5. Fix or quarantine the CUDA 13 NVRTC/PTX mismatch before using this pod for
   fresh fixed-radius evidence.

## Claim Boundary

This report gathers development evidence. It does not authorize:

- Do not claim final v2.0 release from this report.
- Do not claim whole-app speedup for every workload.
- Do not claim broad RT-core acceleration.
- Do not claim package-install support.
- Do not claim unbounded polygon, graph, or segment materialization.

The main conclusion is narrower and useful: v2.0 is strong where the app can
consume compact partner-side columns/summaries, and weak where the current
contract still forces dense all-pairs intermediates or huge materialized witness
tables.
