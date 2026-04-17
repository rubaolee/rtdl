# Goal 313: Linux 32768 Backend Table on Expanded KITTI Data

Purpose:
- formalize the first same-scale backend table on the expanded KITTI data pool
  added after Goal 312
- use the larger duplicate-free `2011_09_26_drive_0014_sync` pair at
  `32768 x 32768`
- report large-scale backend timings for:
  - PostGIS
  - Embree
  - OptiX
- keep the Vulkan boundary explicit instead of implying 3D point
  nearest-neighbor support that is not yet closed

Success criteria:
- a checked-in script exists for the large-scale Embree-vs-OptiX run on the
  `32768` saved packages
- a checked-in script exists for the same-package PostGIS timing run
- the report records the same-scale backend table on the larger `0014_sync`
  pair
- the report states clearly which parity claims are closed at this scale and
  which ones still rely on previously closed smaller-scale anchors
- Gemini review is saved in the repo
- Codex consensus note is saved in the repo
