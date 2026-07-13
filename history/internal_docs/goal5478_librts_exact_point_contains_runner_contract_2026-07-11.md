# Goal5478: LibRTS Exact Point-Contains Runner Contract

Date: 2026-07-11

## Objective

Prepare the smallest denominator-aligned exact-input gate while the official AE
archive downloads. Do not run or claim the gate before verified extraction.

## Selected Workload

```text
paper target: Figure 6 point-contains
geometry: datasets/polygons/dtl_cnty.wkt
query: datasets/queries/point-contains_queries_100000/dtl_cnty.wkt
author log identity: 12,234 geometries / 100,000 points / 136,475 results
author denominator: internal Query Time; Loading Time excluded
```

This is the smallest paper-log point workload and maps directly to RTDL's
generic `expanded_aabb_point_membership_rows_2d` primitive.

## Contract

The app-owned runner:

```text
Paper-reproduction-apps/librts-paper/run_exact_point_contains_count_gate.py
```

requires both a size+MD5 verified archive result and a safely extracted result.
Both input files must resolve under the verified extraction root. It passes the
same WKT files to the author query binary and RTDL, converts each geometry to
its 2-D MBR, and runs RTDL OptiX with a fail-closed row capacity derived from
the author result count plus margin.

The author executable exposes only a result count, not pair rows. Therefore the
gate can close same-input count agreement only. Author Loading Time, internal
Query Time, RTDL WKT load, RTDL primitive query, and route wall remain separate;
no ratio is authorized by this runner.

## Validation

Three tests pass for robust WKT numeric/spacing parsing, author output fields,
and rejection of unverified/outside-extraction inputs. No real archive input or
GPU execution occurs in Goal5478.

## Boundary

Not claimed: exact-input count result, author pair-row agreement, Figure 6
reproduction, performance ratio, complete paper reproduction, or Embree.

## Exit

```text
completed_exact_point_contains_runner_contract__execution_pending_verified_archive__review_pending
```
