# Goal2817 RTNN Block-Partial Aggregate Path

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2817 continues the v2.5 RTNN fixed-radius ranked-summary work after the
Goal2816 negative reset probe. The next tested hypothesis was that small
direct-summary rows still pay unnecessary global aggregate traffic. Goal2817
adds a generic block-partial variant for prepared-query, summary-only float32
fixed-radius aggregates: each CUDA block writes one aggregate partial into a
prepared query-owned workspace, then the host downloads and reduces those small
partials.

This remains app-agnostic. The native vocabulary is fixed-radius, query points,
ranked summaries, aggregate partials, and prepared query handles. No RTNN
native symbol or benchmark-specific branch is introduced.

## Code Changes

| File | Change |
| --- | --- |
| `src/native/optix/rtdl_optix_core.cpp` | Added `fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks`, a block-partial summary-only aggregate kernel. |
| `src/native/optix/rtdl_optix_workloads.cpp` | Added prepared query-owned partial aggregate workspace and a small-row direct path for `query_count <= 65536`. |
| `src/rtdsl/optix_runtime.py` | Added phase label `prepared_query_uniform_cell_ranked_summary_aggregate_f32_block_partials`. |
| `tests/goal2817_rtnn_block_partial_aggregate_test.py` | Guards generic naming, workspace ownership, pod artifacts, and claim boundary. |

## Pod Evidence

Clean-from-Git pod:

```text
commit: 578cfe947037fff476c81b84a11e36ac6ac8fe45
source_dirty: []
GPU: NVIDIA RTX A5000, 570.211.01
OptiX build: pass
focused tests: 7 passed
```

Artifacts:

- `docs/reports/goal2817_rtnn_block_partial_aggregate_pod/rtnn_block_partial_median_f32_32768.json`
- `docs/reports/goal2817_rtnn_block_partial_aggregate_pod/rtnn_block_partial_median_f32_65536.json`

## A/B Median Timing Against Goal2815

| Points | Distribution | Goal2815 RTDL (s) | Goal2817 RTDL (s) | RTDL change | Goal2817 CuPy/RTDL |
| ---: | --- | ---: | ---: | ---: | ---: |
| 32768 | uniform | 0.000095278 | 0.000083132 | 1.146x | 0.920x |
| 32768 | clustered | 0.004706190 | 0.004881053 | 0.964x | 2.453x |
| 32768 | shell | 0.000136988 | 0.000130961 | 1.046x | 2.067x |
| 65536 | uniform | 0.000155801 | 0.000138950 | 1.121x | 1.077x |
| 65536 | clustered | 0.018604644 | 0.018752541 | 0.992x | 2.513x |
| 65536 | shell | 0.000349855 | 0.000365343 | 0.958x | 7.451x |

The important movement is the uniform weak spot:

- 32K uniform improves by about 1.15x but still trails CuPy.
- 65K uniform improves by about 1.12x and crosses parity, at 1.077x CuPy/RTDL.
- 5 of 6 small rows now beat the CuPy grid opponent. The only remaining
  same-contract small-row miss is 32K uniform.

The clustered and shell movements are mixed but bounded. Clustered rows continue
to use the two-step path, not the block-partial path. Shell rows use the
block-partial path; 32K shell improves and 65K shell regresses modestly, but
65K shell still has a large 7.451x CuPy/RTDL margin.

## Interpretation

Goal2817 shows that the remaining small-row problem was not only allocation
overhead. For sparse direct-summary rows, reducing global aggregate traffic and
using query-owned partial aggregate workspace can move real timing. The design
is still contract-driven: use block partials when the user asks for a summary
aggregate, not when the user asks for ordered witness rows.

The remaining 32K uniform gap is now small enough that the next useful target
should be broader overhead amortization rather than another single-call
micro-tweak: batched prepared aggregates, CUDA graph capture, or an event-based
multi-aggregate execution contract.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized before external review.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No package-install claim is authorized.
- No native app-specific engine customization is introduced.
