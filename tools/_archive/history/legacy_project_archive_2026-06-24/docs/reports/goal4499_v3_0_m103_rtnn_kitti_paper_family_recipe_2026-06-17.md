# Goal4499 / V3 M103 RTNN KITTI Paper-Family Recipe

## Conclusion

A real KITTI source root is available, and at least one bounded paper-family recipe can now feed same-contract author RTNN, RTDL OptiX, and Embree/CPU runs.

This is deliberately not an exact RTNN paper reproduction. It creates an auditable KITTI-family recipe boundary so later performance packets can compare author RTNN, RTDL OptiX, and Embree/CPU on the same bounded input without pretending the paper's exact frame recipe is known.

## Recipe Matrix

| Target | Target Points | Selected Points | Frames | Status | Paper Equivalence |
|---|---:|---:|---:|---|---|
| `KITTI-1M` | 1,000,000 | 1,000,000 | 9 | `bounded_family_recipe_ready` | `bounded_family_recipe_not_exact_paper_recipe` |
| `KITTI-6M` | 6,000,000 | 6,000,000 | 50 | `bounded_family_recipe_ready` | `bounded_family_recipe_not_exact_paper_recipe` |
| `KITTI-12M` | 12,000,000 | 12,000,000 | 99 | `bounded_family_recipe_ready` | `bounded_family_recipe_not_exact_paper_recipe` |
| `KITTI-25M` | 25,000,000 | 13,178,862 | 108 | `insufficient_source_points` | `bounded_family_recipe_not_exact_paper_recipe` |

## Claim Boundary

- Bounded same-contract comparison is allowed only when a row is `bounded_family_recipe_ready`.
- Paper-reproduction wording remains disallowed.
- Synthetic uniform/shell/clustered rows remain distribution evidence only and are not substitutes for these KITTI recipes.

Artifacts:

- `docs/reports/goal4499_v3_0_m103_rtnn_kitti_paper_family_recipe_2026-06-17.json`
- `docs/reports/goal4499_v3_0_m103_rtnn_kitti_paper_family_recipe_2026-06-17.jsonl`
