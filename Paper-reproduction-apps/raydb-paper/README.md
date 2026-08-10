# RayDB Paper Reproduction App

This app evaluates RTDL against *RayDB: Building Databases with Ray Tracing
Cores* (PVLDB 19(1), 2025), using the pinned author artifact at commit
`a610c00d7334d8907435cc0a124f9ca8392ee456`.

## Current Status

```text
scoped_generated_ssb_correctness_and_system_extraction_complete
```

RTDL, the pinned RayDB executable, and an independent DuckDB relational oracle
produce identical complete grouped-result rows for all 13 RayDB SSB queries at
both SF10 and SF20. The same hashed packet bytes are supplied to the author and
RTDL paths.

| Scale | `lineorder` rows | Queries | RTDL partitions/query | Complete rows equal |
|---:|---:|---:|---:|---|
| SF10 | 59,986,052 | 13/13 | 12 x at most 5M rows | yes |
| SF20 | 119,994,608 | 13/13 | 24 x at most 5M rows | yes |

The inputs are deterministic same-source SSB generations from pinned
`ssb-dbgen` commit `0741e06d4c3e811bcec233378a39db2fc0be5d79` with recorded
table hashes and construction provenance. They are not established as the
paper's exact input bytes.

The author source is admitted by an app-owned policy: pinned remote and commit,
complete Git identity, exactly one tracked `Makefile` modification, and a
tracked-diff hash equal to the approved GCC-path compatibility patch
(`2cd73c8...e4388`). The machine closeout binds that patch and validates the
same policy for every archived author child. Repository paths remain host-local
and are not pinned.

## What Is Compared

For each of `q11`, `q12`, `q13`, `q21`, `q22`, `q23`, `q31`, `q32`, `q33`,
`q34`, `q41`, `q42`, and `q43`:

```text
pinned generated SSB tables
-> app-owned DuckDB query and RayDB packet lowering
-> identical hashed data/predicate packet
-> pinned RayDB author executable
-> RTDL generic partitioned grouped-i64 route
-> complete canonical nonzero (group tuple, aggregate value) rows
```

Correctness is exact integer row equality. `Line Num`, aggregate totals,
checksums, and timing are not used as substitutes for the result relation.
The packet, child-artifact, author-binary, runner, RTDL-code, native-library,
host, and GPU identities are bound into each scale's execution cohort. The
author source identity and tracked diff were recorded by every author child and
are audited exactly across both archived matrices. They were not locked in the
original v1 cohort before execution; future runs use cohort v2, which adds that
pre-execution source lock.

## RTDL Program Shape

The RayDB-specific program remains in this app:

```python
partitions = lower_ssb_query_to_ray_triangle_partitions(
    tables,
    query_contract,
    partition_rows=5_000_000,
)

result = run_partitioned_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
    rays,
    partitions,
    group_count=query_contract.group_count,
    expected_primitive_count=lineorder_row_count,
    reduction="sum",
    backend="optix",
)
```

SSB joins, predicates, categorical encodings, SQL, packet layout, and canonical
output comparison are app-owned. RTDL sees only rays, triangles, stable
primitive ids, group ids, signed integer values, and a reduction operation.

The extracted RTDL system capability is app-neutral:

- bounded partition execution with exact contiguous primitive-id coverage;
- prepared ray-batch reuse across partitions;
- grouped `count`, `sum`, `min`, `max`, and `sum_count`;
- signed-int64 values with pre-launch overflow rejection;
- legacy unsigned ABI compatibility plus explicit signed-v2 native symbols;
- per-partition ledgers, standard FNV-1a row checksums, and reconciled timing;
- fail-closed gap, overlap, tail, group-range, ABI, and deduplication checks.

A non-RayDB surface-patch consumer and the generic hardware gate exercise the
same partition and reduction contract without SQL or paper semantics.

## Performance Result

The only direct author/RTDL comparison is the same-host, same-packet
`optixLaunch + synchronize` phase. Its phase boundary is aligned, but its
launch topology is not: the author uses one monolithic launch while RTDL uses
bounded sequential partitions.

| Scale | Author launch median | RTDL partition-launch sum median | Faster |
|---:|---:|---:|---|
| SF10 | 0.439941 ms | 4.054084 ms (12 launches) | author, 13/13 |
| SF20 | 0.767822 ms | 8.159624 ms (24 launches) | author, 13/13 |

This is an unfavorable result for RTDL's partitioned launch phase. It is not a
Figure 12, whole-program, cross-query aggregate, or paper-performance ratio.

A separate SF10 q11 capacity diagnostic aligns the launch topology at one
59,986,052-row launch. Complete rows still match; the author launch is
5.29199 ms and RTDL is 7.199011 ms, so RTDL remains about 1.36x slower in that
single-query phase diagnostic. RTDL route wall is 74.625 s because monolithic
host triangle packing dominates, so the one-launch result is not a preferred
whole-route execution model.

The main remaining costs are outside traversal:

| Scale | App lowering median | RTDL route median | Prepare/build median |
|---:|---:|---:|---:|
| SF10 | 142.951 s | 12.869 s | 4.593 s |
| SF20 | 306.804 s | 24.287 s | 8.905 s |

Host-side SSB/SQL lowering and partition triangle packing remain material.
Prepared ray reuse does not make this route zero-copy or fully device-resident.

## Historical RayDB Work Is Not Paper Reproduction

RTDL contains older RayDB-shaped benchmark assets under
`examples/current/research_benchmarks/raydb_style/`. This paper app reuses
generic capabilities from that work but does not reclassify historical
synthetic timings or benchmark rows as paper reproduction evidence.

## Claim Boundary

This app claims:

- deterministic same-source SF10 and SF20 execution;
- all 13 queries at each scale;
- identical complete grouped rows across author, DuckDB oracle, and RTDL; and
- a generic signed-i64 bounded-partition system capability.

It does not claim:

- exact paper-input bytes or paper-dataset hashes;
- Figure 12 or the unavailable paper-modified Crystal baseline;
- paper RTX 4090 hardware reproduction;
- paper performance, whole-program speedup, or cross-query aggregate speedup;
- author-algorithm equivalence;
- zero-copy or a fully device-resident database pipeline; or
- full RayDB paper reproduction.

The machine-readable closeout is
[`results/raydb_scoped_closeout.json`](results/raydb_scoped_closeout.json).
