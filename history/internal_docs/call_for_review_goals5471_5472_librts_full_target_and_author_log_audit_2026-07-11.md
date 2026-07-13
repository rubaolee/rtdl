# Call for Review: Goals5471-5472 LibRTS Full Target And Author-Log Audit

Please strictly review the full-paper target and denominator audit. This packet
does not claim that RTDL has reproduced any complete LibRTS paper figure.

Primary report:

```text
history/internal_docs/goal5471_5472_librts_full_target_and_author_log_denominator_audit_2026-07-11.md
```

Machine evidence:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5471_full_paper_target_availability.json
Paper-reproduction-apps/librts-paper/results/librts_goal5472_author_paper_log_denominators.json
```

Builders and regression:

```text
Paper-reproduction-apps/librts-paper/build_full_paper_target_availability_audit.py
Paper-reproduction-apps/librts-paper/build_author_paper_log_denominator_matrix.py
tests/goal5471_5472_librts_full_target_and_author_log_matrix_test.py
```

Review questions:

1. Are the AE repository and three author submodule commits pinned correctly?
2. Is the final-paper-to-AE-output numbering warning accurate and necessary?
3. Do all 264 logs classify under final-paper Figures 6-12 without omission?
4. Are author logs correctly treated as reference targets rather than RTDL
   reproduction evidence?
5. Are the seven timing-denominator contracts correctly extracted from plotting
   and execution scripts?
6. Are Ray-Multicast log indices correctly normalized from `log2(k)` to actual
   power-of-two `k` values?
7. Does the USCensus extraction match the source log and paper narrative?
8. Is exact-input availability correctly false despite author logs being present?
9. Is postponing POD allocation until inputs and denominators are ready correct?
10. Does the report avoid paper-figure, exact-data, performance-ratio, and Embree
    overclaims?

Requested verdict:

```text
approve_goals5471_5472_librts_full_target_and_author_log_denominator_audit
```
