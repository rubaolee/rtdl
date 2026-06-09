# Goal4096 Device Partition Key Decode

Date: 2026-06-09

## Verdict

`accept`

Goal4096 removes unnecessary host reconstruction of partition keys from the
device partition-summary pair-status path. The device kernel now decodes
partition coordinates directly from the sorted `unique_cells` column.

This is a generic runtime improvement. It is not DBSCAN-specific engine logic.

## What Changed

Before Goal4096, device pair enumeration still did this:

- copy `unique_cells` back to the host;
- rebuild `(x, y, z)` partition key tuples in Python;
- copy key arrays back to the device for the pair-status kernel.

After Goal4096:

- host key reconstruction remains only for the explicit `host` enumeration mode;
- device modes pass `partition_count` and `unique_cells`;
- the RawKernel decodes `base_x`, `base_y`, and `base_z` directly from
  `unique_cells[left]`;
- output occupied-key columns are computed from `unique_cells` on device.

## Pod Evidence

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `0619c6e30cc94f04e9f6b17b2a7bafbf5db33783`
- Runner: `scripts/goal4095_partition_convergence_phase_breakdown.py`
- Output:
  - `docs/reports/goal4096_device_partition_key_decode_phase_breakdown_pod.json`
  - `docs/reports/goal4096_device_partition_key_decode_phase_breakdown_pod.stdout.txt`

## Before/After

Comparison is Goal4095 baseline versus Goal4096 rerun, both at 65,536 points
using `device_count_then_emit_non_skip`.

| Profile | Goal4095 build median | Goal4096 build median | Build speedup | Other-build speedup | Count-probe speedup | Emit speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 0.091420 | 0.075677 | 1.208x | 1.290x | 1.205x | 1.084x |
| `road3d` | 0.082552 | 0.066259 | 1.246x | 1.298x | 1.262x | 1.129x |
| `ngsim_dense` | 0.201295 | 0.136108 | 1.479x | 2.026x | 1.300x | 1.207x |

The optimization materially reduces the producer bottleneck, especially for
`ngsim_dense`, where the uninstrumented build phase is cut about in half.

## Remaining Bottleneck

Goal4096 improves the current preview, but it does not erase the architectural
limit identified by Goal4095:

- the pair-status path still performs a count probe and an emit pass;
- pair rows are still materialized before continuation;
- signature replay still has substantial bookkeeping outside ambiguous union.

The next high-value step remains a generic fused/native fixed-radius
grouped-union producer that can consume partition-pair status directly without
round-tripping through a full row table.

## Boundary

This report is internal runtime evidence. It does not promote
`partition_convergence_hybrid`, authorize release, public speedup, broad RT-core,
whole-app, paper-reproduction, hidden-dispatch, automatic partner selection,
app-specific engine logic, native ABI addition, or true-zero-copy claims.
