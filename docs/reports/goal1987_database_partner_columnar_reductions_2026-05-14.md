# Goal1987 Database Partner Columnar Reductions

Date: 2026-05-14

Status: implementation slice with pod timing

## Why This Goal Exists

The `database_analytics` v2 row was fast after the user-approved RawKernel
control path, but that left a design debt: the speedup depended on an app-local
DB kernel instead of reusable partner algebra.

Goal1987 adds generic partner columnar primitives:

```text
columnar_rows_to_partner_columns(...)
partner_columnar_predicate_mask(...)
partner_columnar_predicate_reduce(...)
```

The database control path now uses those primitives for the `cupy` and `torch`
partner modes. The old RawKernel helper remains in the file as a comparison
baseline and compatibility reference, but it is no longer the selected `cupy`
path for `run_database_analytics_rawkernel`.

## Boundary

This does not add database logic to the native engine. It is not SQL, query
planning, indexing, transactions, or an engine DBMS. It is generic columnar
predicate filtering plus scalar/grouped count/sum/ids reductions.

It is also not a final performance win over a fused custom RawKernel. The
generic path is correct and reusable, but it currently launches multiple
partner operations and is slower than the old fused app-local kernel.

## Pod Timing

The RTX 2000 Ada pod compared the old fused RawKernel helper to the new generic
CuPy columnar reduction path:

| Copies | Rows | RawKernel median s | Generic columnar median s | Generic/RawKernel | Correct |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1,000 | 13,000 | 0.009256 | 0.024307 | 2.626x | yes |
| 10,000 | 130,000 | 0.093420 | 0.241647 | 2.587x | yes |
| 50,000 | 650,000 | 0.483471 | 1.329504 | 2.750x | yes |
| 100,000 | 1,300,000 | 0.961816 | 2.649347 | 2.755x | yes |

Artifact:

- `docs/reports/goal1987_pod_database_partner_columnar_reductions_cupy_perf.json`

## Design Lesson

This solves the app-customization design problem for the database control row:
the v2 path can now be written as reusable columnar predicate/reduction algebra.

It does not fully solve the performance problem. To match custom RawKernel
performance without app-local code, v2 needs a reusable fused/batched partner
columnar summary primitive that can evaluate several predicates and grouped
reductions in one pass.
