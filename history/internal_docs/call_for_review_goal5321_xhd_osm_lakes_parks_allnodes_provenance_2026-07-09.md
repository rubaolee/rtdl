# Call For Review: Goal5321 X-HD OSM Lakes/Parks/AllNodes Provenance Search

Please strictly review Goal5321.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5321_osm_lakes_parks_allnodes_provenance_search.json
tests/goal5321_xhd_osm_lakes_parks_allnodes_provenance_test.py
history/internal_docs/goal5321_xhd_osm_lakes_parks_allnodes_provenance_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5301_non_graphics_dataset_provenance_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
```

## Goal5321 Summary

Author logs show:

```text
lakes.bz2.wkt -> parks.bz2.wkt
HDResult = 55.734275817871094
input point counts = 301,704,289 / 403,688,408
sections = auto_tune, eb_gpu, hybrid_gpu, rt_gpu
```

Public SpatialHadoop page shows OSM datasets exist:

```text
new All Nodes = 2.7B records, 24.9GB download
new Lakes     = 8.4M records, 2.7GB download
new Parks     = 10M records, 2.9GB download

old all_nodes = 1.7B points, 17GB download
old lakes     = 4.3M polygons, 798MB download
old parks     = 234K polygons, 34MB download
```

But Goal5321 finds no author input bytes, no hashes, no OSM planet snapshot,
no extraction/filter identity, and no deterministic conversion proof.

Exit label:

```text
osm_lakes_parks_allnodes_exact_provenance_not_found__snapshot_filter_blocked
```

## Review Questions

1. Does the author log evidence correctly prove workload existence but not input
   provenance?
2. Does the SpatialHadoop catalog evidence support public-source availability
   while still failing exact-input requirements?
3. Is it correct to classify the old Goal54 live-Overpass Australia slice as a
   bounded analogue only, not exact X-HD OSM reproduction?
4. Does Goal5321 correctly avoid using public catalog record counts as exact
   identity proof?
5. Is it correct that no POD is needed until concrete author files or accepted
   public snapshots appear?
6. Should OSM remain lower priority than already value-matched Level-B rows
   unless snapshot/filter/conversion evidence appears?
7. Are the forbidden claims complete?
8. Is the exit label acceptable?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5321_osm_snapshot_filter_blocked
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5321

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
2. ...
...
8. ...
```
