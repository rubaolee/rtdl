# External Review - Goal5452 Paper-Apps Readiness

Date: 2026-07-10

## Verdict

```text
approve_with_required_amendments
```

## Summary

The four-app portfolio snapshot is an honest readiness record. Every app keeps
its scoped result separate from full-paper reproduction, the reported numbers
and boundaries agree with the underlying reviewed packets, and the stale
scaffold/current-status regression is covered by tests.

## Required Amendment

### RA-1 - RayJoin review evidence did not cover the scientific claim

The snapshot originally cited
`review_v2_14_4_all_open_review_debt_2026-07-06.md` as the sole evidence for
the RayJoin Sections 5.2/5.3/bounded-5.7 reproduction status. That review
covers v2.14.4 API/export/release consolidation, not the scientific
reproduction closeout.

The RayJoin record must instead cite the Antigravity scientific reviews for:

```text
Section 5.2 AuthorOfficial revalidation;
Section 5.3 AuthorOfficial reproduction;
bounded Section 5.7 County x Zipcode byte equality;
Section 5.7 regression hardening.
```

The v2.14.4 review may remain only as additional API/performance-boundary
evidence.

## Non-Blocking Notes

1. Tests should validate that review files contain the app identity and
   approval terms, not merely that the path exists.
2. Each app should record the reviewer/source of external review.
3. Verified sign-off files faithfully reflect prior verdicts, but long-term
   review provenance is strongest when the reviewer directly creates or
   confirms the sign-off.

## Review Answers

1. The four scoped statuses are distinct from full-paper reproduction.
2. RayJoin timing and semantic caveat are stated together.
3. RT-BarnesHut keeps both the favorable narrow phase and unfavorable broader
   envelope.
4. RT-DBSCAN does not claim exact paper preprocessing or broad author-semantic
   equivalence.
5. X-HD remains limited to same-input directed-HDResult reproduction.
6. No historical review-pending artifact was silently upgraded, but the
   RayJoin evidence pointer requires RA-1.
7. The RTDL-core versus app-owned boundary remains explicit.
8. The stale scaffold/current-status regression is covered; review relevance
   checking should be strengthened.

After RA-1 and the relevance-test hardening are implemented, Goal5452 may be
re-reviewed for an unconditional readiness verdict.
