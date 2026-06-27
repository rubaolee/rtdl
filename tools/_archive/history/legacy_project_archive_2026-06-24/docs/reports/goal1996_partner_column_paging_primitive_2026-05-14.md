# Goal1996 Partner Column Paging Primitive

Date: 2026-05-14

Status: implementation slice

## Why This Goal Exists

Row-output apps remain less favorable than compact count/flag apps because
serializing every witness row back to Python can dominate useful work. Goal1965
added generic partner-side compaction; Goal1996 adds the next small missing
piece: bounded paging over partner-owned columns.

## What Changed

The partner adapter now exposes:

```text
partner_page_columns(columns, offset=..., limit=..., partner=...)
```

It accepts a generic partner-owned column table and returns a bounded slice of
the same columns with metadata recording `offset`, `limit`, `row_count`, and
`source_row_count`.

## Boundary

This is not a new native RTDL engine feature and does not add app-specific row
logic to the engine. It is a generic partner utility for controlling how much
row-output data is exposed to Python after RTDL/native discovery and partner
filtering.

It does not by itself authorize a broad row-output speedup claim. Large pod
timing is still required before claiming that arbitrary row-producing programs
are accelerated end to end.

## Validation

Local validation passed:

```text
py -3 -m unittest tests.goal1996_partner_column_paging_primitive_test \
  tests.goal1965_partner_column_compaction_primitives_test
```
