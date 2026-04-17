# Goal 319: v0.5 Cross-Platform Embree Correctness Matrix

Purpose:
- close the bounded cross-platform correctness claim for the Embree 3D
  nearest-neighbor trio
- prove Windows and local macOS Embree agree with the same RTDL truth/oracle
  semantics already validated on Linux
- avoid any cross-platform performance claim

Success criteria:
- record a bounded correctness matrix covering:
  - Linux
  - local macOS
  - Windows
- use the already-closed Embree 3D test trio:
  - `tests.goal298_v0_5_embree_3d_fixed_radius_test`
  - `tests.goal299_v0_5_embree_3d_bounded_knn_test`
  - `tests.goal300_v0_5_embree_3d_knn_test`
- keep the Linux truth chain explicit:
  - Python reference
  - native CPU / oracle
  - supporting PostGIS checks where applicable
- state clearly that this is a correctness matrix, not a performance matrix

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
