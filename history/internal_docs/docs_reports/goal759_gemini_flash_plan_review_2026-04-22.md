# Goal 759: Gemini Flash Plan Review (RTX Cloud Benchmark Manifest)

Status: ACCEPTED

## Reviewer's Verdict

The proposed plan for a machine-readable RTX cloud benchmark manifest is **ACCEPTED**.

### Usefulness of the Manifest

The manifest is highly useful and necessary. By formalizing which app paths should be benchmarked and explicitly defining permissible claims, it will prevent accidental miscategorization during cloud runs, ensure consistency in reporting, and provide a clear, machine-readable contract for benchmarking efforts. This will lead to more efficient use of paid cloud GPU resources and more accurate performance claims.

### Avoidance of Overclaiming RTX Speedups

The plan demonstrates a strong and commendable commitment to avoiding overclaiming RTX speedups. This is evidenced by:

- **Explicit Performance Categorization:** The manifest leverages the `rtdsl.optix_app_performance_matrix()` and `rtdsl.optix_app_benchmark_readiness_matrix()` to classify apps, including categories like `OPTIX_TRAVERSAL_PREPARED_SUMMARY` and `CUDA_THROUGH_OPTIX`.
- **Limited Claims for Partial Accelerations:** For apps where only a component benefits from OptiX traversal (e.g., `outlier_detection`, `dbscan_clustering`), the plan explicitly states "no whole-app speedup claim" or "no full DBSCAN speedup claim." This directly aligns with the detailed `allowed_claim` notes in `app_support_matrix.py`.
- **Exclusion of Non-RTX-Core Candidates:** Apps like Hausdorff, ANN, and Barnes-Hut are correctly excluded from RTX-core benchmarking candidates due to their current implementation being CUDA-through-OptiX or Python-dominated, rather than pure RT-core traversal.
- **Robust Verification Steps:** The proposed verification process, which includes checking manifest entries against the machine-readable matrices and ensuring no excluded `cuda_through_optix` apps enter the RTX claim set, further reinforces the commitment to accurate and honest claims.
- **Phase-Gating for Flagship Candidates:** Even for the "cleanest traversal flagship candidate" (`robot_collision_screening`), the plan acknowledges it is still "phase-gated," preventing premature, broad speedup claims.

The clarity and detail provided in both the plan document and the `app_support_matrix.py` effectively safeguard against misleading performance claims.
