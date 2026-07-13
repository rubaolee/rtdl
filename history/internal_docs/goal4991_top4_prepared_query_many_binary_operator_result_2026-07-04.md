# Goal4991 - Top4 Prepared/Query-Many Binary Operator Repeat Result

Date: 2026-07-04

## Objective

Extend Goal4990 from the public County x Soil sample to the larger top4 County x Zipcode representative input.

This goal checks whether the same-process prepared/query-many writer-free binary route is real at larger scale, while preserving the boundary:

- fresh one-shot remains separate;
- warmup rows remain visible;
- measured rows are reported as prepared/query-many evidence only;
- no author-performance ratio is claimed for top4.

## Input Reconstruction

The current POD did not contain top4 data. I rebuilt it from the existing project staging script:

```bash
PYTHONPATH=src:. \
.venv/bin/python scripts/goal4970_stage_top4_arcgis_cdb.py \
  --output-dir Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis \
  --page-size 2000 \
  --host-label pod_157_157_221_29_25248
```

Staged data:

| Dataset | Features | Chains | Points | Edges | Bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| top4_county | 441 | 1,612 | 1,706,639 | 1,705,027 | 59,780,073 |
| top4_zipcode | 7,035 | 10,144 | 9,993,104 | 9,982,960 | 350,084,995 |

Artifact:

```text
history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4970_top4_cdb_summary.json
```

## Runtime Command

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIB=/root/rtdl_goal4988/build/librtdl_optix.so \
RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR=/root/rtdl_goal4988/Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/cache \
.venv/bin/python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb \
  --right Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb \
  --pair-name top4_county_zipcode \
  --device-columnar \
  --bounded-exact-lsi-device-columns \
  --bounded-exact-lsi-capacity 1000000 \
  --point-location-device-face-columns \
  --fast-scaled-point-pack \
  --compiled-group \
  --warmup-runs 1 \
  --repeat 3 \
  --summary Paper-reproduction-apps/rayjoin-paper/_runs/top4_arcgis/rtdl/goal4990_repeat_protocol_top4.json
```

Artifact:

```text
history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4990_repeat_protocol_top4.json
```

## Result

Warmup row, reported but excluded:

| Row | writer_free_hot_sec | LSI phase | downstream floor | carrier |
| --- | ---: | ---: | ---: | ---: |
| warmup 1 | 4.411411 | 2.728375 | 1.683036 | 0.819108 |

Measured rows:

| Row | writer_free_hot_sec | LSI phase | downstream floor | carrier |
| --- | ---: | ---: | ---: | ---: |
| measured 1 | 2.480488 | 1.550248 | 0.930241 | 0.098602 |
| measured 2 | 2.373019 | 1.567577 | 0.805442 | 0.098137 |
| measured 3 | 2.417124 | 1.611089 | 0.806035 | 0.099076 |

Median:

```text
median_writer_free_hot_sec  = 2.41712380386889
median_lsi_phase_sec        = 1.5675766840577126
median_downstream_floor_sec = 0.8060348182916641
best_writer_free_hot_sec    = 2.3730190582573414
```

Structural consistency:

```text
single_lsi_row_count = true
lsi_row_count = 428322
single_descriptor_pair_count = true
descriptor_pair_count = 15014
```

Device-column handoff stayed active:

```text
bounded_exact_lsi_numba_direct_handoff_used = true
lsi_pair_input_device_resident = true
lsi_pair_host_to_device_copy_used = false
```

## Interpretation

The prepared/query-many route is not a public-sample accident. It also works on the larger top4 representative input.

However, the larger input exposes a real remaining steady-state floor:

- LSI producer remains the largest measured hot component: median `~1.57s`.
- Downstream floor remains material: median `~0.81s`.
- Carrier construction is no longer the dominant floor after warmup: median `~0.099s`.

This means:

1. Goal4990/4991 successfully formalize and verify the prepared/query-many binary operator route.
2. The route is substantially better than the fresh/warmup row, but top4 is still not "solved."
3. The next optimization target is not carrier construction.
4. The next target is the remaining hot work:
   - exact/bounded LSI producer cost;
   - downstream device-resident continuation beyond the current host/Numba boundary.

## Claim Boundary

Allowed:

- "On top4 County x Zipcode, the prepared/query-many writer-free binary route has median `2.417s` after one reported warmup run."
- "The route keeps LSI pair ids device-resident into the Numba reprojection handoff."
- "Carrier construction is no longer the largest steady-state cost on top4."

Not allowed:

- "v2.14.3 one-shot top4 overlay is `2.417s`."
- "RTDL matches author performance on top4."
- "Prepared/query-many evidence replaces fresh one-shot evidence."
- "The full overlay is device-resident end-to-end."

## Next Work

The next goal should attack the largest top4 steady-state component: LSI producer.

Candidate directions:

1. Decompose `lsi_bounded_exact_pair_id_device_columns_sec` on top4 in the prepared repeat protocol.
2. Determine whether the `~1.57s` is:
   - native traversal / intersection work;
   - host-side setup/ensure;
   - capacity initialization;
   - output compaction / row-count extraction;
   - synchronization.
3. Only after that decomposition choose implementation.

Do not return to carrier micro-optimization unless the decomposition shows carrier again dominates a larger workload.

## Exit Label

```text
completed_top4_prepared_query_many_binary_operator_repeat_protocol__lsi_still_dominates
```
