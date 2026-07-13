# Call For Review - Goal5426 X-HD Full-Public WaterBodies->BlockGroups WKT Resource Gate

Please strictly review Goal5426.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5426_full_public_water_bg_wkt_resource_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5426_full_public_water_bg_wkt_resource_gate.json
tests/goal5426_full_public_water_bg_wkt_resource_gate_test.py
history/internal_docs/goal5426_xhd_full_public_water_bg_wkt_resource_gate_2026-07-10.md
history/internal_docs/call_for_review_goal5426_xhd_full_public_water_bg_wkt_resource_gate_2026-07-10.md
```

Relevant prior evidence:

```text
history/internal_docs/goal5425_xhd_full_public_water_bg_wkt_generation_feasibility_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/manifest.json
history/internal_docs/goal5311_xhd_water_bg_full_public_author_ingestion_result_2026-07-09.md
history/internal_docs/goal5314_xhd_water_bg_corrected_comparison_summary_2026-07-09.md
```

## Requested Verdict Labels

Approve:

```text
approve_goal5426_resource_gate_reuse_existing_goal5311_wkt_no_regeneration
```

Revise:

```text
revise_goal5426_resource_gate
```

Block:

```text
block_goal5426_resource_gate
```

## Review Questions

1. Does Goal5426 correctly use the POD wrapper rather than naked SSH?
2. Is the disk decision correct: `/tmp` free space is below the Goal5425
   recommended 6.283 GiB, so full WKT regeneration should not run on this POD?
3. Does Goal5426 correctly verify that existing Goal5311 full-public WKT files
   are present on the POD and match the local Goal5310 manifest by byte size and
   SHA256?
4. Is symlink reuse under `/tmp/xhd_goal5426/full_public_water_bg` acceptable,
   given that copying the multi-GiB files would waste disk and full generation
   is not safe on the current `/tmp` volume?
5. Does the report make clear that Goal5426 did not generate WKT, did not run
   author `hd_exec`, and did not run RTDL?
6. Does it keep the Goal5311 paper-log mismatch visible while also using
   Goal5314 as the correct paper-config denominator
   (`n_points_cell=8`, author `HDResult=0.8964367508888245`) for the next
   comparison?
7. Does it correctly preserve claim boundaries: no exact paper dataset, no
   geo Figure 5 reproduction, no full paper reproduction, no performance ratio,
   no route optimization, and no explicit `-lb` reopening?
8. Does the stop-loss G-1 block correctly classify this as a dataset/resource
   gate rather than row/hash/internal-stream app-artifact parity work?
9. Is the next recommended Goal5427 correctly limited to refreshing or
   consolidating RTDL-vs-Goal5314 paper-config scalar comparison on the existing
   full-public candidate, rather than comparing against the Goal5311 default
   author denominator?
10. Should Goal5426 close as a resource-gate success even though the
    full-generation safety gate itself failed, because existing complete WKT
    artifacts are hash-verified and reusable?

## Expected Answer Shape

Please answer with:

```text
Verdict: <one requested label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
10. ...
```
