# Goal1989 Database Columnar Payload Fused Batch

Date: 2026-05-14

Status: implementation slice with pod timing

## Why This Goal Exists

Goal1987 replaced the `database_analytics` app-local CuPy RawKernel path with
reusable partner columnar predicate/reduction algebra. That solved the design
problem, but the first generic path was still about 2.6x to 2.8x slower than
the old fused RawKernel because it rebuilt columns from Python row dictionaries
and launched several separate CuPy operations.

Goal1989 fixes the reusable path without adding database logic to the native
engine.

## What Changed

The partner adapter now exposes:

```text
columnar_payload_to_partner_columns(...)
partner_columnar_predicate_reduce_batch(...)
```

`columnar_payload_to_partner_columns` accepts caller-supplied column arrays and
converts them into partner-owned tensors without forcing every app through
Python row dictionaries and categorical string remapping.

`partner_columnar_predicate_reduce_batch` evaluates several summary specs in
one call. On CuPy it generates a fused RawKernel from generic column, predicate,
reduction, grouping, and output-dtype specs. On other partners it preserves the
portable tensor fallback.

The `database_analytics` v2 path now uses the generic columnar-payload plus
fused-summary path rather than the app-local RawKernel helper.

## Pod Timing

Pod:

```text
ssh root@213.173.109.6 -p 31938 -i ~/.ssh/id_ed25519
GPU: NVIDIA RTX 2000 Ada Generation
```

Artifact:

- `docs/reports/goal1989_pod_database_partner_columnar_fused_batch_cupy_perf.json`

The pod compared the old app-local RawKernel reference to the new generic
columnar-payload fused batch path:

| Copies | Rows | App-local RawKernel median s | Generic fused columnar median s | Generic/RawKernel | Correct |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1,000 | 13,000 | 0.009391 | 0.009454 | 1.007x | yes |
| 10,000 | 130,000 | 0.095776 | 0.093369 | 0.975x | yes |
| 50,000 | 650,000 | 0.498285 | 0.475944 | 0.955x | yes |
| 100,000 | 1,300,000 | 0.984043 | 0.954931 | 0.970x | yes |

## Design Lesson

The failed intermediate experiment matters. A fused kernel alone did not help
when the path still paid Python row-dictionary and categorical-remapping costs.
The useful reusable primitive is the combination:

```text
columnar payload handoff + fused batch summaries + explicit output dtype contract
```

The output dtype contract is deliberate. The database example uses `int32`
summary outputs after the caller proves the range is safe, avoiding unnecessary
64-bit contended atomics. This is a generic partner contract, not a database
special case.

## Boundary

This does not customize the RTDL native engine. It does not add SQL, database
planning, indexing, or app-specific kernels to the RTDL engine. It is a partner
continuation facility for caller-supplied columnar payloads.

The timing supports the narrow claim that the database control row can now be
implemented with reusable Python+partner+RTDL machinery at approximately parity
with the old app-local CuPy RawKernel comparison on this pod. It does not
authorize broad whole-app, broad RT-core, package-install, or final v2.0 release
claims.
