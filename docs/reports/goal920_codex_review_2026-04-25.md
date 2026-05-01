# Goal920 Codex Review

Date: 2026-04-25

Verdict: ACCEPT

I independently checked the Goal920 promotion against the local changes and
artifacts:

- The RTX artifact covers the bounded `facility_service_coverage` path at
  `copies=20000`, `iterations=10`, `radius=1.0`, with `query_count=80000`,
  `build_count=80000`, `threshold_reached_count=80000`, and separated OptiX
  phases.
- The new same-scale CPU oracle baseline reports `customer_count=80000`,
  `covered_customer_count=80000`, `all_customers_covered=true`, and
  `uncovered_customer_ids=[]`.
- The app still rejects generic OptiX rows mode and only allows the RT-core
  path through explicit `coverage_threshold_prepared`.
- The support matrix, manifest, docs, and tests keep ranked nearest-depot KNN,
  KNN fallback assignment, and facility-location optimization outside the
  claim.

Focused verification passed 52 tests plus `py_compile` and `git diff --check`.
