# Goal 437: v0.7 RT DB Repeated-Query Performance Gate

## Goal

Measure the repeated-query performance model that actually matters for the
native prepared DB dataset direction.

## Required outcome

- Linux performance gate with PostgreSQL included
- RTDL:
  - build native prepared dataset once
  - execute many bounded queries
- PostgreSQL:
  - setup/index once
  - execute the same query family many times
- report:
  - build/setup time
  - per-query time
  - total time over query batches
  - break-even discussion

## Review requirement

This goal requires at least 2-AI consensus before closure.
