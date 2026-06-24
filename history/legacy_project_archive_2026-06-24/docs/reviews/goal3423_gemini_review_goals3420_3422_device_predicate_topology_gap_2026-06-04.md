# Independent Gemini Review for Goals3420-3422: Device-Predicate / Closed-Shape Topology Gap Chain

**Verdict:** accept

## Review Summary

This independent review covered the v2.8 device-predicate / closed-shape topology gap chain across Goals3420-3422, focusing on the provided reports, artifacts, test files, scripts, and relevant source code. The review confirms that the work adheres to established claim boundaries and correctly identifies the challenges and next steps in achieving a device-resident exact stream direction.

## Detailed Responses to Review Questions

1.  **Do Goals3420-3422 correctly preserve the app-agnostic engine boundary while testing the v2.8 device-resident exact stream direction?**
    Yes, Goals3420-3422 consistently preserve the app-agnostic engine boundary.
    *   **Goal3420**: The report explicitly states that the device stream is a candidate/native predicate path, not a new native exact page-plan producer, and the host-exact path is used only as a correctness oracle. The artifact confirms that `universal_exact_predicate_claim_authorized` is `False`.
    *   **Goal3421**: The CuPy helper is presented as "partner-layer evidence," not a final native v2.8 producer, and host exact rows serve solely as an oracle. The `native_exact_device_predicate_claim_authorized` flag is confirmed `False` in the artifact.
    *   **Goal3422**: The "Next Engineering Target" mandates keeping "RTDL native traversal app-agnostic" and treating "topology rows as caller-provided data, not native app policy."
    *   The source file `src/rtdsl/closed_shape_topology.py` reinforces this by explicitly setting `matches_geos_topology_oracle: False` in the CuPy refinement function and by designing owner-face functions to take caller-supplied topology data, explicitly stating that the engine "does not infer CDB, RayJoin, GIS, or application-specific ownership."

2.  **Is the Goal3420 conclusion valid: native RT device predicate columns are a strong superset on the public CDB, but not exact (`47,570` vs `47,262`, `0 missing`, `308 extra`)?**
    Yes, the Goal3420 conclusion is valid. The `docs/reports/goal3420_device_predicate_page_equivalence_2026-06-04.md` report and its corresponding JSON artifact clearly show the following:
    *   Host-exact pair rows: 47,262
    *   Device predicate pair rows: 47,570
    *   Missing device pairs: 0
    *   Extra device pairs: 308
    *   Mismatched grouped counts: 248
    These numbers, and the qualitative assessment that the device predicate path is a strong superset but not exact, are consistently reflected across the report, artifact, and verified by the unit tests.

3.  **Is the Goal3421 conclusion valid: the CuPy simple-ring refinement removes false positives but misses GEOS/topology boundary pairs (`47,045`, `217 missing`, `0 extra`, `97` mismatched groups at `point_eps=1e-9`)?**
    Yes, the Goal3421 conclusion is valid. The `docs/reports/goal3421_cupy_refined_device_predicate_page_probe_2026-06-04.md` report and its JSON artifact confirm the following for `point_eps=1e-9`:
    *   CuPy refined pair rows: 47,045
    *   Dropped candidate pairs (total): 525 (this includes the 217 host-exact missing pairs)
    *   Missing host-exact pairs from refined output: 217
    *   Extra refined pairs: 0
    *   Mismatched grouped counts: 97
    The analysis correctly identifies that a simple point-in-ring predicate is insufficient to reproduce the GEOS/topology oracle, leading to the observed missing boundary pairs.

4.  **Does Goal3422 correctly identify the next primitive as a generic topology-aware closed-boundary refinement contract, with topology rows supplied by the caller and no RayJoin/CDB policy embedded into native engine code?**
    Yes, Goal3422 correctly identifies the next primitive. The `docs/reports/goal3422_closed_shape_topology_refinement_gap_2026-06-04.md` clearly states the "Next Engineering Target" as building a "topology-aware closed-boundary refinement contract" where "topology rows are caller-provided data, not native app policy." This is further supported by the `docs/research/future_version_to_do_list.md`, which calls for "a generic topology-aware closed-boundary refinement contract where topology rows are caller data, not native app policy." The design of functions in `src/rtdsl/closed_shape_topology.py` (e.g., `filter_closed_shape_membership_candidates_by_owner_face`) reflects this by requiring explicit `topology_rows` from the caller.

5.  **Do all reports and artifacts preserve claim boundaries: no release authorization, no public speedup claim, no RT-core speedup claim, no true-zero-copy claim, no native default-route claim?**
    Yes, all reports and artifacts consistently preserve the specified claim boundaries. Each report explicitly states that release, public speedup, RT-core speedup, true zero-copy, and native default-route claims remain blocked. The JSON artifacts for Goal3420 and Goal3421 have all relevant boolean flags in their `claim_boundary` sections set to `False`. Additionally, the `src/rtdsl/closed_shape_topology.py` file, both in function return values and contract definitions, explicitly sets these claims to `False`, ensuring that no unauthorized claims are made.

## Conclusion

The Goals3420-3422 chain provides a clear and well-evidenced diagnostic of the challenges in implementing a v2.8 device-resident exact stream direction for closed-shape topology. The work correctly identifies the limitations of current approaches and sets a sound direction for future development, while meticulously adhering to claim boundaries and maintaining an app-agnostic engine design.
