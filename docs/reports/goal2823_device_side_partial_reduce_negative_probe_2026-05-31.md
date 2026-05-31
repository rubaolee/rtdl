# Goal2823 Device-Side Partial Reduce Negative Probe

Date: 2026-05-31

Verdict: reject-as-default; keep Goal2822 fused batch path.

Goal2823 tested a natural follow-up to Goal2822: reduce request-indexed block
partials on device and download only one aggregate row per request. The idea was
generic and app-agnostic, but the RTX A5000 evidence was mixed and too small to
justify the extra kernel and implementation complexity.

## Tested Change

The tested commit was `eaf393c1060e31c39177d1b6a8d3193d311784bb`.

It added:

- `fixed_radius_neighbors_3d_ranked_aggregate_partials_reduce`;
- `g_frn3d_ranked_aggregate_partials_reduce`;
- a second device kernel after the fused Goal2822 batch kernel.

The current branch reverts that implementation and keeps the simpler Goal2822
path as the default.

## Pod Evidence

Artifacts are saved under
`docs/reports/goal2823_rtnn_device_side_batch_partial_reduce_pod/`.

| Points | Goal2822 batch median sec | Goal2823 tested median sec | Change vs Goal2822 | Verdict |
| ---: | ---: | ---: | ---: | --- |
| 32768 | 0.000272061 | 0.000274855 | 0.990x | slightly slower |
| 65536 | 0.000829070 | 0.000812536 | 1.020x | tiny improvement |

Both rows preserved exact agreement with the equivalent sequential aggregate
calls and used a clean source checkout (`source_dirty: []`). The problem is not
correctness; it is that the performance signal is too small and inconsistent.

## Interpretation

The host partial download/reduction was not the next material bottleneck. At
these sizes the extra device reduction launch roughly cancels the smaller
download, hurting 32K slightly and helping 65K only marginally. The better
current default is Goal2822: one fused request/query block kernel plus compact
host reduction of a small partial array.

The next RTNN target should not be another partial-reduction micro-probe. Better
candidates are CUDA graph replay for repeated prepared calls, deeper
event-ordered chaining into device consumers, or a stronger single-request path
that reduces native launch/setup overhead.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No v2.5 release claim is authorized.
- Goal2823 is a negative/mixed internal probe and should not be promoted as the
  current implementation.
