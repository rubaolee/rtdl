# Goal 317: Current Linux 4-Backend Nearest-Neighbor Performance Report

Purpose:
- consolidate the current Linux nearest-neighbor backend state into one explicit
  four-backend report
- present the current large-scale Linux ordering across:
  - PostGIS
  - Embree
  - Vulkan
  - OptiX
- keep the backend-role and correctness boundaries explicit instead of letting
  a performance table blur them

Success criteria:
- the report is derived only from already closed Linux performance slices
- the report includes the current same-scale `32768 x 32768` table wherever the
  backend data is available
- the report makes the PostGIS role explicit:
  - correctness/timing anchor
  - not the target production runtime
- the report makes the PostGIS full-3D `knn_rows` boundary explicit:
  - honest timing anchor
  - not an indexed 3D KNN acceleration claim
- the report states the current backend ordering clearly

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
