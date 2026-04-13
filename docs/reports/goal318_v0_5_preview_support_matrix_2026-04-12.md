# Goal 318 Report: v0.5 Preview Support Matrix

Date:
- `2026-04-12`

Goal:
- create a current-state support matrix for the `v0.5` line

Implemented file:
- `docs/release_reports/v0_5_preview/support_matrix.md`

Source evidence:
- `docs/reports/goal315_v0_5_vulkan_3d_nn_closure_2026-04-12.md`
- `docs/reports/goal316_v0_5_linux_large_scale_embree_optix_vulkan_perf_2026-04-12.md`
- `docs/reports/goal317_v0_5_current_linux_4backend_nn_perf_report_2026-04-12.md`
- earlier already closed CPU/oracle, Embree, OptiX, and PostGIS `v0.5` NN
  slices
- bounded macOS Embree 3D correctness rerun on the current worktree
- bounded Windows Embree 3D correctness rerun in
  `C:\Users\Lestat\work\rtdl_v05_crossplat_probe`

What this file does:
- provides one current preview support matrix for the active `v0.5` line
- records the current backend and platform roles in a release-facing form
- keeps the Linux backend ordering explicit
- keeps the Windows/macOS and PostGIS honesty boundaries explicit
- records the newly verified bounded Windows/macOS Embree correctness status

Most important matrix statements:
- Linux is the primary validation platform for the `v0.5` 3D nearest-neighbor
  line
- the current honest Linux preview backend line includes:
  - Python reference
  - native CPU / oracle
  - PostGIS as external anchor
  - Embree
  - OptiX
  - Vulkan
- Windows and local macOS are explicitly bounded and are not being used to
  claim current large-scale nearest-neighbor performance closure
- Windows and local macOS are still allowed into the preview support surface as
  bounded Embree correctness platforms for the 3D nearest-neighbor trio
- the current Linux same-scale ordering is:
  - OptiX
  - Vulkan
  - Embree
  - PostGIS

Important honesty boundary:
- this is a preview support matrix, not a final `v0.5` release sign-off
- it does not claim final cross-platform backend maturity
- it does not upgrade Windows or macOS into large-scale performance platforms
- it does not turn PostGIS into a target production backend

Verification notes:
- local macOS bounded Embree 3D correctness run:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal298_v0_5_embree_3d_fixed_radius_test tests.goal299_v0_5_embree_3d_bounded_knn_test tests.goal300_v0_5_embree_3d_knn_test`
  - `Ran 10 tests`
  - `OK`
- Windows bounded Embree 3D correctness run:
  - `py -3 -m unittest tests.goal298_v0_5_embree_3d_fixed_radius_test tests.goal299_v0_5_embree_3d_bounded_knn_test tests.goal300_v0_5_embree_3d_knn_test`
  - `Ran 10 tests`
  - `OK`

Conclusion:
- Goal 318 gives the active `v0.5` line a current release-facing support matrix
- it is technically closed pending saved review
