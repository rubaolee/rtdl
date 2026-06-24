# Goal 281: v0.5 PostGIS 3D Fixed-Radius Support

Purpose:
- add an honest 3D PostGIS comparison path for the fixed-radius nearest-neighbor workload
- keep the scope bounded to what the repo can support cleanly now
- avoid overclaiming 3D PostGIS KNN before a real contract exists

Success criteria:
- additive 3D PostGIS SQL exists for fixed-radius neighbors
- additive 3D PostGIS table preparation exists for `Point3D`
- additive 3D fixed-radius runner exists and is exported through `rtdsl`
- tests prove parity against the Python truth path on bounded 3D point sets
- docs state clearly that this goal does not yet close live PostGIS-backed KITTI validation

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
