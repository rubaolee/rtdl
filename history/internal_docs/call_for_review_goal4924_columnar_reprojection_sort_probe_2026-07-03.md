# Call For Review: Goal4924 Columnar Reprojection/Sort Probe

Date: 2026-07-03

Please review:

- `history/internal_docs/goal4924_columnar_reprojection_sort_probe_result_2026-07-03.md`
- `history/internal_docs/goal4924_columnar_reprojection_sort_probe.py`
- `history/internal_docs/goal4924_workspace_api_smoke.py`
- `history/internal_docs/goal4924_order_diff_probe.py`
- `history/internal_docs/goal4924_order_diff_after_gcd_summary_2026-07-03.json`
- `history/internal_docs/goal4924_workspace_scaled_int_hooked_rerun_summary_2026-07-03.json`

Requested verdict labels:

- `approve_goal4924_correct_but_not_fast_stop_path`
- `approve_with_required_amendments`
- `reject_goal4924_due_to_correctness_or_boundary_issue`

Questions:

1. Did Goal4924 stay inside the internal RayJoin experiment harness without
   modifying RTDL core, native code, public docs/tutorials/examples, or release
   surface?
2. Is the implementation correctly bounded to app-layer reprojection/sort,
   while preserving public RTDL LSI/PIP primitives and avoiding
   `rtdsl.rayjoin_overlay`?
3. Does the order-diff probe prove that the corrected no-Fraction path matches
   the original Fraction route for row coordinates and map0/map1 sort order?
4. Is the explanation of the two rejected early mistakes accurate:
   whole-dataset edge scaling and missing numerator/denominator reduction?
5. Does the final POD evidence prove byte-for-byte correctness against
   AuthorOfficial on the Australia/South-Australia representative run?
6. Is the performance interpretation honest: sort improved, but
   `reprojection + sort` missed `<=0.45s`, and hot body missed `<=3.45s`?
7. Is the conclusion correct that further Python/Numba micro-optimization is
   not justified for this workload?
8. Does the report preserve the correct non-authorization boundaries: no broad
   RTDL speed claim, no productizing the wrapper, no full eight-pair Section 5.7
   claim, and no raw OptiX callback exposure?

Recommended verdict:

`approve_goal4924_correct_but_not_fast_stop_path`

Reviewer note:

This is intentionally a negative/stop result. A good review should not reward
the fact that the sort got faster unless the hard bars and correctness boundary
are both satisfied. The main question is whether the stop conclusion follows
from the evidence.
