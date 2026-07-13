# Goal4995: Sort Backend And Run-Bounds Probe No-Go

Date: 2026-07-04

## Purpose

After Goal4994, the top4 County x Zipcode prepared/query-many writer-free binary route reached a measured median of about `0.3665s`.  The remaining visible hot-path components were mostly device xsect sort and grouped carrier construction.

Goal4995 tested two narrow candidates before attempting any larger implementation:

1. Replace the device bitonic xsect sort with the existing CPU/NumPy lexsort reference while keeping the device-columnar reprojection route.
2. Merge the `run_start` / `run_end` table generation into a single pass after device sort.

Both candidates were app-layer probes only.  They did not change `src/rtdsl/**` or `src/native/**`.

## Baseline

The relevant prior best result is:

- Artifact: `history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4994_prepared_reprojection_arrays_repeat_top4.json`
- Route: prepared operator session, bounded exact LSI device columns, point-location device face columns, fast scaled-point pack, prepared vertex points, prepared reprojection segment arrays, device sort, compiled group.
- Median writer-free hot time: `0.3665195722132921s`
- Median LSI phase: about `0.0034s`
- Median downstream floor: about `0.3613s`
- Structural anchors: `lsi_row_count = 428322`, `descriptor_pair_count = 15014`

This remains the current best v2.14.3 top4 prepared/query-many binary-route evidence.

## Probe 1: CPU Lexsort Backend

Artifact:

- `history/internal_docs/goal4995_sort_backend_probe_artifacts_2026-07-04/goal4995_cpu_sort_top4.json`

Result:

- Median writer-free hot time: `3.4125294033437967s`
- Best writer-free hot time: `2.793653905391693s`
- Median LSI phase: `0.0030484087765216827s`
- Median downstream floor: `3.4095007553696632s`
- Representative measured CPU sort components:
  - `sort_map0_cpu_columnar_sec`: about `1.26s`
  - `sort_map1_cpu_columnar_sec`: about `1.27s`
- Structural anchors remained stable:
  - `lsi_row_count = 428322`
  - `descriptor_pair_count = 15014`

Decision:

`no_go_cpu_lexsort_backend`

The CPU lexsort route is dramatically slower than the existing device bitonic sort route.  It should not be promoted.  The temporary CLI/backend experiment was removed from the working app code after the probe.

## Probe 2: Single-Pass Run Bounds

Artifacts:

- `history/internal_docs/goal4995_sort_backend_probe_artifacts_2026-07-04/goal4995_run_bounds_top4.json`
- `history/internal_docs/goal4995_sort_backend_probe_artifacts_2026-07-04/goal4995_run_bounds_top4_repeat2.json`

Results:

First run:

- Median writer-free hot time: `3.2565175853669643s`
- Best writer-free hot time: `2.924699515104294s`

Second run:

- Median writer-free hot time: `6.340412588790059s`
- Best writer-free hot time: `5.263754049316049s`

Structural anchors remained stable, but the performance was much worse than Goal4994.  The slowdown also affected carrier and sort phases in ways not explained by the small run-bounds change alone, so the POD state likely included runtime/cache noise.  Nevertheless, the result is enough to reject this candidate: it did not produce a reliable improvement and must not be promoted.

Decision:

`no_go_single_pass_run_bounds`

The run-bounds change was reverted from the app code after the probe.

## Code State After Probe

The working app was restored to the Goal4994-style route:

- default device bitonic sort retained;
- no `--xsect-sort-backend` CLI remains;
- no `_run_bounds_table` replacement remains;
- local tests pass;
- POD structure test passes after restoring the app file.

Validation:

- Local: `py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- Local: `PYTHONPATH=src py -m unittest tests.goal4990_binary_repeat_protocol_test tests.goal4988_lsi_device_columns_direct_numba_handoff_test`
- POD: `PYTHONPATH=src python -m unittest tests.goal4990_binary_repeat_protocol_test`

Restored-route POD check:

- Artifact: `history/internal_docs/goal4995_sort_backend_probe_artifacts_2026-07-04/goal4995_restored_best_route_check_top4.json`
- Median writer-free hot time: `0.47885632887482643s`
- Best writer-free hot time: `0.3498430587351322s`
- Best measured-row key components:
  - `lsi_bounded_exact_pair_id_device_columns_sec`: `0.0030132606625556946s`
  - `sort_map0_device_columnar_sec`: `0.030118906870484352s`
  - `sort_map1_device_columnar_sec`: `0.11717956885695457s`
  - `grouped_compiled_columnar_carrier_construction_sec`: `0.12041576392948627s`
  - `grouped_descriptor_pair_count_consumer_sec`: `0.015320558100938797s`

The restored route returned to the Goal4994 performance regime.  The higher median reflects first measured carrier warmup variance; the best measured row confirms the no-go code was not left in the hot path.

## Current Conclusion

Goal4995 is a negative but useful result.

The two cheap candidates did not improve the prepared/query-many binary route.  The current best evidence remains Goal4994's `~0.3665s` top4 prepared/query-many hot route.

The remaining meaningful optimization targets are now narrower:

1. Device sort remains a visible component, but replacing it with CPU lexsort is wrong.
2. Grouped carrier construction is still a visible app-layer CPU/Numba component.
3. Any next implementation should start from measurement of a real remaining component, not from speculative micro-edits.

## Exit Label

`completed_goal4995_sort_backend_probe_no_go__retain_goal4994_best_route`
