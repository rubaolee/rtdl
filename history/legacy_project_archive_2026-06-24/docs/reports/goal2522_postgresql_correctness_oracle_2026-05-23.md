# Goal2522 PostgreSQL Correctness Oracle For RayDB-Style RTDL

Date: 2026-05-23

## Verdict

Goal2522 adds a PostgreSQL correctness-oracle runner for the RayDB-style
columnar aggregate benchmark slice.

Pod execution passed. PostgreSQL returned exact row parity with the RTDL
CPU-reference contract for grouped `count`, `sum`, `min`, `max`, and
`avg_as_sum_count`.

This goal does not produce or authorize a PostgreSQL performance comparison.

## Why PostgreSQL Fits Here

The current RayDB-style RTDL app is not a full DBMS benchmark. It is a tiny
contract harness for grouped columnar predicates and reductions:

- same input rows and columns;
- same predicates;
- same grouping key;
- same aggregate modes;
- same compact grouped result shape.

PostgreSQL is useful as an independent SQL semantics oracle for this contract.
It is not evidence that RTDL is faster or slower than PostgreSQL, RayDB, or any
other database system.

## Runner

Script:

```bash
PYTHONPATH=src:. python3 scripts/goal2522_postgresql_correctness_oracle.py \
  --output docs/reports/goal2522_postgresql_correctness_oracle_2026-05-23.json
```

With a specific PostgreSQL connection:

```bash
PYTHONPATH=src:. python3 scripts/goal2522_postgresql_correctness_oracle.py \
  --dsn "$RTDL_POSTGRES_DSN" \
  --output docs/reports/goal2522_postgresql_correctness_oracle_2026-05-23.json
```

The runner:

- creates a temporary `rtdl_goal2522_raydb_style_fixture` table;
- inserts the eight-row denormalized fixture;
- applies `ship_year BETWEEN 1994 AND 1995`;
- applies `discount BETWEEN 4 AND 6`;
- applies `quantity < 25`;
- groups by `region_id`;
- computes grouped `count`, `sum`, `min`, `max`, and `avg_as_sum_count`;
- returns a single JSON object from PostgreSQL;
- compares PostgreSQL rows against the RTDL CPU-reference contract rows;
- records a blocked artifact instead of failing when `psql` or a server is not
  available.

## Expected Contract Rows

The expected rows recorded in the artifact are:

```json
{
  "count": [
    {"region_id": 0, "count": 2},
    {"region_id": 1, "count": 1},
    {"region_id": 2, "count": 1}
  ],
  "sum": [
    {"region_id": 0, "sum": 190},
    {"region_id": 1, "sum": 200},
    {"region_id": 2, "sum": 80}
  ],
  "min": [
    {"region_id": 0, "min": 90},
    {"region_id": 1, "min": 200},
    {"region_id": 2, "min": 80}
  ],
  "max": [
    {"region_id": 0, "max": 100},
    {"region_id": 1, "max": 200},
    {"region_id": 2, "max": 80}
  ],
  "avg_as_sum_count": [
    {"region_id": 0, "sum": 190, "count": 2},
    {"region_id": 1, "sum": 200, "count": 1},
    {"region_id": 2, "sum": 80, "count": 1}
  ]
}
```

`avg_as_sum_count` intentionally records the decomposed sum/count pair. It does
not ask PostgreSQL for scalar `AVG`, because the RTDL app contract lowers
average-like behavior as a generic fused sum/count primitive.

## Pod Result

Artifact:

- `docs/reports/goal2522_postgresql_correctness_oracle_2026-05-23.json`

Pod:

```text
ssh root@213.173.108.13 -p 15902 -i ~/.ssh/id_ed25519_rtdl_codex
hostname: 57449dd4f93c
```

Observed status:

```text
ok
```

Observed PostgreSQL path:

```text
/usr/bin/psql
```

Observed result:

```text
all_match_cpu_reference: true
matches_cpu_reference_by_mode: count/sum/min/max/avg_as_sum_count all true
```

Local Mac note: local execution before the pod run was blocked because `psql`
was not installed on the Mac (`psql executable not found: psql`). The checked-in
artifact now records the pod success result.

## Claim Boundary

The JSON payload includes this boundary:

```text
PostgreSQL is used only as an external SQL correctness oracle for the tiny
RayDB-style synthetic fixture. This does not authorize PostgreSQL performance,
whole-DBMS, authors-code, RayDB reproduction, true zero-copy, or public speedup
claims.
```

Allowed after this goal:

- say that RTDL has a ready PostgreSQL correctness-oracle runner for the
  RayDB-style tiny fixture;
- run the oracle in any environment that has `psql` and PostgreSQL access;
- use PostgreSQL rows as an independent SQL-semantics check once the runner
  reports `status: ok`.

Blocked after this goal:

- RTDL-vs-PostgreSQL performance comparison;
- RTDL-vs-RayDB or authors-code comparison;
- public speedup wording;
- SQL engine or DBMS feature claim;
- whole-app database benchmark claim.

## Next Baseline Sequence

The clean sequence is:

1. PostgreSQL correctness oracle: run this Goal2522 script in a PostgreSQL
   environment and require exact row parity.
2. PostgreSQL diagnostic timing: only after correctness passes, add a separate
   timing runner with fixed process, connection, table, query, and result
   materialization boundaries.
3. DuckDB quick baseline: use DuckDB before a GPU database because it is
   embedded, reproducible, and easier to bind to the exact same tiny contract.
4. GPU database baseline: evaluate only if a candidate has a stable local
   install path, clear license, and a small-query API that can express this
   exact fixture without turning into a separate database project.
