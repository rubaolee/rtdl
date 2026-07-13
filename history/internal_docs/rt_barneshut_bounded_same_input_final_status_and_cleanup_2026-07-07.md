# RT-BarnesHut Bounded Same-Input Final Status And Cleanup

Date: 2026-07-07

## Status

```text
bounded_same_input_line_closed
required_review_debt_remaining = 0
```

This is a final housekeeping/status note, not a new implementation goal and not a new call-for-review item.

## Final Technical State

The RT-BarnesHut paper-reproduction app now has a bounded same-input route built on generic RTDL aggregate-hierarchy APIs:

- `AggregateHierarchy3D`,
- generic opening policies including `SizeDistanceOpening`, `LeafOnlyOpening`, and `ContinuationPayloadOpening`,
- generic reducers including `AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT`,
- CPU reference executor,
- optional Numba parity executor,
- app-owned scalar force-output bridge,
- app-owned same-input comparator and patched-author artifact handling.

The generic aggregate route matched patched-author same-input scalar force output on the live POD gate:

```text
force_count = 32768
mismatch_count = 0
max_abs_error = 1830.0
max_rel_error = 2.1112736725325853e-06
opening.policy = continuation_payload_opening
```

Goal5081 and Goal5082 close the genericity/behavior hardening for `ContinuationPayloadOpening`:

- independent non-RT-BarnesHut consumer,
- different reducer (`aggregate_count`),
- behavior-level row assertions,
- accepted aggregate traversal with `rope_index != next_index`.

## Review State

The review register records:

```text
Pending:
None for the bounded same-input RT-BarnesHut line.

Closed:
Goal5065 amendments: verified and closed.
Goals5063-5074 consolidated rearchitecture review: approved.
Goal5075 scalar force-output bridge review: approved.
Goal5076 external review debt: superseded by reviewed Goal5079 live POD same-input evidence.
Goal5077 external review: approved.
Goal5078 external review debt: superseded by reviewed Goal5079 live POD full-gate execution.
Goal5079 external review: complete; required amendments completed by Goal5081.
Goal5080 external review: complete; required amendments completed by Goal5081.
Goal5081 external review: complete and approved.
Goal5082 external review: complete and approved.
Goal5083 external review: complete and approved; bounded same-input line closed.
Goal5084 external review: complete and approved; intermediate debt disposed.
```

Canonical register:

```text
history/internal_docs/rt_barneshut_review_opinions_register_2026-07-06.md
```

## Verification Run

Final local suite:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test tests.goal5072_aggregate_frontier_reduce_cpu_reference_test tests.goal5073_aggregate_frontier_reduce_numba_parity_test tests.goal5081_continuation_payload_genericity_proof_test tests.goal5082_continuation_payload_rope_branch_test
Ran 76 tests in 32.956s
OK (skipped=1)
```

Compile check:

```text
py -m py_compile Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py Paper-reproduction-apps/rt-barneshut-paper/scripts/run_full_pod_reproduction_gate.py Paper-reproduction-apps/rt-barneshut-paper/scripts/run_remote_full_pod_gate.py Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.py src/rtdsl/aggregate_hierarchy.py
```

Result:

```text
OK
```

The local Python environment repeatedly printed:

```text
Could not find platform independent libraries <prefix>
```

This is a known local environment message and did not affect test or compile status.

## Cleanup

Pure Python cache cleanup:

```text
removed_pycache_count = 37
remaining_pycache_count = 0
```

Runtime/evidence directories were intentionally not removed:

```text
Paper-reproduction-apps/rt-barneshut-paper/_runs
Paper-reproduction-apps/rt-barneshut-paper/_work
```

Reason: these directories may contain generated run artifacts and live POD evidence used by the RT-BarnesHut review trail. They are ignored by the app package rules and should not be silently deleted during evidence-preserving cleanup.

## Public README Sync

After bounded closeout, `Paper-reproduction-apps/rt-barneshut-paper/README.md`
was synchronized with the final evidence:

- `mismatch_count = 0`,
- `max_abs_error = 1830.0`,
- `max_rel_error = 2.1112736725325853e-06`,
- broader reported envelope `469.35 ms / 185.45 ms = 2.53x` unfavorable to RTDL,
- bounded same-input CUDA/POD gate passed,
- independent tree construction and full paper reproduction remain not claimed.

## Public Surface Scan

Scanned:

```text
Paper-reproduction-apps/README.md
Paper-reproduction-apps/rt-barneshut-paper/README.md
src/rtdsl/aggregate_hierarchy.py
src/rtdsl/__init__.py
```

Patterns:

```text
Goal[0-9]+
call_for_review
Antigravity
Claude
Gemini
review debt
verdict
```

Result:

```text
0 matches
```

## Claims Explicitly Not Authorized

The bounded same-input line still does not authorize:

- full RT-BarnesHut paper reproduction,
- independent tree construction from raw particle input,
- whole-envelope RTDL speedup,
- author-performance parity,
- phase-boundary performance acceptance,
- native/CUDA aggregate-hierarchy backend completion.

Broader envelope remains unfavorable to RTDL:

```text
RTDL total = 469.34572154283524 ms
Author total = 185.446 ms
Envelope ratio = 2.530902373428573
```

## Recommended Stop Point

Stop this line here.

Future work, if explicitly authorized, should be a separate line:

1. phase-boundary acceptance,
2. independent tree construction,
3. native/device aggregate-hierarchy backend,
4. broader RT-BarnesHut paper reproduction.
