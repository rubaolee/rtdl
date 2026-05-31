# Goal2815 RTNN Prepared Aggregate Workspace

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2815 targets the small-row overhead left after Goal2813 and Goal2814. The
large-scale RTNN sweep showed that the generic unsorted bounded top-k summary
path scales well, but the 32K and 65K uniform rows still paid too much fixed
runtime overhead. Inspection showed one avoidable cost: every aggregate call
allocated a tiny device aggregate buffer even though the prepared fixed-radius
search handle already owns the lifetime of the reusable GPU-side state.

Goal2815 moves that aggregate buffer into the prepared fixed-radius handle as a
reusable prepared-handle aggregate workspace. The workspace is still cleared for
each synchronous aggregate call, so results and lifecycle semantics are
unchanged. The optimization is generic: it applies to fixed-radius ranked
summary aggregates and does not introduce any RTNN-specific native engine path.

## Code Changes

| File | Change |
| --- | --- |
| `src/native/optix/rtdl_optix_workloads.cpp` | Added `d_ranked_aggregate` to `PreparedFixedRadiusNeighborsGrid3D` and reused it in both prepared-query and non-resident-query aggregate paths. |
| `tests/goal2815_rtnn_prepared_aggregate_workspace_test.py` | Guards the generic workspace ownership, A/B artifacts, and claim boundary. |
| `docs/reports/goal2815_rtnn_prepared_aggregate_workspace_pod/*.json` | A/B pod artifacts for pre-workspace and post-workspace 32K/65K rows with repeat 5. |

## Pod Validation

Build/test probe before commit:

```text
base checkout: 1551b8bfdd0fe9f326351ba896738f3b3a6c929b plus local Goal2815 patch
GPU: NVIDIA RTX A5000, 570.211.01
OptiX build: pass
focused tests: 10 passed
```

Clean current-head benchmark:

```text
commit: 95218cf43094ee3fdc2826c4f5ea07cb175bbeb4
source_dirty: []
OptiX build: pass
focused tests: 8 passed
```

Pre-workspace A/B baseline:

```text
commit: 8dacc429105d33f1e08bb43fef4c843d266bba75
source_dirty: []
repeat: 5
```

## A/B Median Timing

| Points | Distribution | Pre-workspace RTDL (s) | Goal2815 RTDL (s) | RTDL change | Goal2815 CuPy/RTDL |
| ---: | --- | ---: | ---: | ---: | ---: |
| 32768 | uniform | 0.000108866 | 0.000095278 | 1.143x | 0.797x |
| 32768 | clustered | 0.004882446 | 0.004706190 | 1.037x | 2.540x |
| 32768 | shell | 0.000147998 | 0.000136988 | 1.080x | 1.919x |
| 65536 | uniform | 0.000175621 | 0.000155801 | 1.127x | 0.885x |
| 65536 | clustered | 0.022085239 | 0.018604644 | 1.187x | 2.533x |
| 65536 | shell | 0.000379033 | 0.000349855 | 1.083x | 7.794x |

All post-workspace rows pass, preserve exact aggregate agreement with the CuPy
grid opponent, keep `upload_sec: 0.0`, and retain median timing. The improvement
is bounded but consistent. It helps the exact weak rows we wanted to improve,
especially 32K/65K uniform, but it does not fully remove small-row overhead:
32K and 65K uniform rows still do not beat CuPy.

## Interpretation

This goal confirms that some of the remaining small-row gap was generic runtime
setup overhead, not traversal semantics. Reusing the aggregate workspace gives a
modest win without changing the primitive contract or introducing app-specific
logic.

The remaining small-row gap likely needs a deeper generic execution contract:
batched aggregate calls, a reusable zeroed workspace pool, CUDA graph capture,
or event-ordered aggregate chaining. Those are v2.5 runtime design ideas, not
RTNN-specific shortcuts.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized before external review.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No package-install claim is authorized.
- No native app-specific engine customization is introduced.

Goal2815 is accepted as a small generic runtime improvement and a useful
diagnostic step. It is not sufficient on its own to close every small-row
performance gap.
