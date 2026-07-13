# Call For Review - Goal5127 X-HD Generic Nearest Pipeline Extraction

Please strictly review Goal5127.

Files to inspect:

- `history/internal_docs/goal5127_xhd_generic_nearest_pipeline_extraction_2026-07-08.md`
- `src/rtdsl/partner_continuations.py`
- `src/rtdsl/__init__.py`
- `tests/goal5127_xhd_generic_nearest_pipeline_extraction_test.py`
- Existing compatibility tests:
  - `tests/goal5117_generic_3d_hausdorff_column_route_test.py`
  - `tests/goal5115_xhd_rtdl_route_gate_test.py`
  - `tests/goal5118_xhd_bounded3d_rtdl_route_gate_test.py`

Review questions:

1. Does Goal5127 correctly treat Hausdorff distance as an application-level
   composition rather than a core RTDL primitive?
2. Are the new helpers (`pairwise_l2_distance_candidate_rows_numpy_columns`,
   `nearest_witness_numpy_columns`,
   `max_nearest_distance_witness_numpy_columns`) genuinely app-neutral?
3. Did the existing `directed_hausdorff_2d_numpy_columns` and
   `directed_hausdorff_3d_numpy_columns` become compatibility wrappers over the
   generic pipeline rather than independent app-coded implementations?
4. Does the Goal5127 test prove the generic pipeline can reproduce the same
   witness/distance as the existing 3D directed Hausdorff wrapper?
5. Is the core window free of X-HD, paper, author, and `hd_exec` identity?
6. Are the claim boundaries sufficiently conservative, especially no
   performance, no RT-core X-HD, and no full paper reproduction claim?
7. Did this change preserve existing X-HD bounded-route tests?
8. Should any of these helpers remain internal/provisional rather than public
   exports from `rtdsl.__init__`?

Expected verdict labels:

- `approve_goal5127_generic_nearest_pipeline_extraction`
- `approve_with_required_amendments`
- `block_due_to_app_identity_leakage_or_overclaim`
