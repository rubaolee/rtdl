### Verdict

The matrix implementation provides a strong, technically honest foundation that successfully separates exact reproduction from bounded approximations and extensions. However, it contains a logical coherency flaw: over-aggressive filtering completely excludes non-paper baselines from the matrix, making it impossible to apply the intended "nonpaper_comparison_only" label to any row.

### Findings

- **Technical Honesty:** Excellent. The matrix proactively prevents false claims of exact parity by strictly mapping `exact_reproduction_candidate` targets to the `blocked_on_exact_dataset_and_adapter` status, acknowledging that true replication is blocked until the underlying datasets and baseline adapters are perfectly aligned.
- **Labeling Preservation:** The code correctly reads `reproduction_tier` from the targets and maps them to accurate, distinct statuses (`planned_bounded_matrix`, `blocked_on_exact_dataset_and_adapter`, and `planned_rtdl_extension`), cleanly preserving the conceptual boundaries of the experiments.
- **Dataset-Packaging Isolation:** The logic within `rtnn_reproduction_matrix()` successfully prevents non-paper baseline libraries (`postgis` and `scipy_ckdtree`) from merging into `dataset_packaging` artifacts, satisfying the requirement to keep dataset rows strictly aligned with paper baselines.

### Risks

- **Dead Code and Coherency Flaw:** In `src/rtdsl/rtnn_matrix.py`, the generator explicitly skips `postgis` and `scipy_ckdtree` if the target artifact is either `dataset_packaging` or `paper_matrix`. Since *all* current experiment targets defined in `RTNN_EXPERIMENT_TARGETS` use one of these two artifacts, these non-paper baselines are entirely excluded from the generated matrix.
- **Unfulfilled Goal Scope:** The Goal 267 charter explicitly requires that the code "label matrix rows honestly" with `nonpaper_comparison_only`. Because the non-paper baselines are skipped and not appended to the matrix, the `_matrix_status_for` branch that returns `"nonpaper_comparison_only"` is effectively dead code. No rows will ever receive this label, failing that specific requirement.

### Conclusion

The matrix successfully lays down the rigorous framework needed for the `v0.5` line, treating technical honesty and provenance with the required strictness. The separation of exact, bounded, and extension tiers is highly coherent. However, a minor architectural fix is required to resolve the exclusion of non-paper baselines: to satisfy the goal of explicitly surfacing and labeling them as `"nonpaper_comparison_only"`, the filtering logic in `rtnn_reproduction_matrix()` must be relaxed (e.g., allowing them in `paper_matrix` rows just so they can be tagged as non-paper) or a new experiment target artifact specifically intended for broad comparisons must be introduced.
