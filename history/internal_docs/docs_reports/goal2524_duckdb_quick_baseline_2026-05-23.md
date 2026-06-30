# Goal2524 DuckDB Quick Baseline For RayDB-Style RTDL

Date: 2026-05-23

## Verdict

Goal2524 adds a pod-backed DuckDB quick baseline for the same tiny RayDB-style
grouped aggregate contract.

DuckDB is useful here because it is embedded, reproducible, and easy to bind to
the exact synthetic fixture. It is not a GPU database baseline and does not
authorize public performance wording.

## Pod Evidence

Pod:

```text
ssh root@213.173.108.13 -p 15902 -i ~/.ssh/id_ed25519_rtdl_codex
hostname: 57449dd4f93c
```

DuckDB install:

```text
venv: /tmp/rtdl_goal2524_venv
duckdb: 1.5.3
```

Artifact:

- `docs/reports/goal2524_duckdb_quick_baseline_pod_2026-05-23.json`

Runner:

```bash
python3 scripts/goal2524_duckdb_quick_baseline.py \
  --repeats 500 \
  --output docs/reports/goal2524_duckdb_quick_baseline_pod_2026-05-23.json
```

## Contract Timed

The DuckDB runner creates an in-memory table with the same eight rows and runs
one grouped SQL query that computes:

- grouped count;
- grouped sum;
- grouped min;
- grouped max;
- decomposed sum/count for `avg_as_sum_count`.

The result is remapped to the same five RTDL result modes and compared with the
CPU reference rows.

## Result

500 repeats on the pod:

| Case | Median ms | Notes |
| --- | ---: | --- |
| Python reference | 0.00881 | In-process tiny fixture reference |
| DuckDB single grouped SQL query | 1.215755 | Embedded in-memory DuckDB 1.5.3 |
| DuckDB / Python median ratio | 138.00x | Diagnostic tiny-fixture ratio only |

Correctness:

```text
all_match_cpu_reference: true
```

Interpretation: DuckDB is a clean correctness-compatible embedded SQL baseline,
but for this eight-row fixture the SQL engine overhead dominates. This result
is expected and should not be generalized to larger analytical workloads.

## Claim Boundary

This diagnostic result does not authorize public speedup, whole-DBMS,
authors-code, RayDB reproduction, true zero-copy, or GPU-database claims.

Allowed:

- DuckDB can express the same RayDB-style tiny fixture contract.
- On this pod and this tiny fixture, the DuckDB diagnostic median was
  `1.215755 ms`.

Blocked:

- public speedup wording;
- whole-DBMS performance claim;
- RayDB or authors-code comparison;
- true zero-copy claim;
- GPU database claim.
