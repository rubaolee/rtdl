# V4 Advanced Surface Teaching Pass - 2026-06-27

## Purpose

The public tutorial programs already had small concept examples for RT-shaped
relations and continuations. The remaining risk was that advanced device-array
examples could still look like opaque API smoke tests: call one prepared
function, print JSON, and leave the learner unable to connect it back to the
programming model.

This pass tightened that layer without changing engine behavior or performance
claims.

## Public Files Updated

| File | Action |
| --- | --- |
| `examples/tutorial_programs/fixed_radius_torch_device_arrays.py` | Added teaching context for point columns, radius-neighbor rows, and threshold continuation. |
| `examples/tutorial_programs/point_group_nearest_witness_torch_device_arrays.py` | Added teaching context connecting nearest-witness output to NN and ranked-summary tutorials. |
| `examples/tutorial_programs/ray_triangle_any_hit_flags_torch_device_arrays.py` | Added teaching context for ray/triangle hit rows and any-hit flags. |
| `examples/tutorial_programs/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | Added teaching context for hit rows plus weighted-sum continuation. |
| `examples/tutorial_programs/primitive_grouped_i64_reduction_torch_device_arrays.py` | Added teaching context for primitive payload rows and grouped integer reductions. |
| `examples/tutorial_programs/closest_hit_grouped_argmin_torch_device_arrays.py` | Added teaching context for grouped closest-witness selection. |
| `examples/tutorial_programs/aabb_index_all_ops_count.py` | Added teaching context for AABB predicate rows and count outputs. |
| `examples/tutorial_programs/README.md` | Added an advanced-surface bridge table mapping each advanced script to its concept tutorial. |
| `tutorials/current/07_benchmark_apps.md` | Added the concept-to-surface bridge so users know how to read `teaching_context`. |

## Exit Checks

- All seven advanced scripts were run with `--dry-run`.
- Each dry-run now emits a `teaching_context` section.
- The added public wording avoids internal project process language.

## Remaining Standard Gate

Run the full public-doc scan, public tutorial tests, release packaging tests,
universe gate, catalog gate, and clean-tag gate before tagging or pushing this
state.
