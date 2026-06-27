# Handoff: Claude Review For Goal2801 Hausdorff/X-HD Canonical Entrypoint

Please perform an independent read-only Claude review of Goal2801 and write the review to:

`docs/reviews/goal2801_claude_review_hausdorff_xhd_canonical_entrypoint_2026-05-31.md`

## Files To Inspect

- `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py`
- `tests/goal2801_hausdorff_xhd_v25_canonical_entrypoint_test.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `docs/reports/goal2801_hausdorff_xhd_v2_5_canonical_entrypoint_2026-05-31.md`
- `docs/reports/goal2801_pod_artifacts/hausdorff_xhd_v25_canonical_entrypoint_4096.json`
- `docs/reports/goal2801_pod_artifacts/hausdorff_xhd_v25_canonical_entrypoint_4096.stdout`

## Review Questions

1. Does Goal2801 provide a real canonical exact Hausdorff entrypoint rather than another scattered method note?
2. Does the entrypoint compare the RTDL/OptiX exact witness path with the same-contract CuPy grid exact baseline?
3. Is the report honest that RTDL/OptiX is correct and uses RT cores but is much slower than CuPy grid on this 4K fixture?
4. Does the manifest avoid overclaiming Triton, public speedup, X-HD paper reproduction, or native app customization?
5. Are app-specific Hausdorff/X-HD policies kept outside the native engine contract?
6. Is clean-from-Git rerun correctly identified as pending before final evidence closure?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
