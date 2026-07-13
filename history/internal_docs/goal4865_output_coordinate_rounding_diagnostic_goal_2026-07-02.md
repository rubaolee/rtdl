# Goal4865: Output Coordinate Rounding Diagnostic For Point 172575

Date: 2026-07-02

Depends on:

- Goal4864: streaming compare advanced past chain `41230` and exposed a new
  coordinate-only first difference at line `499960`.

## Purpose

Diagnose the coordinate-only mismatch:

```text
author: -144.125743 64.796193
rtdl:   -144.125743 64.796192
```

The target point id is `172575`, shared by output chains `166685` and `166686`.

## Rules

- no full Section 5.7 rerun;
- no performance run;
- first determine whether this is an original CDB point, an intersection point,
  or a midpoint-derived point;
- compare author output formatting/source with RTDL formatting/source;
- add a small regression before any large confirmation.

## Exit Labels

- `diagnosed_original_cdb_point_formatting_mismatch`
- `diagnosed_intersection_unscale_rounding_mismatch`
- `diagnosed_output_writer_formatting_mismatch`
- `blocked_need_author_formatting_instrumentation`
