# RTDL Post-v0.5 Review Follow-up — 2026-04-14

Reviewer: Claude Sonnet 4.6
Session: Continuation of the April 14 post-v0.5 code review (context-compaction follow-up)
Prior report: `docs/reports/claude_v0_5_post_release_review_2026-04-14.md`

---

## Purpose

This session resumed work after a context-compaction boundary in the April 14 review session. Two items were carried forward from that session:

1. Verify and resolve four pre-existing test failures in `goal265` / `goal267` (field rename `tier` → `reproduction_tier`).
2. Restore the review test file `tests/claude_v0_5_post_release_review_test.py`, which was written during the prior session but lost at the compaction boundary.

---

## Actions Taken

### 1. Pre-existing `goal265` / `goal267` failures — resolved (already fixed in repo)

The April 14 report identified four test failures caused by `RtnnMatrixEntry.tier` being renamed to `reproduction_tier` (now an enum). Both test files were read and found to already use `reproduction_tier` — the fix had been applied to the repo before this session resumed.

Confirmed clean:

```
PYTHONPATH=src:. python3 -m unittest \
  tests.goal265_v0_5_rtnn_dataset_registry_test \
  tests.goal267_v0_5_rtnn_reproduction_matrix_test -v
# Ran 12 tests — OK
```

### 2. Restored `tests/claude_v0_5_post_release_review_test.py`

The file was absent from the worktree. It was recreated from the source modules reviewed in the April 14 session. The test suite was adapted to the actual `RtnnBoundedComparisonResult` field set in the worktree (which omits `distance_abs_tol` / `distance_rel_tol` relative to the review snapshot).

**42 tests across 6 classes:**

| Class | Tests | Focus |
|---|---|---|
| `LayoutTypesTest` | 13 | empty layout rejection, `require_fields`, 3D geometry types (`Point3DLayout`, `Triangle3DLayout`, `Ray3DLayout`, `Points3D`, `Triangles3D`, `Rays3D`), `field_to_dict`, scalar sizes |
| `RtnnPerfAuditTest` | 6 | identical rows, missing pair, extra pair, symmetric mismatch, empty rows, positional mismatch |
| `RtnnKittiValidationTest` | 9 | select validation errors (zero/negative max_frames, stride, start_index), source config status, package round-trip, manifest kind rejection, resolve missing root |
| `CuNSearchLivePrecisionTest` | 8 | compile flags (float/double), driver radius/k_max embedding, `f`-suffix on float literals, double distance computation, precision mode detection from `CMakeCache.txt` |
| `RtnnComparisonNotesTest` | 2 | `RtnnBoundedComparisonResult` field set, duplicate-guard blocked note shape |
| `KittiReadySampleTruncationTest` | 4 | sample capped at 5, `status=ready` when bins present, `status=empty` when no bins, `status=missing` when dir absent |

```
PYTHONPATH=src:. python3 -m unittest tests.claude_v0_5_post_release_review_test -v
# Ran 42 tests in 0.016s — OK
```

---

## Full Suite Result

```
PYTHONPATH=src:. python3 -m unittest \
  tests.goal265_v0_5_rtnn_dataset_registry_test \
  tests.goal266_v0_5_rtnn_baseline_registry_test \
  tests.goal267_v0_5_rtnn_reproduction_matrix_test \
  tests.goal269_v0_5_cunsearch_adapter_skeleton_test \
  tests.goal270_v0_5_kitti_bounded_acquisition_test \
  tests.goal271_v0_5_kitti_bounded_loader_test \
  tests.goal272_v0_5_kitti_point_package_test \
  tests.goal273_v0_5_cunsearch_response_parser_test \
  tests.goal274_v0_5_bounded_fixed_radius_comparison_test \
  tests.goal275_v0_5_cunsearch_live_driver_test \
  tests.goal276_v0_5_live_cunsearch_comparison_contract_test \
  tests.goal277_v0_5_kitti_linux_ready_test \
  tests.goal282_cunsearch_compiled_driver_test \
  tests.goal286_cunsearch_duplicate_guard_test \
  tests.goal287_kitti_duplicate_free_selector_test \
  tests.goal328_v0_5_layout_types_name_collision_test \
  tests.claude_v0_5_post_release_review_test
# Ran 102 tests in 0.998s — OK

PYTHONPATH=src:. python3 -m unittest discover -s tests -p "*.py"
# exit code 0 — full suite clean
```

---

## Verdict

**All pre-existing failures resolved. Review test file restored. Full suite passes.**

The post-v0.5 implementation slice remains in the PASS state documented in the April 14 report. No new findings.

---

## Remaining risks (unchanged from April 14 report)

1. `rtnn_cunsearch_live` is Linux + CUDA only. Live end-to-end path (nvcc compile + execute) untestable locally.
2. PostGIS 3D baselines untestable without a live PostGIS 3D instance.
3. `_read_kitti_frame_points` numpy branch gives generic reshape error for non-multiple-of-16 files (F-4, low).
4. Hardcoded `"demo/Demo"` binary path in `rtnn_comparison` stored in request JSON (F-3, cosmetic).
