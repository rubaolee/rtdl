# Goal2523 PostgreSQL Diagnostic Timing For RayDB-Style RTDL

Date: 2026-05-23

## Verdict

Goal2523 adds pod-backed PostgreSQL diagnostic timing for the same tiny
RayDB-style grouped aggregate contract validated in Goal2522.

This is not public performance evidence. It is a same-host engineering
diagnostic for one exact SQL contract.

## Pod Evidence

Pod:

```text
ssh root@213.173.108.13 -p 15902 -i ~/.ssh/id_ed25519_rtdl_codex
hostname: 57449dd4f93c
```

PostgreSQL:

```text
PostgreSQL 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
```

Artifact:

- `docs/reports/goal2523_postgresql_diagnostic_timing_pod_2026-05-23.json`

Runner:

```bash
python3 scripts/goal2523_postgresql_diagnostic_timing.py \
  --repeats 500 \
  --output docs/reports/goal2523_postgresql_diagnostic_timing_pod_2026-05-23.json
```

The pod ran the script as the `postgres` user so local peer authentication could
use `/usr/bin/psql`.

## Contract Timed

The timed PostgreSQL region performs one combined grouped aggregate query over
the eight-row fixture:

- filter `ship_year BETWEEN 1994 AND 1995`;
- filter `discount BETWEEN 4 AND 6`;
- filter `quantity < 25`;
- group by `region_id`;
- materialize grouped `count`, `sum`, `min`, `max`, and decomposed
  `avg_as_sum_count`.

The Python reference timing computes the same five result modes over the same
fixture in-process.

## Result

500 repeats on the pod:

| Case | Median ms | Notes |
| --- | ---: | --- |
| Python reference | 0.00914 | In-process tiny fixture reference |
| PostgreSQL server-side query | 0.096 | PL/pgSQL loop using `clock_timestamp()` |
| PostgreSQL / Python median ratio | 10.50x | Diagnostic tiny-fixture ratio only |

Interpretation: for this very small fixture, PostgreSQL is slower than the
in-process Python reference because the DB executor and JSON materialization
overheads dominate. This says nothing about larger data, indexing, persistent
tables, parallel query, or DBMS-scale workloads.

## Claim Boundary

This diagnostic result does not authorize public speedup, whole-DBMS,
authors-code, RayDB reproduction, true zero-copy, or GPU-database claims.

Allowed:

- PostgreSQL can express the same RayDB-style tiny fixture contract.
- On this pod and this tiny fixture, the PostgreSQL diagnostic median was
  `0.096 ms`.

Blocked:

- public speedup wording;
- whole-DBMS performance claim;
- RayDB or authors-code comparison;
- true zero-copy claim;
- GPU database claim.
