# Goals650-656 Current-Main Any-Hit, Documentation, And Test Catch-Up

Date: 2026-04-20

Status: accepted catch-up history record.

This revision round records post-release current-main work after the public
`v0.9.5` tag. It is not a new public release tag.

## Covered Goals

| Goal | Commit | Result |
| --- | --- | --- |
| Goal650 | `a388fc8` | Added post-release current-main Vulkan native early-exit any-hit. |
| Goal651 | `7db47c1` | Added Apple RT 3D MPS nearest-intersection any-hit. |
| Goal652 | `3c93ef5` | Added Apple RT 2D MPS-prism native-assisted any-hit with exact 2D acceptance. |
| Goal653 | `fa15c3f` | Validated current-main Linux any-hit backends on `lestat-lx1`. |
| Goal654 | `a175eba` | Added public current-main support matrix. |
| Goal655 | `635a203` | Refreshed tutorial/example current-main backend boundaries. |
| Goal656 | `8d96924` | Recorded post-doc-refresh full local test gate. |

## Public Boundary

- Current public release remains `v0.9.5`.
- Current `main` includes post-release native/native-assisted any-hit
  improvements for Vulkan and Apple RT after rebuilding backend libraries.
- These current-main improvements are not retroactive `v0.9.5` tag claims.
- No broad any-hit speedup claim is made.
- Apple RT any-hit is not programmable shader-level Apple any-hit.
- `reduce_rows` remains a Python helper over emitted rows, not a native backend
  reduction.

## Evidence Files

- `docs/reports/goal650_vulkan_native_early_exit_anyhit_2026-04-20.md`
- `docs/reports/goal651_apple_rt_3d_anyhit_native_assisted_2026-04-20.md`
- `docs/reports/goal652_apple_rt_2d_native_anyhit_2026-04-20.md`
- `docs/reports/goal653_current_main_anyhit_linux_validation_2026-04-20.md`
- `docs/reports/goal654_current_main_support_matrix_2026-04-20.md`
- `docs/reports/goal655_tutorial_example_current_main_consistency_2026-04-20.md`
- `docs/reports/goal656_post_doc_refresh_full_local_test_2026-04-20.md`

## Final Test Gate

Goal656 recorded:

```text
Ran 1232 tests in 112.348s
OK (skipped=180)
```

The public command truth audit remained valid:

```json
{"command_count": 248, "public_doc_count": 14, "valid": true}
```

## Consensus

The covered goals were accepted under the standing 2+ AI consensus rule. The
latest closing gate, Goal656, was accepted by Codex and Gemini Flash.
