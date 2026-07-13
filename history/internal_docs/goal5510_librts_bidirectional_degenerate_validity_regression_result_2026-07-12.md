# Goal5510 LibRTS Bidirectional Degenerate-AABB Regression

Status: `implemented__generic_contract_documented__focused_regression_passed`

Goal5510 closes the two non-blocking follow-ups from the Goal5508-5509 review.

The generic AABB contract now explicitly states that native accelerated
intersection paths reject indexed boxes that are not strict after numeric
packing (`min_x < max_x && min_y < max_y`). This prevents OptiX padding from
becoming an implicit match contract for zero-width or zero-height boxes.

The regression fixture uses a degenerate primitive record and a valid query
record. It verifies that the forward pass selects `prim` and rejects the
record, while the backward pass selects `qidx` and accepts the valid record.
The fixture is behaviorally distinguishable and the source scan confirms the
native code remains app-neutral.

Focused verification: 6 tests passed. This goal changes no paper semantics,
does not add LibRTS behavior to RTDL core, and makes no full matrix,
performance, relation, paper, zero-copy, or Embree claim.
