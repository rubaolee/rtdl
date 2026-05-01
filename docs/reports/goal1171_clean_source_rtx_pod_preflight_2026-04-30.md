# Goal1171 Clean-Source RTX Pod Preflight

Date: 2026-04-30

Dry run: `True`
Valid: `True`

## Checks

| Check | Result |
| --- | --- |
| `manifest_exists` | `True` |
| `runner_exists` | `True` |
| `manifest_has_eight_rows` | `True` |
| `runner_refuses_dirty_tree` | `True` |
| `source_clean` | `True` |
| `nvidia_smi_available` | `True` |
| `cuda_prefix_exists` | `True` |
| `nvcc_exists` | `True` |
| `optix_library_exists` | `True` |
| `geos_pkg_config_available` | `True` |
| `geos_c_library_available` | `True` |

## Blockers

None.

## Boundary

This preflight checks readiness for the clean-source Goal1170 RTX batch. It does not run benchmarks and does not authorize public speedup wording.
