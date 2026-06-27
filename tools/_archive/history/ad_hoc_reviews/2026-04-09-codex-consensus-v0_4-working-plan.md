# Codex Consensus: v0.4 Working Plan

Date: 2026-04-09
Status: closed under 3-AI review

## Verdict

The working plan is coherent and executable.

The recommended `v0.4` line is a nearest-neighbor release built around
`fixed_radius_neighbors` first and `knn_rows` second, with a dataset ladder and
baseline ladder that keep the milestone in RTDL's non-graphical core lane.

## Main points

- The 9-goal count is justified because it separates:
  - contract design
  - truth path
  - backend closure
  - external baseline work
  - release-facing docs and audit
- Natural Earth, NYC Street Tree Census, and Geofabrik together form a
  realistic open-data ladder from tutorial scale to dense real-world subsets.
- `scipy.spatial.cKDTree` is the strongest default external CPU baseline.
- PostGIS should support the release with bounded SQL comparisons, but should
  not become the central identity or truth path for the new workload family.

## Final closure note

Claude and Gemini both agreed with the main plan shape.

The only meaningful sharpening from external review is:

- keep the 9-goal ladder as written
- but allow Goal 8 to split into separate OptiX and Vulkan goals if execution
  reality demands it

That is now the accepted working rule for the `v0.4` build line.
