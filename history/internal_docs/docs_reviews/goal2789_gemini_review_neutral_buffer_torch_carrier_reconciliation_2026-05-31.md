# Independent Gemini Review For Goal2789

Date: 2026-05-31

## Review of Goal2789: Neutral Buffer / Triton Tensor-Carrier Reconciliation

This review assesses Goal2789, which addresses a v2.5 architecture risk identified by Claude. The primary objective was to clarify the neutral buffer seam by renaming a misleading helper function and explicitly defining the boundaries of the Triton carrier path.

### Review Questions & Answers:

1.  **Does Goal2789 remove the misleading `_maybe_torch_column` seam name and replace it with explicit Triton tensor-carrier preparation terminology?**
    *   **Answer:** Yes. The `src/rtdsl/hit_stream_handoff.py` file has been updated to replace `_maybe_torch_column` with `_prepare_triton_tensor_carrier_column`. The associated test `tests/goal2789_neutral_buffer_torch_carrier_reconciliation_test.py` explicitly verifies this renaming, and the `docs/reports/goal2789_neutral_buffer_torch_carrier_reconciliation_2026-05-31.md` report confirms this change.

2.  **Does it keep the behavior bounded: Triton may use Torch tensors as a launch carrier, but silent cross-partner torch coercion remains disallowed?**
    *   **Answer:** Yes. The code in `src/rtdsl/hit_stream_handoff.py` (specifically within `describe_v2_5_hit_stream_torch_carrier_adapter` and `describe_v2_5_hit_stream_neutral_seam_reconciliation`) explicitly sets `"silent_cross_partner_torch_coercion_allowed": False`. The tests also confirm that `torch_carrier_allowed_only_for_partner` is set to "triton", reinforcing the bounded behavior. The report explicitly states that silent cross-partner torch coercion remains disallowed.

3.  **Does neutral-buffer metadata still account for host-stage and device-resident handoffs?**
    *   **Answer:** Yes. The `RtdlHitStreamColumnHandoff.to_metadata()` and `_neutral_buffer_seam_metadata` functions in `src/rtdsl/hit_stream_handoff.py` clearly demonstrate that neutral-buffer seam metadata is extensively used to track `device_resident`, `materializes_host_rows_for_bridge`, `transfer_status`, and `lifetime_state`. The tests confirm that `neutral_buffer_seam_contract_version` is correctly applied and that host-stage transfers are accounted for.

4.  **Are true zero-copy, speedup, RT-core, and release claims still blocked?**
    *   **Answer:** Yes. Multiple functions and metadata dictionaries in `src/rtdsl/hit_stream_handoff.py` consistently set `"true_zero_copy_authorized": False` and `"public_speedup_claim_authorized": False`. The Goal2789 report explicitly lists these as unauthorized claims, and the tests verify these flags remain `False`.

5.  **Are the tests/report adequate for this narrow seam-reconciliation goal?**
    *   **Answer:** Yes. The provided `tests/goal2789_neutral_buffer_torch_carrier_reconciliation_test.py` adequately covers the key aspects of the goal, including the naming change, the boundedness of the Triton carrier, and the accounting of neutral-buffer metadata. The `docs/reports/goal2789_neutral_buffer_torch_carrier_reconciliation_2026-05-31.md` report provides a clear and concise summary of the changes, boundaries, and validation, which is sufficient for this specific, narrow reconciliation goal.

### Required Verdict:

`accept-with-boundary`

Goal2789 successfully clarifies the architectural seam by renaming the misleading helper and explicitly bounding the Triton tensor-carrier path. It reinforces that Triton may use Torch tensors as a launch carrier but prevents silent cross-partner torch coercion and maintains the blocked status for true zero-copy, speedup, RT-core, and release claims. The implemented changes and accompanying documentation and tests are appropriate for this specific seam reconciliation.