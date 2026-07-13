# Call For Review - Goal5128 Non-Hausdorff Max-Nearest Consumer

Please strictly review Goal5128.

Files to inspect:

- `history/internal_docs/goal5128_non_hausdorff_max_nearest_consumer_2026-07-08.md`
- `tests/goal5128_non_hausdorff_max_nearest_consumer_test.py`
- `src/rtdsl/partner_continuations.py`
- `history/internal_docs/xhd_review_opinions_register_2026-07-07.md`

Review questions:

1. Does the new test provide a genuine non-Hausdorff consumer for
   `max_nearest_distance_witness_numpy_columns`?
2. Does the facility-service-radius scenario avoid directed-Hausdorff / X-HD /
   paper-app identity?
3. Does the test directly consume the generic pipeline rather than calling
   `directed_hausdorff_*` wrappers?
4. Are the expected nearest witnesses and worst-served-demand result correct?
5. Does this close the Goal5127 non-blocking genericity note?
6. Are the claim boundaries conservative (no performance, no native/RT-core, no
   paper reproduction claim)?

Expected verdict labels:

- `approve_goal5128_non_hausdorff_max_nearest_consumer`
- `approve_with_required_amendments`
- `block_due_to_not_actually_independent_consumer`
