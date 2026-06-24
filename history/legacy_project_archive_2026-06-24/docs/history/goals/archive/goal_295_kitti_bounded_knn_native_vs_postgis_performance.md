# Goal 295: KITTI 3D Bounded-KNN Native RTDL vs PostGIS Performance

Purpose:
- measure the new native 3D `bounded_knn_rows` path against the Python truth
  path and an honest external PostGIS 3D bounded-KNN baseline
- verify that the newly closed native/oracle 3D bounded-KNN path is both
  parity-clean and meaningfully faster than PostGIS on duplicate-free KITTI
  packages
- keep the benchmark scope bounded to the current 3D bounded-radius KNN
  contract rather than overclaiming generic 3D KNN support

Success criteria:
- a real 3D PostGIS `bounded_knn_rows` baseline exists in the repo
- the benchmark uses duplicate-free KITTI package selection
- the report records:
  - RTDL Python reference time
  - RTDL native oracle time
  - PostGIS time
  - parity status for RTDL native and PostGIS
- the report states the honest bounded conclusion about native RTDL versus
  PostGIS on the KITTI 3D bounded-KNN line

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
