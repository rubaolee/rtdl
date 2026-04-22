# Goal 759: Gemini Flash Finish Review (RTX Cloud Benchmark Manifest)

Status: ACCEPT

## Reviewer's Verdict

The implemented solution for a machine-readable RTX cloud benchmark manifest for Goal 759 is **ACCEPTED**. It successfully addresses the stated objectives and provides a robust framework for future benchmarking efforts.

### Usefulness of the Manifest

The manifest is highly useful as a machine-readable contract for NVIDIA RTX cloud benchmark runs. It clearly defines the scope of each benchmark entry, including exact commands, app paths, scales, and crucial metadata such as OptiX performance class and benchmark readiness. This formalization is essential for:
- Preventing miscategorization during cloud runs.
- Ensuring consistency and accuracy in reporting.
- Optimizing the use of paid cloud GPU resources by focusing on relevant app paths.
- Providing a transparent, auditable record of what is being tested and what claims can be made.

The `purpose` and `global_preconditions` sections within the manifest itself (`goal759_rtx_cloud_benchmark_manifest.py`) further reinforce its utility by setting clear expectations and requirements for benchmark execution.

### Mechanical Tie to the Matrices

The manifest is robustly and mechanically tied to the definitions within `/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`. This linkage is verified by `tests/goal759_rtx_cloud_benchmark_manifest_test.py`, specifically the `test_manifest_entries_match_machine_readable_matrices` function. This test confirms that:
- `optix_performance_class` is directly populated from `rt.optix_app_performance_support(entry["app"]).performance_class`.
- `benchmark_readiness` is directly populated from `rt.optix_app_benchmark_readiness(entry["app"]).status`.
This direct programmatic relationship ensures that the manifest accurately reflects the current support and readiness statuses defined in the `app_support_matrix`, preventing manual discrepancies.

### Avoidance of Overclaiming RTX App Speedups

The manifest demonstrates a strong commitment to avoiding overclaiming RTX app speedups through several mechanisms:
- **Explicit `non_claim` Statements:** Each entry in the manifest includes a `non_claim` field that explicitly states what the benchmark results *cannot* claim, such as "not a broad RTX RT-core app speedup claim" for `database_analytics` or "not a full DBSCAN clustering... or whole-app RTX speedup claim" for `dbscan_clustering`.
- **`allowed_claim_today` Field:** The `allowed_claim_today` field provides precise boundaries for what can be claimed, often indicating that full speedup claims are pending further review or specific conditions (e.g., "candidate fixed-radius summary speedup claim only after phase-clean RTX rerun and review").
- **Categorization of `optix_performance_class`:** The `optix_performance_class` field, derived from the `app_support_matrix`, categorizes applications into classes like `PYTHON_INTERFACE_DOMINATED`, `CUDA_THROUGH_OPTIX`, or `HOST_INDEXED_FALLBACK`, which inherently manages expectations regarding RT-core utilization and overall app speedup potential.
- **Exclusion of Inapplicable Apps:** The `excluded_apps` section explicitly lists applications not suitable for RTX cloud benchmarking, along with clear reasons (e.g., "current OptiX path is CUDA-through-OptiX KNN rows, not RT-core traversal" for `hausdorff_distance`).
- **Clear `boundary` Clause:** The manifest includes a `boundary` statement: "The manifest is a benchmark contract only. It does not authorize RTX speedup claims; claims require successful cloud runs, phase-clean evidence, and independent review." This acts as an overarching safeguard against premature or unwarranted speedup claims.
- **Dedicated Test Cases:** The test `test_prepared_summary_apps_are_classified_without_whole_app_claims` and `test_excluded_cuda_through_optix_apps_do_not_enter_manifest_entries` confirm that the manifest logic correctly enforces these restrictions.

The combination of these explicit claims, categorizations, exclusions, and robust verification ensures that the manifest provides a clear and responsible approach to benchmarking, effectively mitigating the risk of overclaiming RTX app speedups.