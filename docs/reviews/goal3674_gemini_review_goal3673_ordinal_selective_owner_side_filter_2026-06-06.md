# Gemini Review: Goal3673 Ordinal-Selective Owner-Side Filter

Date: 2026-06-06

## Review Questions & Answers

1.  **Does the new ordinal-aware side filter remain app-agnostic, or does it smuggle CDB/RayJoin ownership policy into the engine/runtime?**
    The new ordinal-aware side filter appears to remain app-agnostic. The `docs/reports/goal3673_ordinal_selective_owner_side_filter_2026-06-06.md` explicitly states, "no CDB, RayJoin, map, or GIS ownership policy enters the native engine," and further clarifies, "The engine remains app-agnostic: RTDL/OptiX emits generic candidate id columns plus input/prepared ordinals; the caller supplies ambiguity ordinals and owner-face side policy; the CuPy continuation filters only those selected rows." This is consistent with the `docs/research/future_version_to_do_list.md` which emphasizes keeping such decisions in Python policy, not moving them into the native engine.

2.  **Is the negative all-point probe interpreted correctly: owner-side filtering is not a universal replacement for membership?**
    Yes, the negative all-point probe is interpreted correctly. The report (`docs/reports/goal3673_ordinal_selective_owner_side_filter_2026-06-06.md`) clearly states, "All-point owner-side filtering is not a universal replacement for membership. It over-filters valid rows: [...] This is the design lesson: owner-side topology is a selective repair mechanism for ambiguous rows, not the entire point/closed-shape membership predicate." The `full_county_ordinal_owner_side_route_probe.json` artifact provides concrete evidence with `matches_exact_multiset: false` and a significant `missing_rows_after_filter: 24623`, supporting this interpretation.

3.  **Is the positive selective probe strong enough to claim the immediate full-county `47264 != 47262` mismatch is repaired when the caller supplies selected ambiguity input ordinals and owner-side columns?**
    Yes, the positive selective probe is strong enough. The `docs/reports/goal3673_ordinal_selective_owner_side_filter_2026-06-06.md` report details the "Positive Probe: Selective Ordinal-Aware Repair" showing that by supplying selected ambiguity input ordinals, `multiset parity: true` was achieved, with the `candidate rows before filter: 47,264` being correctly reduced to `filtered rows: 47,262` with `missing rows after filter: 0`. The `full_county_selective_ordinal_owner_side_route_probe.json` artifact corroborates this with `matches_exact_multiset: true` and `filtered_row_count: 47262`.

4.  **Are claim boundaries preserved? In particular, no release, public speedup, RTDL-beats-RayJoin, RayJoin reproduction, true-zero-copy, or native default route claim should be authorized.**
    Yes, the claim boundaries are rigorously preserved. The "Boundary" sections in both `docs/reports/goal3673_ordinal_selective_owner_side_filter_2026-06-06.md` and `docs/reports/goal3602_v2_9_benchmark_status_after_resident_evidence_2026-06-06.md` explicitly list all these claims as "Blocked claims remain blocked" or "does not authorize." Furthermore, the `claim_boundary` fields within the `full_county_ordinal_owner_side_route_probe.json` and `full_county_selective_ordinal_owner_side_route_probe.json` artifacts explicitly set these authorizations to `false`. Unit tests like `tests/goal3602_v2_9_benchmark_status_after_resident_evidence_test.py` also verify the presence of these disclaimers in the reports.

5.  **Are the tests adequate and are there missing acceptance bars before this could become a default route?**
    The current tests (`tests/goal3673_ordinal_selective_owner_side_filter_test.py`, `tests/goal3671_side_aware_owner_face_filter_test.py`, and checks within `tests/goal3602_v2_9_benchmark_status_after_resident_evidence_test.py`) appear adequate for validating Goal3673's intended functionality as a selective repair mechanism. However, the report `docs/reports/goal3673_ordinal_selective_owner_side_filter_2026-06-06.md` explicitly states that it "does not yet authorize automatic default route selection because the caller still supplies the selected ambiguity set and the owner-side derivation policy." The "Next Major Direction" section in the same report, echoed in `docs/research/future_version_to_do_list.md`, identifies the missing acceptance bar as the development of "a generic ambiguity-set derivation contract (`candidate stream + topology/boundary signals -> selected input ordinals`)." This contract must remain caller/data-layer policy or a generic primitive and *not* hidden CDB/RayJoin logic within the native engine.

## Verdict

`accept-with-boundary`

## Boundary

The current implementation is accepted as a valuable, explicitly bounded, and app-agnostic selective repair mechanism for the RayJoin PIP mismatch. It does *not* authorize automatic default route selection. Its use as a general-purpose feature for resolving topological ambiguities requires the development of a generic, caller-defined ambiguity-set derivation contract, as outlined in the "Next Major Direction" of Goal3673's report and the `future_version_to_do_list.md`. The claim boundaries rigorously defined in the reports and artifacts must be maintained.
