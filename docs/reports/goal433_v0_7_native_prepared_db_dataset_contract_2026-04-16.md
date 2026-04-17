# Goal 433 Report: v0.7 Native Prepared DB Dataset Contract

Date: 2026-04-16
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_433_v0_7_native_prepared_db_dataset_contract.md`

## Purpose

Goal 432 made the performance problem clear:

- current RTDL `prepare` is dominated by Python-side normalization, encoding,
  and ctypes marshaling
- current RTDL `execute` is comparatively small
- high performance requires Python to become a thin wrapper around native
  prepared dataset and query kernels

Goal 433 defines the contract for that next step.

## Core design

Introduce a native prepared DB dataset object:

- Python owns:
  - API call
  - lightweight schema declaration
  - backend selection
  - query object construction
  - lifetime handle
- native backend owns:
  - row storage ingestion
  - field encoding
  - categorical dictionary encoding
  - RT coordinate encoding
  - RT acceleration structure build
  - query execution
  - candidate/refine work
  - grouped accumulation
  - result buffer ownership

The performance goal is to replace:

- Python-heavy prepare per query

with:

- native dataset build once
- thin Python query launch many times

## Proposed public shape

First-wave Python surface:

```python
dataset = rt.prepare_db_dataset(
    rows,
    backend="embree",
    schema={
        "row_id": "int64",
        "ship_date": "int64",
        "discount": "int64",
        "quantity": "int64",
        "region": "category",
        "revenue": "int64",
    },
)

rows = dataset.conjunctive_scan(
    predicates=(
        ("ship_date", "between", 40, 220),
        ("discount", "between", 3, 7),
        ("quantity", "lt", 20),
    )
)

rows = dataset.grouped_count(
    predicates=(("ship_date", "between", 40, 220),),
    group_key="region",
)

rows = dataset.grouped_sum(
    predicates=(("ship_date", "ge", 60),),
    group_key="region",
    value_field="revenue",
)
```

This is a standard-library/runtime API, not new core language syntax.

## Native ABI contract

Each RT backend should expose a native handle family equivalent to:

- create dataset
  - input:
    - schema
    - rows / column buffers
    - row count
  - output:
    - opaque dataset handle
- destroy dataset
  - input:
    - opaque dataset handle
- query dataset:
  - conjunctive scan
  - grouped count
  - grouped sum

The native dataset handle owns:

- encoded row storage
- field metadata
- dictionary encodings
- RT-ready coordinate representation
- backend acceleration structure

The query calls should take only:

- dataset handle
- predicate clauses
- group/value field names where needed
- output row buffer pointers
- error buffer

## Buffer-transfer requirement

The external review flagged one material implementation risk:

- if large row buffers still cross the Python/native boundary through
  per-row ctypes object construction at dataset creation time, that transfer
  path can simply become the new bottleneck

Therefore Goals `434-436` must address the transfer protocol explicitly.

Acceptable first-wave approaches:

- columnar primitive buffers passed as contiguous native arrays
- binary row-block ingestion with one native decode pass
- memoryview / buffer-protocol input for numeric columns
- backend-owned dictionary encoding for categorical columns

Unacceptable as a performance claim:

- per-row Python object marshaling presented as the final native prepared
  dataset path

The first implementation may still keep a compatibility adapter for Python row
dictionaries, but the report must distinguish:

- compatibility ingestion
- performance-oriented native/columnar ingestion

## First-wave data boundary

Supported first-wave field types:

- `int64`
- normalized date/timestamp encoded as `int64`
- categorical string via native dictionary encoding
- bool as a secondary/refine field

Deferred:

- arbitrary text search
- SQL `LIKE`
- null-heavy SQL semantics
- float aggregate parity
- multi-column group keys

## Query boundary

Supported first-wave queries:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Boundaries retained from Goal 416:

- conjunctive predicates
- up to three primary RT clauses per RT job
- one group key
- integer-compatible grouped sum
- explicit row/candidate/group ceilings

## Correctness gates for Goals 434-436

Each backend implementation must prove:

- direct query results match Python truth
- prepared dataset query results match direct backend query results
- prepared dataset query results match PostgreSQL on Linux
- repeated query results are stable across multiple launches

At minimum:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

must pass on the backend.

## Performance gates for Goal 437

The repeated-query performance gate must compare:

RTDL:

- native dataset build once
- many query executions
- total time over query batch
- per-query median

PostgreSQL:

- setup/index once
- many SQL query executions
- total time over query batch
- per-query median

Required readings:

- build/setup time
- query-only time
- total time for query batches
- break-even query count if present

## Honesty boundary

This contract does not claim:

- RTDL becomes a DBMS
- RTDL replaces PostgreSQL
- arbitrary SQL is supported
- current Goal 432 prepared execution already satisfies this contract

Goal 432 prepared execution is only a measurement split.

Goal 433 defines the next architecture:

- native prepared DB dataset
- Python thin wrapper
- repeated-query performance model
- explicit large-buffer transfer protocol

## Decision

The next implementation order should be:

1. Embree native prepared DB dataset
2. OptiX native prepared DB dataset
3. Vulkan native prepared DB dataset
4. repeated-query PostgreSQL performance gate
5. release-gate refresh
