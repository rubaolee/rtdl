# Goal4075 Numba Signature Workspace Reset Fusion

Date: 2026-06-09

## Status

Implemented, RTX 4000 Ada pod probe recorded, tests pass.

## Purpose

Goal4074 showed that RT-DBSCAN's recommended RT-core grouped-stream route is dominated by the native grouped-union pass, but it also confirmed a stable ~5 ms Numba component-signature continuation. The pod stdout also emitted a `NumbaPerformanceWarning: Grid size 1`, caused by scalar workspace reset launches in the signature path.

Goal4075 fuses those scalar resets into the existing large label-count workspace reset launch:

- before: one launch for `label_counts`, plus one-block launches for `flag_true_count` and `negative_label_count`;
- after: one `zero_signature_workspace_kernel` launch clears `label_counts` and both scalar counters.

This is a generic partner-continuation cleanup. It does not alter the native grouped-union primitive, does not add app vocabulary, and does not change RT-DBSCAN semantics.

## Expected Effect

This should remove the one-block Numba reset warning and slightly reduce the signature-continuation overhead. Goal4074 already showed that the main bottleneck is still native grouped-union traversal, so this is not expected to produce a large whole-route speedup.

## Pod Evidence

Artifacts:

- `docs/reports/goal4075_numba_signature_workspace_reset_fusion_pod_after.json`
- `docs/reports/goal4075_numba_signature_workspace_reset_fusion_pod_after.stdout.txt`
- `docs/reports/goal4075_numba_signature_workspace_reset_fusion_pod_summary.json`

Before/after comparison against the Goal4074 pre-fusion artifact:

| Profile | before elapsed sec | after elapsed sec | after/before | before signature sec | after signature sec | warning after |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `clustered3d_65536` | 0.093321 | 0.093612 | 1.003x | 0.005205 | 0.005362 | absent |
| `road3d_65536` | 0.036245 | 0.035123 | 0.969x | 0.005428 | 0.004882 | absent |

Interpretation:

- The one-block Numba warning is gone.
- Correctness remains stable by component-size signature.
- This does not materially change the recommended route; clustered timing is within noise and road timing improves modestly.
- Goal4074's main conclusion still holds: native grouped-union traversal remains the real bottleneck.

## Boundary

This change does not authorize release, public speedup, broad RT-core speedup, whole-app acceleration, true-zero-copy, automatic partner selection, app-specific native-engine logic, or native ABI claims.
