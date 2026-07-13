# Call For Review — Goal4834 RayJoin SoS Contract Repair and Synthetic Gate

Date: 2026-06-30

Requested verdict labels:

- `approve_goal4834_correctness_repair_no_performance_win_claim`
- `approve_with_required_amendments`
- `fail_redo_goal4834`

## Files To Review

- `history/internal_docs/goal4834_completion_report_2026-06-30.md`
- `history/internal_docs/goal4834_author_sos_t_reported.patch`
- `history/internal_docs/goal4834_author_patch_scope.md`
- `history/internal_docs/goal4834_contract_alignment_notes_2026-06-30.md`
- `history/internal_docs/goal4834_synthetic_cases.md`
- `history/internal_docs/goal4834_synthetic_gate_summary.json`
- `history/internal_docs/goal4834_author_patched_public_sample_summary.json`
- `history/internal_docs/goal4834_rtdl_rebuilt_public_sample_iter0_summary.json`
- `history/internal_docs/goal4834_public_sample_patched_author_vs_rtdl_perf_summary.json`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/rtdsl/rayjoin_overlay.py`
- `tests/goal4834_rayjoin_sos_synthetic_contract_test.py`
- `tests/goal4373_rayjoin_cdb_point_location_route_test.py`
- `tests/goal4374_rayjoin_exact_paper_suite_test.py`

## Review Questions

1. Is the equal-height comparator change in `rtdl_optix_core.cpp` a valid
   directed point-location SoS contract repair rather than a RayJoin-only hidden
   shortcut?
2. Does the implementation align with the author clarified intended behavior:
   query map 0 prefers larger slope, query map 1 prefers smaller slope?
3. Are the synthetic tests sufficient to prove the intended contract on
   controlled cases before relying on POD evidence?
4. Is the patched-author baseline patch properly scoped to the author clarified
   intended SoS behavior, rather than changing overlay semantics arbitrarily?
5. Does the rebuilt RTDL OptiX public-sample result prove byte-for-byte
   correctness on County x Soil?
6. Is the bounded 3-run performance smoke interpreted honestly, especially that
   RTDL does not beat the patched-author median in this run?
7. Does the report correctly avoid broad Section 5.7, broad RayJoin, broad RTDL,
   or Embree claims?
8. Should Goal4834 close with label
   `completed_correctness_repair__public_sample_byte_equal__no_performance_win_claim`?

## Non-Authorization

This review must not authorize:

- full Section 5.7 eight-pair reproduction;
- any broad performance claim;
- claim that RTDL is faster than the patched author on this public sample;
- V3/V4 work;
- Embree work;
- user-facing public documentation changes.
