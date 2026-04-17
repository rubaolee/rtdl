# Goal 294: KITTI Native RTDL vs PostGIS Performance

Purpose:
- measure the new native 3D RTDL fixed-radius path against PostGIS on the same
  duplicate-free KITTI packages
- separate the Python truth path from the native performance story
- record whether native RTDL materially narrows or reverses the earlier
  PostGIS advantage

Success criteria:
- the benchmark uses the same duplicate-free KITTI package selection path
- the report records:
  - RTDL Python reference time
  - RTDL native oracle time
  - PostGIS time
  - cuNSearch time
  - parity status for RTDL native, PostGIS, and cuNSearch
- the report states the honest bounded conclusion about RTDL native versus
  PostGIS

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
