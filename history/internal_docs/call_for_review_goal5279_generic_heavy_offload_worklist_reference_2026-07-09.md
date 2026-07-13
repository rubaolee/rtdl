# Call For Review - Goal5279 Generic Heavy-Offload Worklist Reference

Please strictly review Goal5279.

## Files To Review

Implementation:

```text
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
```

Tests:

```text
tests/goal5279_generic_heavy_offload_worklist_test.py
tests/goal5139_generic_nearest_state_frontier_api_test.py
tests/goal5140_generic_cell_mbr_traversal_abi_test.py
```

Result / artifact:

```text
history/internal_docs/goal5279_generic_heavy_offload_worklist_reference_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5279_generic_heavy_offload_worklist_reference_2026-07-09.json
```

Context:

```text
history/internal_docs/goal5278_generic_heavy_offload_worklist_api_design_2026-07-09.md
history/internal_docs/goal5277_xhd_memory_denominator_alignment_decision_result_2026-07-09.md
```

## Review Questions

1. Does Goal5279 implement an app-neutral heavy/offload worklist schema rather
   than an X-HD-specific `offloading_point_ids_` clone?
2. Are the row schema and kind codes generic enough for non-X-HD uses?
3. Does the NumPy/CPU reference select active and miss rows correctly in the
   evidence fixture?
4. Does overflow fail closed with no partial rows and diagnostic attempted
   count retained?
5. Does telemetry expose queue capacities, queue bytes, current/peak offload
   rows, and offload queue peak bytes in a status-bearing way?
6. Is the non-X-HD facility-backlog consumer sufficient for this first
   implementation stage?
7. Are the public exports in `src/rtdsl/__init__.py` appropriate, or should the
   helper remain internal until Goal5280?
8. Does the implementation avoid app identity leakage in RTDL core?
9. Are the claim boundaries clear that this is not Figure 11 reproduction,
   author memory parity, native backend completion, or a performance claim?
10. Is Goal5281 correctly identified as the first goal that can provide POD /
    native peak telemetry evidence?

## Requested Verdict Labels

Preferred approval label:

```text
approve_goal5279_generic_heavy_offload_worklist_reference
```

If the reviewer finds the schema too X-HD-shaped:

```text
revise_goal5279_schema_too_app_shaped
```

If the reviewer finds the telemetry insufficient for the Goal5278 path:

```text
revise_goal5279_memory_telemetry_contract
```

If the reviewer finds the public API exposure premature:

```text
approve_with_required_amendment_keep_goal5279_internal_until_goal5280
```
