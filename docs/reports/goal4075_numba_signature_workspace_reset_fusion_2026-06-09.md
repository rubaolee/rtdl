# Goal4075 Numba Signature Workspace Reset Fusion

Date: 2026-06-09

## Status

Implemented locally; pod validation pending.

## Purpose

Goal4074 showed that RT-DBSCAN's recommended RT-core grouped-stream route is dominated by the native grouped-union pass, but it also confirmed a stable ~5 ms Numba component-signature continuation. The pod stdout also emitted a `NumbaPerformanceWarning: Grid size 1`, caused by scalar workspace reset launches in the signature path.

Goal4075 fuses those scalar resets into the existing large label-count workspace reset launch:

- before: one launch for `label_counts`, plus one-block launches for `flag_true_count` and `negative_label_count`;
- after: one `zero_signature_workspace_kernel` launch clears `label_counts` and both scalar counters.

This is a generic partner-continuation cleanup. It does not alter the native grouped-union primitive, does not add app vocabulary, and does not change RT-DBSCAN semantics.

## Expected Effect

This should remove the one-block Numba reset warning and slightly reduce the signature-continuation overhead. Goal4074 already showed that the main bottleneck is still native grouped-union traversal, so this is not expected to produce a large whole-route speedup.

## Boundary

This change does not authorize release, public speedup, broad RT-core speedup, whole-app acceleration, true-zero-copy, automatic partner selection, app-specific native-engine logic, or native ABI claims.

