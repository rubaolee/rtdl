# Call For Review: Goal4932 Host-Columnar Generic Grouped-Sequence Assembly Result

Date: 2026-07-03

Requested verdict labels:

- `approve_goal4932_host_columnar_generic_assembly_complete_authorize_goal4933_app_wiring`
- `approve_with_required_amendments`
- `block_goal4932_result`

## Files To Review

- `history/internal_docs/goal4932_host_columnar_generic_grouped_sequence_assembly_result_2026-07-03.md`
- `src/rtdsl/output_assembly.py`
- `src/rtdsl/__init__.py`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py`
- `tests/goal4932_generic_output_assembly_test.py`
- `history/internal_docs/goal4931_generic_output_assembly_layer_design_2026-07-03.md`
- `history/internal_docs/antigravity_goal4931_generic_output_assembly_layer_design_review_2026-07-03.md`

## Questions For Reviewer

1. Does Goal4932 stay within the Stage A host-columnar prototype authorized by
   Goal4931?
2. Is `output_assembly.py` generic rather than app-identity-specific?
3. Is the API surface (`GroupedSequenceAssemblyPlan`,
   `GroupedSequenceAssemblyResult`, `assemble_grouped_sequences`) appropriate
   for a generic RTDL output-assembly layer?
4. Do the tests prove deterministic grouping, ordering, validity filtering, and
   dedupe behavior?
5. Does the non-RayJoin spatial join grouped-pairs test satisfy the first
   genericity proof gate?
6. Is the Section 5.7-like test correctly bounded as a structural shape proof
   rather than full RayJoin writer evidence?
7. Does the tiny app-adapter byte-equality test prove real RayJoin app-layer
   wiring without overclaiming public-sample coverage?
8. Does the report correctly avoid performance claims and device/native claims?
9. Is Goal4933, a RayJoin public-sample generic assembly POD smoke, the right
   next goal before any performance claim?

## Non-Authorization

This review must not authorize:

- v2.14.2 release wording;
- broad performance claims;
- device-resident row-buffer implementation;
- native RTDL traversal changes;
- RayJoin text/topology formatting in RTDL core;
- Layer 4 in-traversal fusion.
