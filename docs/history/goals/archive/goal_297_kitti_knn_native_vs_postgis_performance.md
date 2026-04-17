# Goal 297: KITTI 3D KNN Native RTDL vs PostGIS Performance

Purpose:
- measure the new native 3D `knn_rows` path against the Python truth path and
  an honest external PostGIS 3D KNN baseline
- verify that the native/oracle 3D `knn_rows` path is both parity-clean and
  materially faster than PostGIS on duplicate-free KITTI packages
- keep the baseline boundary explicit: this PostGIS path is a correctness anchor
  for 3D KNN, not a claim of indexed 3D KNN acceleration

Success criteria:
- a real 3D PostGIS `knn_rows` baseline exists in the repo
- the benchmark uses duplicate-free KITTI package selection
- the report records:
  - RTDL Python reference time
  - RTDL native oracle time
  - PostGIS time
  - parity status for RTDL native and PostGIS
- the report states the honest bounded conclusion about native RTDL versus
  PostGIS on the KITTI 3D KNN line

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
