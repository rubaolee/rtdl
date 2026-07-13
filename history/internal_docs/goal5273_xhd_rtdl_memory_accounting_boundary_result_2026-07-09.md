# Goal5273 X-HD RTDL Memory Accounting Boundary Result

Date: 2026-07-09

## Verdict

`completed_rtdl_memory_accounting_boundary__figure11_not_reproduced`

Goal5273 defines an app-owned RTDL memory accounting boundary for the X-HD
paper app.  It does **not** reproduce Figure 11 and does **not** claim memory
parity with the author's X-HD logs.

## Inputs

- Author Figure 11 memory matrix:
  `Paper-reproduction-apps/x-hd-paper/results/xhd_goal5272_figure11_author_memory_log_matrix_2026-07-09.json`
- RTDL hd_exec-compatible graphics route artifacts:
  - `xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json`
  - `xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json`
  - `xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json`
  - `xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json`
- Nonzero frontier worklist accounting example:
  `xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json`

## Output Artifact

`Paper-reproduction-apps/x-hd-paper/results/xhd_goal5273_rtdl_memory_accounting_boundary_2026-07-09.json`

Schema:

`rtdl.paper_reproduction.xhd.figure11_rtdl_memory_accounting_boundary.v1`

Status:

`rtdl_memory_accounting_boundary_ready__figure11_not_reproduced`

## Field Mapping

The author Figure 11 X-HD memory log reports these fields:

- `BVH`
- `Grid`
- `MBRs B`
- `WL`
- `WL Heavy Peak`

RTDL can currently account for only part of that shape:

| Author field | RTDL status |
|---|---|
| `BVH` | unavailable; current route metadata does not expose acceleration-structure memory |
| `Grid` | estimated from generic grid-cell column contract |
| `MBRs B` | estimated from occupied cell min/max MBR columns |
| `WL` | estimated from `frontier_row_capacity` when a bounded frontier table exists |
| `WL Heavy Peak` | unavailable; no author-like heavy-cell offload peak in current route |

RTDL also reports RTDL-only fields (`input_column_matrices_and_ids`,
`nearest_state`) separately.  They are not author Figure 11 fields.

## Graphics Rows

For exact-witness route artifacts, the current route does not allocate frontier
rows, so `WL` is estimated as `0.0 MB`.  This is a route-accounting result, not
a Figure 11 reproduction row.

| Workload | Author X-HD total MB | RTDL author-mapped estimated MB excluding unavailable | RTDL total accounted estimated MB excluding unavailable |
|---|---:|---:|---:|
| Dragon / Asian Dragon | 29.618 | 55.526 | 189.055 |
| Dragon / Buddha | 6.186 | 9.038 | 49.002 |
| Thai / Asian Dragon | 72.646 | 55.526 | 432.710 |
| Thai / Buddha | 75.608 | 9.038 | 292.657 |

The fast-scalar Dragon/Buddha route is included only as a frontier worklist
example:

- estimated `WL`: `213.694 MB`
- estimated total accounted excluding unavailable: `262.695 MB`

This example demonstrates that RTDL can estimate bounded frontier row memory
when the route allocates a frontier table.  It is not a Figure 11 row.

## What This Proves

1. RTDL now has an explicit memory-accounting schema for the X-HD paper app.
2. Grid, MBR, frontier-worklist, input-column, and nearest-state estimates are
   computed from route metadata rather than informal prose.
3. Unavailable fields are represented as `status=unavailable...` with
   `bytes=null`, not silently as zero.
4. The Figure 11 gap is now concrete: exact GPU allocator telemetry for BVH and
   an author-like heavy worklist peak are still missing.

## What This Does Not Prove

- It does not reproduce Figure 11.
- It does not measure exact GPU allocator memory.
- It does not measure RTDL BVH / acceleration-structure memory.
- It does not measure an author-like heavy worklist peak.
- It does not claim author memory parity.
- It does not claim a performance ratio.

## Validation

Commands run:

```powershell
py -m unittest tests.goal5273_xhd_rtdl_memory_accounting_test
py -m unittest tests.goal5273_xhd_rtdl_memory_accounting_boundary_artifact_test tests.goal5273_xhd_rtdl_memory_accounting_test
```

Result:

```text
Ran 7 tests in 0.012s
OK
```

## Next Work

The next Figure 11 step should not be another prose table.  It should choose
one of two paths:

1. expose real native/allocator telemetry for unavailable fields (`BVH`,
   `WL Heavy Peak`), or
2. integrate this accounting into the hd_exec-compatible `Running` output with
   explicit per-field status so users can see exactly what is estimated and what
   is unavailable.

Until then, Figure 11 remains `not_reproduced`.
