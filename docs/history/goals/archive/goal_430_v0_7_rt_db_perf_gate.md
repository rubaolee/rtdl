# Goal 430: v0.7 RT DB Performance Gate

## Goal

Measure the first bounded `v0.7` DB workload family across implemented RT
engines against PostgreSQL.

## Required outcome

- bounded performance runs for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- explicit boundary between correctness and performance claims
- PostgreSQL remains the external database baseline

## Review requirement

This goal requires at least 2-AI consensus before closure.
