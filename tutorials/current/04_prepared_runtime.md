# Measured Runtime Surfaces

V4's important runtime idea is measured generic fused operators.

Instead of exposing app-specific kernels, V4 exposes operator surfaces such as:

- fixed-radius count-threshold;
- closest-hit grouped argmin;
- ray/triangle any-hit flags;
- primitive grouped-i64 reduction;
- point-group nearest witness;
- ray/triangle any-hit weighted sum;
- fixed-radius graph component union;
- AABB all-ops count.

Run the portable catalog check:

```powershell
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Try dry-run examples without CUDA:

```powershell
py -3 examples\v4\fixed_radius_torch_device_arrays.py --dry-run
py -3 examples\v4\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
py -3 examples\v4\aabb_index_all_ops_count.py --dry-run
```

Dry runs prove API reachability and claim-boundary flags. GPU performance
requires the recorded hardware path and exact benchmark command.

Next: [Measurement Boundaries](05_measurement_boundaries.md)
