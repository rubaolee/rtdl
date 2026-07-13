# Call For Review: Goal4934 Layer 3 Feasibility And Writer Semantics Audit

Date: 2026-07-03

Requested reviewer: Antigravity, with Claude debt allowed later.

Primary report:

`history/internal_docs/goal4934_layer3_feasibility_writer_semantics_audit_2026-07-03.md`

## Review Request

Please review Goal4934 strictly.

The goal is a gate before any compiled/vectorized writer work. The report audits the current RayJoin Section 5.7 writer and classifies each operation as generic, generic-if-columnar, app-specific, or file IO.

The proposed exit label is:

`needs_layer1_shape_before_decision`

This means:

- do not implement a compiled writer yet;
- do not stop the whole line yet;
- next define a neutral row-buffer/data-shape contract.

## Questions

1. Does the operation classification accurately describe the current `write_output_chains_streaming_numba_skip` writer?

2. Is the report correct that current Layer 3 implementation would be premature because the generic layer still consumes Python strings/lists/headers built by app-specific chain loops?

3. Does the report correctly avoid hiding RayJoin output-chain semantics behind generic RTDL names?

4. Is the proposed generic output IR truly generic enough to be considered in RTDL core, or does it still leak RayJoin semantics?

5. Is `needs_layer1_shape_before_decision` the right exit label, rather than `layer3_generic_feasible` or `writer_is_app_specific_stop`?

6. Is Goal4935, a Layer 1 row-buffer/data-shape contract goal, the right next step before any materializer prototype?

7. Does the report preserve the right non-claims: no performance claim, no compiled writer authorization, no V3/V4 claim, and no RayJoin-specific core writer?

Requested verdict labels:

- `approve_goal4934_needs_layer1_shape_before_decision`
- `approve_with_required_amendments`
- `reject_goal4934_wrong_feasibility_classification`
