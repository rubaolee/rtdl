# Gemini Review: Goal3073 v2.7 Generated Primitive Catalog

Date: 2026-06-03

## Review Questions & Verdicts

1.  **Does the generated catalog now treat `src/rtdsl/primitive_hierarchy.py` as the single source of truth?**
    *   **Verdict:** `accept`
    *   **Evidence:** The `Goal3073` report explicitly states this intent. `docs/rtdl_primitive_catalog.md` contains a warning not to hand-edit and directs users to modify `src/rtdsl/primitive_hierarchy.py` or the renderer instead. The `render_primitive_catalog_markdown` function in `src/rtdsl/primitive_catalog.py` directly consumes `PRIMITIVE_HIERARCHY` from `src/rtdsl/primitive_hierarchy.py`. Unit tests in `tests/goal3073_v2_7_generated_primitive_catalog_test.py` confirm the catalog matches the rendered output and that the source of truth is correctly identified in the generated document.

2.  **Is the drift gate strong enough for this v2.7 slice?**
    *   **Verdict:** `accept`
    *   **Evidence:** The `Goal3073` report describes a byte-for-byte comparison of the checked-in Markdown against the programmatically rendered content. This is confirmed by `test_checked_in_catalog_matches_renderer` in `tests/goal3073_v2_7_generated_primitive_catalog_test.py`. Additionally, `test_generator_check_mode_detects_no_drift` verifies the `generate_rtdl_primitive_catalog.py --check` mode, and `test_every_hierarchy_node_id_appears_in_catalog` ensures all nodes are present. These combined measures provide a robust drift gate for the current slice.

3.  **Does the generated catalog remain readable and useful for primitive discovery?**
    *   **Verdict:** `accept`
    *   **Evidence:** The generated `docs/rtdl_primitive_catalog.md` is well-structured and comprehensive. It includes clear explanations of what constitutes a primitive, a hierarchical organization, detailed status metadata, layer-specific tables with outputs, dependencies, capabilities, and backend information, as well as a dedicated section for discovery metadata (aliases, intent phrases, references, distinctions). The "Controlled Discovery Facets" and "App-Owned Boundary Exclusions" are also clearly presented, making the document highly readable and useful for primitive discovery.

4.  **Was replacing `Triton-first Partner Continuation` with `Explicit Partner Continuation` the correct current-source cleanup?**
    *   **Verdict:** `accept`
    *   **Evidence:** The `Goal3073` report clearly explains that this change reflects the v2.6/v2.7 boundary, emphasizing that "partner choice is explicit user/runtime metadata, not hidden routing or native-engine policy." The `PrimitiveHierarchyNode` with `id="continuation.partner_resident"` in `src/rtdsl/primitive_hierarchy.py` now correctly reflects `title="Explicit Partner Continuation"` and the updated summary. `tests/goal3073_v2_7_generated_primitive_catalog_test.py` explicitly validates the presence of the new wording and the absence of the old in the generated catalog, confirming the cleanup.

5.  **Does the updated v2.5 pivot test preserve historical coverage without forcing stale current wording?**
    *   **Verdict:** `accept`
    *   **Evidence:** Inspection of `tests/goal2676_v2_5_triton_partner_pivot_test.py` reveals that the test `test_primitive_hierarchy_records_explicit_partner_continuation` specifically checks for the new "Explicit Partner Continuation" while simultaneously asserting that older, potentially stale phrases like "NumPy/CuPy/PyTorch-style" are absent from the node's summary. Other tests within this file continue to validate v2.5 specific behaviors and terminology (e.g., `test_planner_marks_triton_count_sum_as_executable_preview`, `test_raydb_v2_5_surface_prefers_triton_and_not_cupy_or_pytorch_partner`), demonstrating that historical coverage relevant to v2.5 is maintained.

6.  **Are there any release, speedup, zero-copy, broad RT-core, paper-reproduction, or app-shaped-engine overclaims?**
    *   **Verdict:** `accept`
    *   **Evidence:** Both the `Goal3070` and `Goal3073` primary reports contain explicit "Boundary" sections that clearly disclaim any claims regarding release readiness, performance improvements, zero-copy, broad RT-core, paper-reproduction, or app-specific primitives. Furthermore, the generated `docs/rtdl_primitive_catalog.md` prominently features a "Claim Boundary" section and a "Status" header that reiterate these disclaimers, ensuring consistency and preventing overclaims in the documentation.
