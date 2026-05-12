# Goal1756 Embree Same-Surface Wall-Clock Column

## Verdict

`embree_same_surface_wall_clock_column_ready_without_public_speedup_claim`

This finishes the Embree column as same app-level command wall-clock evidence. It is broader than native subphase timing and includes process startup, input construction, native work, and JSON serialization. It must not be used as public speedup wording without separate review.

## Summary

- Rows: `16`
- Public claim authorized: `False`
- Release authorized: `False`
- `same_surface_app_wall_clock_ratio`: `16`

## Methodology Notes

- Both versions run through the same app-level CLI command for each row, then the adapter normalizes the elapsed wall-clock field into one schema.
- The current checkout requires tests/fixtures/rayjoin/br_county_subset.cdb for the segment-polygon examples; the fixture directory was synced to the Linux run root before the repaired pass.
- polygon_set_jaccard uses --copies 2000 for both versions because the current generic path raised MemoryError at the earlier --copies 20000 attempt.
- robot_collision_screening uses --pose-count 20000 for both versions because --pose-count 200000 remained CPU-bound for more than 26 minutes on v1.0 and was not a practical complete-column workload.

## Embree Column

| App | Classification | v1.0 sec | Current sec | v1.0/current |
| --- | --- | ---: | ---: | ---: |
| `service_coverage_gaps` | `same_surface_app_wall_clock_ratio` | 0.9904867269797251 | 1.035935202962719 | 0.956x |
| `event_hotspot_screening` | `same_surface_app_wall_clock_ratio` | 1.8040206279838458 | 1.7770651809987612 | 1.015x |
| `facility_knn_assignment` | `same_surface_app_wall_clock_ratio` | 65.99340750597185 | 70.07725688803475 | 0.942x |
| `road_hazard_screening` | `same_surface_app_wall_clock_ratio` | 0.8319314169930294 | 0.847240862029139 | 0.982x |
| `segment_polygon_hitcount` | `same_surface_app_wall_clock_ratio` | 0.22114389995113015 | 0.2558442230219953 | 0.864x |
| `segment_polygon_anyhit_rows` | `same_surface_app_wall_clock_ratio` | 0.2281380160129629 | 0.24203134997515008 | 0.943x |
| `graph_visibility_edges` | `same_surface_app_wall_clock_ratio` | 0.9583024149760604 | 1.004786464967765 | 0.954x |
| `graph_bfs` | `same_surface_app_wall_clock_ratio` | 0.4464125339873135 | 0.45997437002370134 | 0.971x |
| `graph_triangle_count` | `same_surface_app_wall_clock_ratio` | 0.6927562939818017 | 0.6963409219752066 | 0.995x |
| `hausdorff_distance` | `same_surface_app_wall_clock_ratio` | 105.03601461200742 | 107.03261061100056 | 0.981x |
| `ann_candidate_search` | `same_surface_app_wall_clock_ratio` | 37.14948011102388 | 44.54873568896437 | 0.834x |
| `barnes_hut_force_app` | `same_surface_app_wall_clock_ratio` | 3.3645453099743463 | 3.4010800230316818 | 0.989x |
| `polygon_pair_overlap_area_rows` | `same_surface_app_wall_clock_ratio` | 5.266816477000248 | 20.315425040957052 | 0.259x |
| `polygon_set_jaccard` | `same_surface_app_wall_clock_ratio` | 0.49160192400449887 | 6.2490841670078225 | 0.079x |
| `outlier_detection` | `same_surface_app_wall_clock_ratio` | 1.065373871999327 | 1.0746012580348179 | 0.991x |
| `robot_collision_screening` | `same_surface_app_wall_clock_ratio` | 717.8390749600367 | 715.4233178420109 | 1.003x |

## Boundary

These ratios answer the user's practical v1.0 customized-engine versus current generic-engine Embree question at the same app-command level. They do not replace Goal1750's stricter native/subphase same-contract summary and do not authorize public performance wording.
