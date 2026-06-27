# V4 Goal4758 Installed Wheel Smoke

Status: `passed`

This smoke validates the current V4.0 wheel from an installed package path.
It is intentionally no-CUDA: it checks the public V4 front door and planner
boundary after wheel installation rather than source-tree imports.

## Result

- wheel: `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\dist\goal4758_v4_release_candidate\rtdl_source_tree-4.0.0-py3-none-any.whl`
- install status: `passed`
- smoke status: `passed`
- venv removed: `True`
- matrix apps: `10`
- matrix rows: `30`
- measured partners: `cupy, numba, rtdl_native, torch`
- CuPy grouped-vector-sum plan: `certified_partner_measured_ready`
- Numba component-union plan: `tier2_measured_ready`

## Non-Authorization

This smoke does not authorize public V4.0 tagging, broad speedup wording,
blanket CuPy performance claims, arbitrary Numba callbacks, or true-zero-copy claims.
