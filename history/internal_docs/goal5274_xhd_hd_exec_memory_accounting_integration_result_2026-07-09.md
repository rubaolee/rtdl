# Goal5274 X-HD hd_exec-Compatible Memory Accounting Integration Result

Date: 2026-07-09

## Verdict

`completed_hd_exec_status_bearing_memory_accounting_integration__figure11_not_reproduced`

Goal5274 integrates the Goal5273 RTDL memory-accounting boundary into the
app-owned RTDL `hd_exec`-compatible entrypoint.  This is a user-facing JSON
integration step, not new allocator telemetry and not Figure 11 reproduction.

## What Changed

Updated:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

New CLI option:

```text
--include-memory-accounting
```

When enabled, the RTDL entrypoint attaches a status-bearing object under:

```text
Running.Repeats[0].Memory
RTDL.memory_accounting
```

The `Running.Repeats[0].Memory` object intentionally is **not** the author's raw
Figure 11 numeric memory dict.  It is a status-bearing RTDL object with explicit
semantics:

```text
RTDL status-bearing memory accounting for the selected route. This is not the
author's Figure 11 Memory schema, not exact GPU allocator telemetry, and not an
author memory parity claim.
```

## Why The Shape Is Different From Author Memory

The author logs store a raw numeric dict such as:

```json
{
  "BVH": 1920,
  "Grid": 48,
  "MBRs B": 24,
  "WL": 72,
  "WL Heavy Peak": 0
}
```

RTDL currently cannot honestly fill that exact shape because `BVH` and
`WL Heavy Peak` are unavailable.  Writing them as `0` would be false.  Therefore
the RTDL memory field carries per-field status and `bytes=null` for unavailable
fields.

## Output Evidence

Generated example artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5274_hd_exec_memory_accounting_attached_example_2026-07-09.json
```

This example starts from the existing Dragon/Buddha exact-witness
hd_exec-compatible payload and attaches memory accounting.  It does not claim a
new route execution.

Key values:

```text
route_label: cell-mbr-exact-witness
Running.Repeats[0].Memory.Status: status_bearing_rtdl_memory_accounting_attached
Grid estimate: 8.743 MB
BVH status: unavailable_opaque_native_acceleration_memory_not_reported
```

For unsupported public-columnar routes, `--include-memory-accounting` does not
crash and does not invent values.  It emits:

```text
status: memory_accounting_unavailable_for_selected_route
```

with all author-mapped fields unavailable.

## Claim Boundary

Still false:

```text
Figure 11 reproduced
author memory parity
exact GPU allocator measurement
author BVH memory measured by RTDL
author heavy-worklist peak measured by RTDL
performance ratio
```

## Validation

Commands run:

```powershell
py -m unittest tests.goal5274_xhd_hd_exec_memory_accounting_integration_test tests.goal5255_xhd_rtdl_hd_exec_entrypoint_test tests.goal5273_xhd_rtdl_memory_accounting_test
py -m unittest tests.goal5274_xhd_hd_exec_memory_accounting_artifact_test tests.goal5274_xhd_hd_exec_memory_accounting_integration_test tests.goal5273_xhd_rtdl_memory_accounting_boundary_artifact_test
```

Observed:

```text
Ran 11 tests in 1.549s
OK
```

and:

```text
Ran 6 tests in 1.622s
OK
```

## What This Proves

1. The RTDL hd_exec-compatible entrypoint can now emit memory accounting in the
   same broad JSON location as the author (`Running.Repeats[0].Memory`).
2. The emitted memory is status-bearing, so unavailable fields remain visible.
3. The integration is opt-in and does not change default entrypoint output.
4. Unsupported routes fail closed by reporting unavailable fields, not by
   emitting misleading zero totals.

## What This Does Not Prove

- It does not reproduce Figure 11.
- It does not provide exact GPU allocator telemetry.
- It does not measure RTDL BVH memory.
- It does not measure an author-like heavy worklist peak.
- It does not make RTDL's Memory field denominator-compatible with author
  Figure 11 logs.

## Next Work

The next hard step remains native telemetry:

```text
Expose actual acceleration-structure/BVH memory and heavy-worklist peak
telemetry, or explicitly close Figure 11 as not reproducible under current RTDL
instrumentation.
```

Until then, Figure 11 remains `not_reproduced`.
