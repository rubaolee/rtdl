# Goal2822 Fused Batch Block-Partial Kernel

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2822 targets the remaining overhead inside the Goal2821 heterogeneous
prepared-aggregate batch path. Goal2821 reduced host/native crossings, but the
native block-partial batch still launched one aggregate kernel per request.
Goal2822 adds a fused 2D-grid block-partial kernel: `blockIdx.x` indexes query
blocks and `blockIdx.y` indexes aggregate requests.

This is app-agnostic. The native vocabulary remains fixed-radius neighbors,
prepared queries, ranked-summary aggregates, request radii, `k_max` values, and
block partials. No RTNN-specific ABI or benchmark branch is introduced.

## Change

- Added
  `fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks_batch`.
- Added the corresponding module function handle:
  `g_frn3d_grid_ranked_summary_aggregate_f32_blocks_batch`.
- The prepared-query aggregate batch path now uploads compact request arrays
  (`float radii`, `uint32_t k_values`) and launches one 2D-grid kernel for the
  small-row block-partial batch path.
- The host reduction layout remains `request_index * block_count + block_index`,
  so result semantics stay identical to Goal2821.

## Pod Evidence

Artifacts are saved under
`docs/reports/goal2822_rtnn_fused_batch_block_partial_kernel_pod/`.

The pod reran the same heterogeneous four-request sweep used in Goal2821:

| Request | Radius | k_max |
| ---: | ---: | ---: |
| 1 | 0.01 | 8 |
| 2 | 0.02 | 16 |
| 3 | 0.03 | 32 |
| 4 | 0.04 | 50 |

Results versus the Goal2821 non-fused batch baseline:

| Points | Goal2821 batch median sec | Goal2822 fused batch median sec | Change vs Goal2821 | Fused batch vs sequential singles |
| ---: | ---: | ---: | ---: | ---: |
| 32768 | 0.000300650 | 0.000272061 | 1.105x | 1.234x |
| 65536 | 0.000899193 | 0.000829070 | 1.085x | 2.139x |

Environment:

- GPU: NVIDIA RTX A5000, driver 570.211.01.
- Source commit: `ef2204808d9997729b194d743f76a8508fd84a85`.
- Source dirty state: `[]`.
- Focused tests: 16 passed.

Correctness:

- Fused batch aggregate results exactly matched the equivalent four sequential
  single aggregate calls for both rows.
- The phase label remained
  `prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_block_partials`;
  Goal2822 changes the native implementation underneath that generic phase.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No v2.5 release claim is authorized.
- This is internal v2.5 RTNN-path runtime evidence only. It authorizes the
  narrow conclusion that fusing the small-row block-partial batch launch is a
  correct generic optimization and modestly faster than Goal2821 on the measured
  heterogeneous sweep.

## Interpretation

Goal2822 confirms the right performance diagnosis for heterogeneous sweeps:
removing kernel-launch repetition matters, but it is not the only remaining
cost. The fused kernel gives a clean 8-11% batch improvement while preserving
exact aggregate results. The remaining overhead is now mostly useful neighbor
work plus one fused launch and one compact partial download/reduction.

The next generic target should be chosen carefully. More micro-launch cleanup is
unlikely to buy another large jump. Better candidates are CUDA graph replay for
repeated prepared workloads, device-side final reduction of block partials, or
event-ordered chaining into a partner consumer that avoids downloading compact
partials when the next stage also runs on device.
