# RayJoin Section 5.7 Overlay 8/8 Status Report

Date: 2026-06-14

Update: the Block x Water RTDL OptiX result in this report has been superseded by the later directed-segment point-location face-id device-column optimization. See `docs/reports/goal4376_overlay_face_id_columns_2026-06-14/rayjoin_overlay_point_location_optimization_report_2026-06-14.md`. The 8/8 data-availability boundary remains unchanged: 2/8 measured, 6/8 blocked on missing exact Lakes/Parks inputs.

## Bottom Line

We now have an 8/8-capable Section 5.7 polygon-overlay runner for:

- author RayJoin RT code
- RTDL OptiX
- RTDL Embree

We executed the two exact-available full-scale US pairs on the pod. We do not yet have a completed 8/8 paper reproduction because the six Lakes/Parks exact inputs are not currently obtainable from the public paper/data links. Substituting a different OSM/Overpass extract would make the matrix look complete but would not be the RayJoin paper's Section 5.7 workload.

This is therefore a real 8/8 campaign scaffold plus a real 2/8 measured result, not a public-ready 8/8 reproduction.

## Protocol

Pod: NVIDIA RTX 4000 Ada Generation, driver 550.127.08.

Dataset root used on pod:

```text
/workspace/rayjoin_section57_data/cdb_topology
```

Benchmark protocol:

- author RT: process-level warmup 1, measured repeat 3, reported hot median
- RTDL OptiX/Embree: warmup 1, measured repeat 3, reported warm-cache median
- RTDL input provenance: `same_source_regenerated_cdb`
- RTDL packed cache: enabled
- timeout: 7200s per run

Important timing caveat: RayJoin paper Table 4 reports polygon-overlay processing time with preprocessing time in parentheses. The local author rows here are measured executable process wall times over regenerated/local CDB artifacts. They are useful for local author-vs-RTDL comparison, but should not be treated as a direct remeasurement of the paper's Table 4 numbers.

Paper source: RayJoin ICS'24, Section 5.7 and Table 4: https://gengl.me/public/publications/ics24.pdf

## Coverage

| Pair | Paper RayJoin proc (preproc) | Exact inputs available locally | Local results |
|---|---:|---:|---:|
| County x Zipcode | 0.12 (0.07) | yes | author RT, RTDL OptiX, RTDL Embree |
| Block x Water | 0.23 (0.12) | yes | author RT, RTDL OptiX, RTDL Embree |
| LKAF x PKAF | 0.01 (0.01) | no | blocked |
| LKAS x PKAS | 0.04 (0.05) | no | blocked |
| LKAU x PKAU | 0.01 (0.01) | no | blocked |
| LKEU x PKEU | 0.20 (0.20) | no | blocked |
| LKNA x PKNA | 0.25 (0.21) | no | blocked |
| LKSA x PKSA | 0.02 (0.01) | no | blocked |

Coverage result: 2/8 complete, 6/8 blocked on missing exact Lakes/Parks CDB inputs.

The unavailable paths are:

```text
point_cdb/lakes/Africa/lakes_Africa_Point.cdb
point_cdb/parks/Africa/parks_Africa_Point.cdb
point_cdb/lakes/Asia/lakes_Asia_Point.cdb
point_cdb/parks/Asia/parks_Asia_Point.cdb
point_cdb/lakes/Australia/lakes_Australia_Point.cdb
point_cdb/parks/Australia/parks_Australia_Point.cdb
point_cdb/lakes/Europe/lakes_Europe_Point.cdb
point_cdb/parks/Europe/parks_Europe_Point.cdb
point_cdb/lakes/North_America/lakes_North_America_Point.cdb
point_cdb/parks/North_America/parks_North_America_Point.cdb
point_cdb/lakes/South_America/lakes_South_America_Point.cdb
point_cdb/parks/South_America/parks_South_America_Point.cdb
```

Data-source check on 2026-06-14:

- Author repository README points users to ArcGIS, SpatialHadoop Lakes/Parks, and a Dryad preprocessed-dataset link; it does not include the full benchmark datasets in the repo: https://github.com/pwrliang/RayJoin
- Dryad paper share redirects to `/404`: https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA
- SpatialHadoop still lists Lakes/Parks datasets, but the four checked Google Drive download IDs for new/old Lakes/Parks return final `404 Not Found`: https://spatialhadoop.cs.umn.edu/datasets.html

## Performance Matrix

Times are seconds. `OptiX/Author` is RTDL OptiX total divided by local author RT hot median. `OptiX speedup over Embree` is Embree total divided by OptiX total.

| Pair | Author RT hot median | RTDL OptiX total | RTDL Embree total | OptiX/Author | OptiX speedup over Embree | RTDL LSI count |
|---|---:|---:|---:|---:|---:|---:|
| County x Zipcode | 5.614 | 5.819 | 9.954 | 1.04x slower | 1.71x faster | 181,629 |
| Block x Water | 28.088 | 42.380 | 34.905 | 1.51x slower | 0.82x, so Embree is 1.21x faster | 649,605 |
| LKAF x PKAF | blocked | blocked | blocked | n/a | n/a | n/a |
| LKAS x PKAS | blocked | blocked | blocked | n/a | n/a | n/a |
| LKAU x PKAU | blocked | blocked | blocked | n/a | n/a | n/a |
| LKEU x PKEU | blocked | blocked | blocked | n/a | n/a | n/a |
| LKNA x PKNA | blocked | blocked | blocked | n/a | n/a | n/a |
| LKSA x PKSA | blocked | blocked | blocked | n/a | n/a | n/a |

## Row Interpretation

County x Zipcode is the best current RTDL overlay story:

- RTDL OptiX is close to local author RT: 5.819s vs 5.614s.
- RTDL OptiX is clearly faster than RTDL Embree: 1.71x.
- Data movement is not the bottleneck: RTDL OptiX load/pack median is 0.061s.
- Public wording can say: on the available County x Zipcode row, RTDL OptiX reaches near parity with the author RT executable and beats the RTDL Embree CPU path.

Block x Water is not an RT-core speedup row:

- author RT is fastest: 28.088s.
- RTDL Embree is second: 34.905s.
- RTDL OptiX is slowest: 42.380s.
- Data movement is not the explanation: RTDL OptiX load/pack median is only 0.049s.
- The reversal is compute-shape driven. RTDL OptiX wins the LSI hot call versus Embree on this row, but loses badly on the massive vertex-PIP work:
  - RTDL OptiX LSI hot call: 9.61s
  - RTDL Embree LSI hot call: 15.93s
  - RTDL OptiX vertex PIP calls: 13.90s + 11.82s
  - RTDL Embree vertex PIP calls: 4.43s + 2.89s
- Public wording must not claim RT acceleration for Block x Water. The correct wording is: this row exposes a remaining RTDL OptiX compute/fusion weakness for overlay's vertex-location phase.

## Engineering Changes

Implemented/updated:

- `src/rtdsl/rayjoin_paper_suite.py`
  - added the full RayJoin Section 5.7 Table 4 manifest
  - marked `implemented_compute_optional_output` overlay rows as runnable
  - exposes the 8 overlay pairs and the paper reference timings
- `scripts/rayjoin_section57_overlay_matrix.py`
  - new 8/8 batch planner/runner/summarizer
  - supports author RT, RTDL OptiX, RTDL Embree
  - records skipped rows with exact missing-input reasons
  - records timeouts without aborting the full batch
  - runs author RT as repeated process-level warmup/repeat, not a single cold run
- `tests/goal4374_rayjoin_exact_paper_suite_test.py`
  - now covers the Section 5.7 manifest, runner planning, runnable overlay status, timeout handling, and author repeated-run behavior

Validation:

```text
py -3 -m py_compile src\rtdsl\rayjoin_paper_suite.py scripts\rayjoin_paper_reproduction_suite.py scripts\rayjoin_section57_overlay_matrix.py
py -3 -m unittest tests.goal4374_rayjoin_exact_paper_suite_test
python3 -m unittest tests.goal4374_rayjoin_exact_paper_suite_test  # on pod
```

All 22 RayJoin exact-suite tests passed locally and on the pod.

## Evidence Files

Primary local artifacts:

```text
docs/reports/goal4375_section57_overlay_8x8_2026-06-14/section57_overlay_8x8_plan_after_us_rebuild.json
docs/reports/goal4375_section57_overlay_8x8_2026-06-14/section57_overlay_8x8_summary_after_us_rebuild.json
docs/reports/goal4375_section57_overlay_8x8_2026-06-14/section57_overlay_county_zipcode_author_rt.json
docs/reports/goal4375_section57_overlay_8x8_2026-06-14/section57_overlay_county_zipcode_rtdl_optix.json
docs/reports/goal4375_section57_overlay_8x8_2026-06-14/section57_overlay_county_zipcode_rtdl_embree.json
docs/reports/goal4375_section57_overlay_8x8_2026-06-14/section57_overlay_block_water_author_rt.json
docs/reports/goal4375_section57_overlay_8x8_2026-06-14/section57_overlay_block_water_rtdl_optix.json
docs/reports/goal4375_section57_overlay_8x8_2026-06-14/section57_overlay_block_water_rtdl_embree.json
docs/reports/goal4375_section57_overlay_8x8_2026-06-14/section57_us_cdb_scan.json
```

## What Is Needed To Finish True 8/8

To finish the actual 8/8 reproduction, we need one of:

1. The RayJoin authors' preprocessed CDB package for the six Lakes/Parks pairs.
2. A valid mirror of the exact SpatialHadoop Lakes/Parks source used by the paper, plus a documented conversion path to the same per-continent CDB layout.
3. A new, explicitly labeled non-paper dataset campaign. This would be useful engineering work, but it must not be called the RayJoin Section 5.7 reproduction.

Once the missing exact inputs exist under the expected `point_cdb/lakes/...` and `point_cdb/parks/...` paths, the 8/8 runner can execute the full matrix without new benchmark-code work.

## Publication Conclusion

Do not close the RayJoin overlay app as a full 8/8 paper reproduction yet.

The honest closeout is:

- Section 5.7 8/8 infrastructure is complete.
- Same-source full-scale US overlay rows are complete for 2/8 pairs.
- County x Zipcode supports a positive RTDL OptiX story: near parity with author RT, faster than Embree.
- Block x Water does not support an RTDL OptiX acceleration claim: author RT and RTDL Embree are both faster than RTDL OptiX.
- The missing six rows are blocked by unavailable exact paper inputs, not by the runner or RTDL overlay machinery.
