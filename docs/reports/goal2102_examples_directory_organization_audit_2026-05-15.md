# Goal2102 Examples Directory Organization Audit

Status: complete.

Purpose: review `examples/` as a learner would see it in GitHub, then clean the
directory so it is organized, precise, and not frustrating.

## Findings And Operations

| Area | Finding | Operation |
| --- | --- | --- |
| Root example listing | Old-version DB demo files were visible beside current v2.0-facing examples. | Moved them to `examples/internal/archived_apps/` and updated current imports. |
| Apple RT helper listing | Retired Apple RT scenario helpers were visible beside the unified Apple app. | Moved them to `examples/internal/archived_apps/` and kept `rtdl_apple_rt_demo_app.py` as the public wrapper. |
| Examples index | The index was long and mixed inventory, history, and guidance in one flow. | Rewrote `examples/README.md` around short path, directory map, and job-oriented public examples. |
| Archived helpers | Internal helpers had no local archive doorway. | Added `examples/internal/archived_apps/README.md`. |
| Apple unavailable path | Running the Apple demo on non-macOS could print a destructor warning after the expected skip. | Initialized the prepared Apple RT 2D handle defensively before backend loading. |
| Public docs/tests | Existing tests expected older catalog wording and old helper paths. | Updated tests and release-facing command list to match the organized public wrappers. |

## Final Shape

| Location | Reader meaning |
| --- | --- |
| `examples/rtdl_*.py` | Current public examples and app wrappers. |
| `examples/visual_demo/` | Visual Python apps that use RTDL for query work. |
| `examples/reference/` | Canonical kernels and helper generators. |
| `examples/generated/` | Preserved generated bundles. |
| `examples/internal/` | Internal experiments and compatibility helpers. |
| `examples/internal/archived_apps/` | Runnable archived helpers imported by current unified wrappers or retained for audit tests. |

## Validation

| Check | Result |
| --- | --- |
| Root `examples/*.py` old-version/goal-name scan | clean |
| Examples README local links | clean |
| `rtdl_database_analytics_app.py --backend cpu_python_reference --scenario regional_dashboard --output-mode summary` | pass |
| `rtdl_apple_rt_demo_app.py` on non-macOS | pass with expected Apple RT unavailable status |
| Focused examples/docs tests | pass |

## Boundary

This is an organization and learner-surface cleanup. It does not change the
public runtime contract or authorize new performance claims.

