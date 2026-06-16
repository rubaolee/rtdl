# Goal4432 V3.0 M35 Aggregate-Frontier Device Columns Contract

## Decision

M35 turns the M34 Barnes-Hut finding into an app-agnostic implementation target:
`AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D`. The contract is specified and exported,
but deliberately marked `specified_not_implemented` and `executable=false`.

M34 showed that the existing Embree/OptiX aggregate-frontier row ABI is a
host-materialized frontier collector. At 8,192 points it emitted 3,440,003 rows,
and OptiX was only 1.005x faster than Embree by wrapper median. That result is a
contract diagnosis, not a backend conclusion.

## Contract Target

The new contract requires a native producer that writes generic aggregate-frontier
device columns:

- `source_id`
- `frontier_kind_code`
- `item_id`
- `owner_aggregate_id`
- `dfs_index`
- `resume_index`
- `metadata_flags`
- `row_offsets`

The handoff must be device-resident, same-stream or event-ordered, and consumable
by a partner without copying frontier rows to host before continuation.

## Boundary

The contract forbids app reductions, force laws, whole-solver logic, automatic
partner selection, and host frontier-row materialization in the hot path. It
authorizes no public speedup wording, no RT-core speedup wording, no whole-app
wording, no true-zero-copy wording, and no implementation claim.

## Next Implementation Step

Implement the first `optix` native producer symbols named by
`AGGREGATE_FRONTIER_DEVICE_COLUMNS_REQUIRED_SYMBOLS`, then connect the produced
columns to the existing grouped-vector partner continuation with explicit stream
or event ordering and transfer counters.
