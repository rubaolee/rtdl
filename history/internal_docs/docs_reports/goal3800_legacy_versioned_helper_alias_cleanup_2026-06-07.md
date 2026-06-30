# Goal3800 Legacy Versioned Helper Alias Cleanup

Date: 2026-06-07

## Purpose

Goal3800 addresses the first low-risk item in the future TODO entry for legacy
versioned helper names. The problem was not native-engine leakage: the native
surface remains app-agnostic. The problem was learner/app-facing Python helper
names that still made the active generic typed-stream front door look like a
`v2_5` or `v2_6` artifact.

## Scope

This goal covers two active benchmark examples that expose the old names most
directly:

| Example | Legacy helper/route preserved | Current alias added | Reason |
| --- | --- | --- | --- |
| Triangle counting | `v2_5_plan`, `v2_6_numba_compact_mask_plan`, `run_triangle_counting_v2_6_numba_compact_mask_preview(...)` | `primitive_first_plan`, `segmented_compact_mask_numba_plan`, `run_triangle_counting_segmented_compact_mask_numba_preview(...)` | The implementation already routes through generic scalar summaries or generic segmented typed-stream compact-mask continuation. |
| Spatial RayJoin | `v2_6_numba_compact_mask_plan`, `run_rayjoin_v2_6_numba_compact_mask_preview(...)` | `primitive_first_plan`, `segmented_compact_mask_numba_plan`, `run_rayjoin_segmented_compact_mask_numba_preview(...)` | The implementation already treats Numba as a generic compact-mask continuation over caller-owned candidate rows. |

## Design Decision

The old helpers were not renamed in place. They remain available because earlier
reports, tests, and artifacts depend on those names. The new names are current
aliases that express the real contract:

- `primitive_first_plan`: the fused RTDL primitive remains preferred when the
  scalar summary already covers the workload.
- `segmented_compact_mask_numba_plan`: Numba is a user-selected partner
  continuation over generic candidate ids plus a boolean keep mask.

This keeps the user-facing direction cleaner without breaking historical
evidence.

## Boundaries

- No native-engine code changed.
- No release, package-install, zero-copy, or public speedup claim is authorized.
- The old versioned constants remain stable protocol/artifact identifiers.
- This goal does not declare all legacy versioned helper names cleaned. It only
  closes the two compact-mask benchmark entry points that were safe to alias.

## Validation

- `py -3 -m py_compile` on the two edited benchmark apps.
- `tests.goal3800_legacy_versioned_helper_alias_cleanup_test`
- Existing compact-mask wiring tests for Goals2999 and 3002 remain compatible.
