# Call For Review: Goal4939 Grouped Path-Split Row-Buffer Prototype

Please review Goal4939.

## Files

- Completion report: `history/internal_docs/goal4939_grouped_path_split_row_buffer_prototype_2026-07-03.md`
- Source: `src/rtdsl/output_assembly.py`
- Public exports: `src/rtdsl/__init__.py`
- Tests: `tests/goal4939_grouped_path_split_records_test.py`
- Prior design gate: `history/internal_docs/goal4938_layer3_boundary_relocation_report_2026-07-03.md`
- Prior review: `history/internal_docs/antigravity_goal4938_layer3_boundary_relocation_review_2026-07-03.md`

## Requested Verdict

Choose one:

- `approve_goal4939_generic_path_split_prototype_authorize_goal4940`
- `redo_goal4939_due_to_genericity_or_test_gap`
- `reject_goal4939_as_hidden_app_specific_route`

## Review Questions

1. Is `assemble_grouped_path_split_records` generic, or does it hide RayJoin/overlay semantics?
2. Does it correctly operate on neutral primitive columns: chains, base points, split events, interval descriptors, and validity masks?
3. Do the tests prove a non-RayJoin path segmentation fixture before any RayJoin wiring?
4. Do the tests sufficiently prevent app identity leakage into `src/rtdsl/output_assembly.py`?
5. Does the API compose correctly with the existing `GroupedOutputRowBuffer` and materializer path?
6. Is it correct that Goal4939 does not authorize any RayJoin speedup claim yet?
7. Should Goal4940 be authorized to wire this into the RayJoin public sample as an app adapter with byte-equality and same-run performance gates?

## Non-Authorization

This review should not authorize:

- RayJoin-specific semantics in RTDL core;
- author-format text output in RTDL core;
- public speedup claims;
- skipping byte equality in Goal4940;
- continuing if Goal4940 is byte-equal but slower.
