# Call For Review - Goal5313 X-HD WaterBodies/BG Author Config Alignment

Please strictly review Goal5313:

```text
history/internal_docs/goal5313_xhd_water_bg_author_config_alignment_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_n_points_cell_alignment_summary.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_author_water_bg_full_public_n_points_cell_8.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_witness_distance_probe.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_source_13579843.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_bg_target_22441127.json
Paper-reproduction-apps/x-hd-paper/scripts/inspect_xhd_wkt_point_by_index.py
tests/goal5313_xhd_water_bg_n_points_cell_alignment_test.py
```

## Context

Goal5311 ran author `hd_exec` on the Goal5310 full-public WaterBodies ->
BlockGroups WKT candidate and got:

```text
HDResult = 0.8970130085945129
NumPointsPerCell = 15
```

The paper-branch log value for the same named pair is:

```text
HDResult = 0.8964367508888245
num_points_per_cell = 8
```

Goal5312 ran RTDL on the same full-public candidate and got:

```text
RTDL exact-witness HDResult = 0.8964380566690101
source_id = 13,579,843
target_id = 22,441,127
```

Goal5313 reruns author `hd_exec` on the same full-public WKT candidate with
`-n_points_cell=8` and obtains:

```text
HDResult = 0.8964367508888245
```

It also extracts the RTDL witness coordinates and records:

```text
float64 distance = 0.8964380566690101
float32 distance = 0.8964367508888245
```

## Review Questions

1. Does the evidence support the conclusion that Goal5311's apparent author
   mismatch was caused by using the author default `n_points_cell=15` rather
   than the paper-log `n_points_cell=8` configuration?
2. Does the Goal5313 author rerun actually match the paper-branch HDResult
   exactly under `-n_points_cell=8`?
3. Does the witness probe prove that RTDL's reported witness pair is
   self-consistent in float64?
4. Does the witness probe prove that the same witness pair's float32 distance
   equals the author/paper value?
5. Is it correct to interpret the remaining RTDL-vs-author difference as a
   float64-vs-float32 boundary for this witness, while still refusing to claim
   identical internal numeric behavior?
6. Does the new inspection helper remain app-owned and avoid adding X-HD
   semantics to RTDL core?
7. Are the tests sufficient to pin the `n_points_cell` correction and witness
   numeric boundary?
8. Does the report correctly avoid claiming exact paper WKT recovery, Figure 5
   completion, or performance parity?
9. Should Goal5311/5312 be superseded by a new author-paper-config comparison
   summary rather than edited away?
10. Is Goal5314's proposed next step appropriate?

## Expected Answer Shape

```text
Verdict: approve_goal5313_xhd_water_bg_author_config_alignment
or
Verdict: revise_goal5313_...

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to the 10 questions:
1. ...
...
10. ...
```
