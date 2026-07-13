# Call For Review: Goal5488 LibRTS Columnar Prepared-Phase Loader

Please review the implementation and POD evidence:

```text
history/internal_docs/goal5488_librts_prepared_phase_columnar_loader_result_2026-07-12.md
Paper-reproduction-apps/librts-paper/run_exact_point_contains_count_gate.py
Paper-reproduction-apps/librts-paper/run_exact_point_contains_prepared_phase_columns_gate.py
Paper-reproduction-apps/librts-paper/results/librts_goal5488_dtl_cnty_prepared_phase_columns.json
Paper-reproduction-apps/librts-paper/results/librts_goal5488_lakes_bz2_prepared_phase_columns.json
```

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / revise
Blocking findings:
Required amendments:
Non-blocking notes:
Correctness and input identity:
Phase-accounting assessment:
Generic-system boundary:
```

## Review Questions

1. Do both exact inputs match the author count through the columnar route?
2. Are the input SHA-256 values unchanged from the verified archive members?
3. Does the new app route call the generic `Aabb2DColumns` API rather than a
   LibRTS-specific native helper?
4. Are WKT load, prepare, prepared query, and native primitive phases kept
   separate?
5. Is the `66.311s -> 0.856s` prepare-phase movement described as evidence of
   removed host packing rather than an end-to-end speedup claim?
6. Is the higher single-run `lakes.bz2` query wall treated honestly as an
   uncontrolled fresh-process/first-use observation rather than regression
   proof?
7. Does the route avoid claiming device zero-copy or device-resident index
   construction?
8. Are Figure 6, pair-row equality, performance ratio, full-paper reproduction,
   and Embree correctly left closed?
9. Does the app keep ownership of WKT parsing and input provenance while RTDL
   owns only the generic AABB column contract?
10. Are next measurements required to use repeated clean/warm regimes before
    any performance conclusion?

Please inspect the two JSON artifacts directly and do not infer a ratio from
the phase table. The old and new runs were not a controlled median-of-N matrix.
