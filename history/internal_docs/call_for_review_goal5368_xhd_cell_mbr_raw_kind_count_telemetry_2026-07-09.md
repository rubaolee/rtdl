# Call For Review - Goal5368 X-HD Cell-MBR Raw Kind-Count Telemetry

Please strictly review Goal5368.

Primary result document:

```text
history/internal_docs/goal5368_xhd_cell_mbr_raw_kind_count_telemetry_result_2026-07-09.md
```

Primary result artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json
```

POD probe artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5368_dragon_asian_lb256_author_radius_noinline_kind_count_pod.json
```

Files changed:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_prelude.h
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5368_cell_mbr_raw_kind_count_telemetry.py
tests/goal5368_cell_mbr_frontier_kind_count_telemetry_test.py
tests/goal5368_lb_raw_kind_count_artifact_test.py
```

Validation:

```text
py -m py_compile src/rtdsl/optix_runtime.py
py -m py_compile src/rtdsl/partner_continuations.py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5368_cell_mbr_raw_kind_count_telemetry.py
py -m unittest tests.goal5368_cell_mbr_frontier_kind_count_telemetry_test tests.goal5368_lb_raw_kind_count_artifact_test tests.goal5367_lb_author_radius_probe_test tests.goal5366_lb_denominator_reconciliation_test tests.goal5365_rtdl_lb_counterpart_gate_test tests.goal5364_lb_trace_gate_author_pair_contract_test tests.goal5363_lb_heavy_offload_semantics_audit_test
Ran 22 tests OK

POD:
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
make build-optix
small POD smoke raw_frontier_kind_counts={"1":1,"2":1,"3":1}
Dragon -> AsianDragon count-only probe completed
```

## Key Numbers

Author `lb256`:

```text
OffloadingSize = 27133990
Radius         = 79.2156982421875
```

RTDL author-radius no-inline/count-only raw telemetry:

```text
attempted all kinds     = 589961522
raw_frontier_kind1_rows = 284979633
raw_frontier_kind2_rows = 304981889
raw_frontier_kind3_rows = 0
```

Comparison:

```text
raw kind2 / author OffloadingSize = 11.239846738352892
row_count_parity = false
```

## Review Questions

1. Does Goal5368 implement a generic native raw frontier kind-count telemetry
   feature rather than an X-HD-specific core primitive?
2. Are the v3 telemetry fields available before row download / host sort /
   host unique, including overflow/count-only mode?
3. Does the Python `allow_overflow_telemetry=True` path remain opt-in while
   preserving the default fail-closed overflow behavior?
4. Is the POD small smoke sufficient to show the telemetry distinguishes
   kind1/kind2/kind3 rows?
5. Does the Dragon -> AsianDragon probe correctly show that no-inline raw
   kind2 rows are much larger than author `OffloadingSize`?
6. Is the conclusion justified: author `OffloadingSize` is not simply all raw
   RTDL cell-MBR kind2 rows under the same scalar radius?
7. Does the report correctly refuse explicit `-lb` support, row-count parity,
   same-denominator memory parity, Figure 7/11 reproduction, performance ratio,
   exact paper dataset reproduction, and full X-HD paper reproduction?
8. Is the proposed next target correct: align author iterative queue state
   (`in_queue_idx`, `cmin2/current best`, radius schedule, raw offload queue
   emission), not more scalar-radius tuning?

Expected verdict labels:

```text
approve_goal5368_raw_kind_count_telemetry__author_lb_denominator_still_unmatched
revise_goal5368_raw_kind_count_telemetry
block_goal5368_raw_kind_count_telemetry
```
