---

## Code Review: Goal2625 SEGMENTED_ROW_STREAM

---

### Verdict: **ACCEPT**

---

### Blocking Issues

None.

---

### Non-Blocking Issues

**1. Duplicate `__all__` entry in `__init__.py`**
`"emit_segmented_row_stream"` appears twice in `__all__` (lines 1284 and 2183). Harmless at runtime but should be cleaned up before the next catalog audit.

**2. `page_index` relies on an unenforced alignment invariant**
`emit_segmented_row_page` computes `page_index = offset // page_size` (`segmented_row_stream.py:198`). This is correct only when the token offset is always a multiple of `page_size` — which holds for all internally-generated tokens, but is not validated at `parse_segmented_row_token` time. An external consumer who crafts a misaligned token would get a silently wrong `page_index` that `validate_segmented_row_pages` would then catch as a contiguity failure. The behaviour is ultimately safe but the invariant should be documented or enforced at parse time.

**3. Two distinct labels for the same overflow policy**
`SEGMENTED_ROW_STREAM_CONTRACT` carries both `"overflow_policy": "fail_closed_no_partial_result"` and `"failure_mode": "fail_closed_overflow"`. They describe the same guarantee with different keys and names. A future reader auditing the contract dict against the error message string (`failure_mode=fail_closed_overflow`) will have to cross-reference both keys to confirm they are the same thing.

**4. Missing direct negative-path tests for token helpers**
`parse_segmented_row_token` has three rejectable paths (wrong stream_id prefix, non-integer offset, negative offset) and `_normalize_stream_id` rejects colon-containing IDs. These paths are exercised indirectly but never hit directly in the test suite. For `internal_substrate` this is acceptable; they should be pinned before any promotion gate.

**5. Zero-row stream not explicitly tested**
`emit_segmented_row_stream` on an empty `rows` iterable will produce an empty `pages` tuple and `complete_candidate_coverage=False` (because `bool(pages)` is `False`). Whether an empty stream should be considered complete is a design question; there is no test asserting the intended behaviour.

---

### Rationale

**App-independence**: The implementation contains no domain vocabulary. The contract's `app_boundary` field, the catalog entry, the hierarchy node boundary, and the report all consistently state that row schema, pagination, and completion metadata are the only owned behaviors. Domain interpretation is explicitly pushed to consumers. The composition test (`test_segmented_stream_composes_with_existing_aabb_rows`) verifies the contract survives the boundary with a concrete upstream primitive and confirms `native_engine_customization=False`.

**Fail-closed on exact overflow**: `_enforce_total_capacity` (`segmented_row_stream.py:389–400`) raises `SegmentedRowStreamOverflowError` *before* any pagination runs, with `partial_result_returned=False` in the message. Both `emit_segmented_row_page` and `emit_segmented_row_stream` call it as the first post-normalization step. The overflow test (`test_total_capacity_overflow_fails_closed_before_returning_pages`) confirms the exception is raised and the message matches `failure_mode=fail_closed_overflow.*partial_result_returned=False`.

**`internal_substrate` scoping**: The status is set consistently in the contract dict, the hierarchy node (`continuation.segmented_chunked_rows`, `primitive_hierarchy.py:436`), the catalog table, and the test assertion. The report explicitly notes this is a runtime-organization decision, not a stable external primitive claim, and that native backend page emission requires separate evidence. No stable/experimental language appears anywhere in the changed files.

**Test coverage**: Eight tests cover contract metadata, deterministic token offsets, round-trip reconstruction, incomplete-window detection and rejection, fail-closed overflow, schema/contiguity validation, cross-primitive composition, and hierarchy/catalog documentation. That is sufficient breadth for an `internal_substrate` landing.
