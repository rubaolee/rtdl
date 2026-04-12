### Verdict

The implementation for Goal 261 successfully and accurately achieves the stated purpose. The code slice correctly identifies the paths where 3D point geometry payloads would otherwise silently degrade to 2D behavior in the native backend packers and inserts explicit, honest barriers instead.

### Findings

- **Embree Backend:** The `pack_points` function successfully intercepts `_CanonicalPoint3D` instances and raises a `ValueError`. Additionally, the `_pack_for_geometry` method checks if `expected_dimension == 3` for `points` and raises an explicit error prior to prepared native execution.
- **OptiX Backend:** Mirrors the Embree implementation accurately. Both `pack_points` and `_pack_for_geometry` intercept 3D points and raise appropriate errors that clearly communicate the lack of native support.
- **Vulkan Backend:** Correctly updates `_pack_for_geometry` to intercept 3D point inputs. It relies on the shared `pack_points` imported from the Embree runtime to catch explicit `_CanonicalPoint3D` records, which guarantees uniform contract enforcement across all three hardware backends.
- **Honesty Gap Closed:** The error messages added are explicit about *why* the failure occurs (e.g., "the v0.5 3D point nearest-neighbor line is not native-online yet"). This prevents silent truncation of the `z` coordinate and perfectly aligns with the project's honesty principles.
- **Test Coverage:** The `goal261_v0_5_native_3d_point_contract_test.py` file exhaustively covers the newly added exception barriers across all three runtimes for both point packing and prepared path resolution.

### Risks

- There are minimal to no risks introduced by this slice. The changes are strictly bounded to throwing exceptions for an unsupported geometry state. No existing 2D point workflows or kernels are affected by these checks.
- *Minor observation:* The Vulkan backend imports `pack_points` directly from the Embree runtime. If a user were to somehow directly invoke that packing function through a Vulkan context, they might see an "Embree point packing..." error string. However, since the primary entry point `_pack_for_geometry` was updated with a Vulkan-specific error message, users will receive the correct context during standard execution, rendering this a non-issue.

### Conclusion

Goal 261 is technically correct, properly scoped, and effectively prevents the silent degradation of 3D point inputs to 2D representations. The implementation honors the repository's strict contract maturity model by ensuring that native execution explicitly and honestly fails for 3D points prior to the C++/accelerated implementations being built. The slice is robust and complete.
