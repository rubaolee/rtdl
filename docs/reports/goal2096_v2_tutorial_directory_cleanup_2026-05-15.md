# Goal2096 v2.0 Tutorial Directory Cleanup

Date: 2026-05-15

## Purpose

GitHub renders the `docs/tutorials/` directory as a public learner shelf. The
directory still exposed older-version tutorial names, old release-line language,
and stale commit messages, which made the v2.0-facing documentation look
historical instead of current.

This pass makes the active tutorial directory single-version and v2.0-facing.
Older tutorial material is preserved under history.

## File-by-File Findings And Operations

| File | Finding | Operation |
| --- | --- | --- |
| `docs/tutorials/README.md` | Tutorial ladder mixed current partner tutorials with old inventory-style examples. | Rewrote as `RTDL v2.0 Tutorials`, added a current learning ladder, claim boundary, and legacy archive link. |
| `docs/tutorials/v2_app_building.md` | Missing current app-building tutorial for Python+partner+RTDL. | Added a v2.0 app-building tutorial explaining Python, partner arrays, RTDL primitive contracts, backend work, and continuation. |
| `docs/tutorials/v0_8_app_building.md` | Old-version filename was visible in the active tutorial directory. | Moved to `docs/history/legacy_tutorials/v0_8_app_building.md`. |
| `docs/history/legacy_tutorials/README.md` | Needed an archive doorway for moved tutorial history. | Added a short legacy tutorial archive index. |
| `docs/tutorials/db_workloads.md` | Opened as an old DB release-line tutorial and contained goal-named historical tests. | Reframed as current bounded columnar-payload tutorial; moved historical validation context behind archives. |
| `docs/tutorials/graph_workloads.md` | Opened with old graph release-line language and old release links. | Reframed around frontier/edge traversal rows and v2.0 graph-summary boundaries. |
| `docs/tutorials/nearest_neighbor_workloads.md` | Opened with old nearest-neighbor release-line language and historical performance report wording. | Reframed around fixed-radius/K-closest/Hausdorff composition and current v2.0 claim boundary. |
| `docs/tutorials/segment_polygon_workloads.md` | Opened with old segment/polygon release-line language and stale goal references. | Reframed around current v2.0 segment/polygon rows, streaming witness columns, and bounded claims. |
| `docs/tutorials/feature_quickstart_cookbook.md` | Included historical goal/performance references in learner recipes. | Replaced old evidence narration with current v2.0 evidence-packet boundary links. |
| `docs/tutorials/hello_world.md` | Content was still valid but GitHub showed it as old. | Added a current v2.0 tutorial-path note. |
| `docs/tutorials/sorting_demo.md` | Content was still valid but GitHub showed it as old. | Added a current v2.0 tutorial-path note. |
| `docs/tutorials/rendering_and_visual_demos.md` | Content was still valid but GitHub showed it as old. | Added a current v2.0 tutorial-path note. |
| `docs/tutorials/partner_anyhit.md` | Already v2-facing. | Added a sequencing note pointing learners toward the OptiX partner-column tutorial. |
| `docs/tutorials/partner_optix_zero_copy_anyhit.md` | Already v2-facing. | Added a sequencing note pointing back to the first partner tutorial. |

## Boundary

This is documentation cleanup, not a final v2.0 release. The tutorial path now
teaches the v2.0 pre-release candidate surface while preserving the project
redline: final v2.0 still requires the strict 3-AI consensus gate.
