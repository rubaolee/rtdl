# Goal 278 Review: v0.5 Real KITTI Layout and Offset Support

Date: 2026-04-12
Reviewer: Gemini CLI

## Verdict

The implementation honestly and effectively supports the real KITTI raw-data layout and bounded frame offsets. It maintains full backward compatibility with the legacy toy directory structures while enabling production-ready acquisition from real-world datasets.

## Findings

- **Real KITTI Layout Support:** `src/rtdsl/rtnn_kitti.py` and `src/rtdsl/rtnn_kitti_ready.py` now correctly recognize both `velodyne/*.bin` and the real raw-data path `velodyne_points/data/*.bin`. Sequence name extraction correctly handles both cases by looking at the parent directory of the discovery anchor.
- **Bounded Frame Offsets:** The `start_index` parameter has been successfully introduced across the acquisition stack.
  - `select_kitti_bounded_frames` uses robust Python slicing (`records[start_index::stride][:max_frames]`) to implement the offset.
  - `write_kitti_bounded_package_manifest` correctly persists the `start_index` in the manifest, ensuring reproducibility.
- **Readiness Detection:** The `inspect_kitti_linux_source_root` function in `rtnn_kitti_ready.py` has been updated to search for `velodyne_points` in addition to the legacy `velodyne` directory, ensuring the readiness check works as expected on real Linux source trees.
- **Comprehensive Testing:**
  - `tests/goal270_v0_5_kitti_bounded_acquisition_test.py` includes a new test case `test_discover_frames_supports_real_kitti_raw_layout` using a simulated real KITTI tree.
  - `test_bounded_selection_obeys_start_index` verifies the offset logic.
  - `tests/goal277_v0_5_kitti_linux_ready_test.py` verifies that the readiness check correctly identifies real KITTI structures.
- **Backward Compatibility:** All existing tests for the legacy directory structure continue to pass, confirming that the "toy" dataset path is not broken.

## Risks

- **Low Risk:** The changes are additive and maintain support for the legacy layout.
- **Discovery Scope:** `rglob("*.bin")` is used for discovery. While this is effective, in extremely large directories with unrelated `.bin` files, it relies on the path filtering in `_kitti_frame_record_from_bin_path` to exclude noise. The current implementation correctly filters based on the presence of `velodyne` or `velodyne_points` in the path.

## Conclusion

Goal 278 is a successful maturation of the KITTI acquisition layer. The system is now capable of working directly with the real KITTI raw dataset layout on Linux and supports flexible frame selection via offsets, which is critical for creating partitioned query/search packages for validation.
