# Goal2832 Gemini Review: Goal2831 Primitive Payload Column Descriptors (2026-05-31)

## Review Date
2026-05-31

## Reviewed By
Gemini CLI Agent

## Files Inspected
- `docs/reports/goal2831_primitive_payload_column_descriptors_2026-05-31.md`
- `tests/goal2831_primitive_payload_column_descriptor_test.py`
- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `docs/reports/goal2829_fixed_radius_graph_same_stream_device_partials_2026-05-31.md`
- `docs/reports/goal2830_goal2829_same_stream_partials_consensus_2026-05-31.md`

## Review Questions and Answers

### 1. Does Goal2831 provide a genuinely generic primitive-payload column descriptor rather than an app-shaped RTNN/RayJoin/DBSCAN API?
Yes. The `RtdlPrimitivePayloadColumnDescriptor` is designed with generic fields such as `semantic_role`, `producer`, `consumer`, `stream_ordering`, `lifetime_state`, and `fallback_reason`. The `GENERIC_PRIMITIVE_PAYLOAD_COLUMN_ROLES` defines abstract roles, and tests explicitly confirm that unsupported, app-specific roles are rejected. Furthermore, the `hit_stream_handoff.py` module explicitly avoids mentions of "rayjoin" or "rtnn", reinforcing the generic nature of the API.

### 2. Does it correctly compose with the neutral-buffer seam, including transfer status, lifetime state, native producer, and fallback reason?
Yes. The `RtdlPrimitivePayloadColumnDescriptor` wraps an `RtdlBufferDescriptor` and includes dedicated fields for `transfer_status`, `lifetime_state`, `native_producer`, and `fallback_reason`. Its `to_metadata()` method properly integrates these into the `neutral_buffer_seam` dictionary, validating the composition. Tests specifically confirm the correct population of these fields and the interaction between `native_producer` and `lifetime_state`.

### 3. Does the Goal2829 same-stream partial path now publish a descriptor for the graph-owned partial buffer without exposing unsafe ownership or claiming broad zero-copy?
Yes. Goal2831's integration ensures that the `describe_fixed_radius_graph_partial_payload_descriptor` (used by the Goal2829 path) correctly sets `semantic_role="partial_aggregate_rows"`, `producer="optix_cuda_graph"`, `lifetime_state="producer_retained"`, and `native_producer=True`. This confirms that the buffer is owned and retained by the producer (the CUDA graph), preventing unsafe ownership. Crucially, the `true_zero_copy_authorized` flag is explicitly set to `False` in the metadata, aligning with the strict claim boundaries of Goal2829/2830 and avoiding broad zero-copy claims. The `transfer_status` is appropriately set to `borrowed_device_pointer_unmeasured`.

### 4. Are invalid roles and invalid native lifetimes fail-closed in tests?
Yes. The `test_invalid_roles_and_native_lifetime_fail_closed` in `tests/goal2831_primitive_payload_column_descriptor_test.py` explicitly verifies this behavior. It asserts that `ValueError` exceptions are raised when an unsupported `semantic_role` is provided or when a native producer does not retain ownership, thus ensuring fail-closed behavior for these invalid states.

### 5. Are claim boundaries strict: no arbitrary partner execution, public speedup, broad true-zero-copy, paper reproduction, whole-app speedup, or v2.5 release claim?
Yes. The `RtdlPrimitivePayloadColumnDescriptor.to_metadata()` method explicitly sets `public_speedup_claim_authorized` and `true_zero_copy_authorized` to `False`. The `claim_boundary` string within the metadata, as well as the Goal2831 report and supporting consensus documents, reiterate these strict exclusions. This aligns with the `accept-with-boundary` verdicts of previous related goals.

### 6. Is the proposed next step reasonable: use descriptors to drive a partner-neutral continuation planner for CuPy/Triton/Numba selection with explicit fallback reasons?
Yes. The Goal2831 report clearly states this as the next logical step. The generic nature of the descriptors, their ability to encapsulate essential metadata like fallback reasons, and the validated fail-closed mechanisms provide a solid foundation for building a robust, partner-neutral continuation planner, consistent with the v2.5 direction.

## Verdict
`accept-with-boundary`
