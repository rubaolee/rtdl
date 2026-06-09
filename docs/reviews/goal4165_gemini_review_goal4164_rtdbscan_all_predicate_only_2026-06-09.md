# External Review Handoff: Goal4164 RT-DBSCAN All-Predicate-Only Mode

## Verdict: accept-with-boundary

### Review Summary:

Goal4164 introduces an explicit, user-selectable all-predicate-only mode for RT-DBSCAN. The implementation correctly exposes this mode without hidden dispatch, ensuring users are aware of its specific operational characteristics. A critical aspect of this change is its "fail-closed" mechanism for mixed predicate rows; the system explicitly raises a `ValueError` and guides users towards the appropriate fallback route (`optix_rt_core_grouped_stream_numba_column_signature_3d`). This robust error handling prevents incorrect application of the fast path.

The provided pod artifact comprehensively validates both the successful execution of the all-predicate-only mode and the correct invocation of the fail-closed logic, confirming its behavior on the specified `NVIDIA RTX 4000 Ada Generation, 550.127.05` at commit `d25eff118d8590068c5aa0ead9c557240ae3a06c`. Importantly, the implementation strictly adheres to the native engine/app boundary, leveraging existing generic primitives and metadata without introducing any DBSCAN-specific native ABI or semantics.

Furthermore, the documentation and artifacts consistently and clearly avoid any overclaiming regarding release readiness, broad RT-core speedup, route promotion, or whole-app speedup, maintaining transparency about the experimental and candidate nature of this mode.

### Answers to Questions:

1.  **Does Goal4164 expose the Goal4158 all-predicate fast path as an explicit user-selected mode without hidden dispatch?**
    Yes, Goal4164 explicitly exposes the `optix_rt_core_flags_cupy_predicate_direct_status_all_true_column_signature_3d` mode as a user-selected option. The documentation, benchmark application, and tests confirm that it is an explicit candidate route and explicitly disallows hidden dispatch (`"hidden_dispatch_allowed": False`).

2.  **Does the mode fail closed for mixed predicate rows, with a clear fallback to `optix_rt_core_grouped_stream_numba_column_signature_3d`?**
    Yes, the mode fails closed for mixed predicate rows. When `all_predicate_fast_path` is required but not observed, a `ValueError` is raised. The error message explicitly instructs users to use `optix_rt_core_grouped_stream_numba_column_signature_3d` for mixed predicate rows. The pod artifact's `road_sparse_many_noise_fail_closed` case demonstrates this behavior.

3.  **Does the pod artifact prove both branches on `NVIDIA RTX 4000 Ada Generation, 550.127.05` at commit `d25eff118d8590068c5aa0ead9c557240ae3a06c`?**
    Yes, the `docs/reports/goal4164_all_predicate_only_mode_pod.json` artifact confirms execution on the specified GPU and commit. It includes two cases: `clustered_all_true_min_neighbors_1` (success with `all_predicate_fast_path_observed: true`) and `road_sparse_many_noise_fail_closed` (error with `ValueError` and the correct fallback message), thereby proving both intended branches.

4.  **Does the implementation keep the native engine/app boundary intact and avoid adding DBSCAN-specific native ABI or semantics?**
    Yes, the implementation successfully maintains the native engine/app boundary. The changes are confined to the application layer, introducing an explicit mode and validation checks based on existing generic primitives. The benchmark application's metadata explicitly states `"native_dbscan_abi_added": False`, confirming no new DBSCAN-specific native ABI.

5.  **Does the report avoid overclaiming release readiness, broad RT-core speedup, route promotion, or whole-app speedup?**
    Yes, the report, `claim_boundary` metadata in the pod artifact, and the benchmark application's configuration all consistently and explicitly set flags like `release_authorized`, `public_speedup_claim_authorized`, `route_promotion_authorized`, and `whole_app_claim_authorized` to `false`. This clearly indicates that the mode is a candidate and does not overclaim its readiness or impact.
