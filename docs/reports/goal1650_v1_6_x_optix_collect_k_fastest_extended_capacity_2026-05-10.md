# Goal1650 v1.6.x OptiX Collect-K Fastest Extended Capacity

## Verdict

`fastest_candidate_extended_capacity_enabled`

The opt-in `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` path now uses the existing 128-tile extended row-width-2 capacity without requiring the separate `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1` flag.

## Problem

The v1.6.x long-workload performance target uses `COLLECT_K_BOUNDED` counts above the base 64-tile limit. The code already had an extended 128-tile diagnostic capacity, but the fastest candidate did not automatically select it.

On the A4500 pod at commit `f5af8d17391e59a5ebecc75b71dffa9e7152af29`:

- `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` alone timed out for `candidate_count=196608` and `262144` in 30 seconds, producing only empty JSONL files.
- Adding `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1` restored the tiled path:
- `candidate_count=196608`: `total_ms=0.556595`, `merge_sync_ms=0.234059`, parity accepted.
- `candidate_count=262144`: `total_ms=0.681118`, `merge_sync_ms=0.324099`, parity accepted.

This showed that the immediate long-workload blocker was not a new algorithm requirement for those counts; it was that the fastest opt-in path did not include the already validated extended capacity.

## Change

The fastest candidate now selects the extended 128-tile capacity:

`collect_k_use_fastest_candidate() || collect_k_extended_128_tile_diagnostic()`

The Python expected-path helper was also updated so validation expects the tiled path up to `262144` whenever `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` is enabled.

The separate diagnostic flag remains valid for isolated experiments. This change only affects callers that have already opted into `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`.

## Post-Change A4500 Evidence

After the change was applied to the A4500 pod checkout and rebuilt, the following commands passed with only `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`; `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC` was not set.

- `candidate_count=196608`: `total_ms=0.553565`, `merge_sync_ms=0.231468`, path `row_width2_bounded_multi_tile_sort_merge`, accepted parity.
- `candidate_count=262144`: `total_ms=0.683538`, `merge_sync_ms=0.312909`, path `row_width2_bounded_multi_tile_sort_merge`, accepted parity.

Artifacts:

- `docs/reports/goal1650_post_fastest_196608.json`
- `docs/reports/goal1650_post_fastest_196608.jsonl`
- `docs/reports/goal1650_post_fastest_196608.md`
- `docs/reports/goal1650_post_fastest_262144.json`
- `docs/reports/goal1650_post_fastest_262144.jsonl`
- `docs/reports/goal1650_post_fastest_262144.md`

## Claim Boundary

This is opt-in fastest-candidate performance work for experimental `COLLECT_K_BOUNDED`. It does not authorize public speedup wording, stable `COLLECT_K_BOUNDED` promotion, whole-application speedup claims, release tags, or release action.
