# Goal 278: v0.5 Real KITTI Layout And Offset Support

Purpose:
- make the bounded KITTI acquisition layer work against the real KITTI raw layout on Linux
- stop assuming a toy `velodyne/*.bin` tree when the real dataset uses `velodyne_points/data/*.bin`
- add a supported frame offset so bounded query/search packages can come from different real frames

Success criteria:
- KITTI readiness check reports `ready` on the real Linux source tree
- KITTI frame discovery works against the real raw layout
- bounded manifest writing supports a non-negative `start_index`
- tests cover both the legacy toy fixtures and the real raw-data directory shape

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
