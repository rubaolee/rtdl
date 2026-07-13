# Call For Review: Goal4935 Layer 1 Output Row-Buffer/Data-Shape Contract

Date: 2026-07-03

Requested reviewer: Antigravity, with Claude debt allowed later.

Primary report:

`history/internal_docs/goal4935_layer1_output_row_buffer_contract_2026-07-03.md`

Code:

- `src/rtdsl/output_assembly.py`
- `src/rtdsl/__init__.py`

Tests:

- `tests/goal4935_output_row_buffer_contract_test.py`
- `tests/goal4932_generic_output_assembly_test.py`

## Review Request

Please review Goal4935 strictly.

Goal4935 should prove a neutral Layer 1 output row-buffer/data-shape contract is ready before any compiled output materializer work begins.

The requested exit label is:

`layer1_shape_contract_ready`

## Questions

1. Does the new `GroupedOutputRowBufferSchema` / `GroupedOutputRowBuffer` contract stay generic, or does it leak RayJoin/overlay/author semantics?

2. Does object-dtype rejection correctly prevent the Goal4933 failure mode where generic assembly consumed Python strings/lists too late?

3. Are descriptor columns, item payload columns, validity masks, and dedupe keys sufficient as a Layer 1 shape for a future generic materializer prototype?

4. Does the RayJoin-style adapter test prove the app can map into the neutral shape without putting RayJoin semantics into core?

5. Does the non-RayJoin radius-neighbor fixture prove the shape is not RayJoin-only?

6. Are the tests sufficient for this contract stage, given that this goal does not implement a compiled writer or device-resident row-buffer?

7. Is it correct to close Goal4935 with `layer1_shape_contract_ready` and authorize only Goal4936 materializer prototyping next?

8. Does the report preserve the right non-claims: no compiled writer, no native writer, no device-resident row-buffer, no speedup, no V3/V4 claim?

Requested verdict labels:

- `approve_goal4935_layer1_shape_contract_ready`
- `approve_with_required_amendments`
- `reject_goal4935_shape_contract_leaks_app_semantics`
