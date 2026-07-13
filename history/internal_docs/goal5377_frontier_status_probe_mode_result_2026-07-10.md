# Goal5377 Frontier Status Probe Mode Result

Date: 2026-07-10

## Verdict

`heavy_before_inline_prune_probe_no_go__author_lb_row_parity_still_missing`

Goal5377 added and tested a generic RTDL frontier status probe mode, then used it
against the Goal5374 author `-lb` OffloadingSize oracle. The implementation is
useful as a generic diagnostic surface, but the specific hypothesis is rejected:
moving heavy-cell/offload classification before inline-current-best pruning does
not match the author's `-lb` denominator.

## What Was Implemented

System changes:

- Added native OptiX ABI `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6`.
- Added app-neutral launch parameter `frontier_status_probe_mode`.
- Added experimental mode `heavy-before-inline-prune`.
- Forwarded the mode through:
  - `src/rtdsl/optix_runtime.py`;
  - `src/rtdsl/partner_continuations.py`;
  - `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py`.
- Added focused regression coverage in
  `tests/goal5377_frontier_status_probe_mode_test.py`.

The native mode is generic. It is not named after X-HD, `lb`, or the paper. It
only changes one generic classification order:

```text
default:
  inline-current-best prune can suppress the cell before heavy/offload

heavy-before-inline-prune:
  heavy/offload classification runs before that inline-current-best prune
```

## Validation

Local:

```text
py -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/partner_continuations.py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py

py -m unittest \
  tests.goal5377_frontier_status_probe_mode_test \
  tests.goal5376_status_machine_candidate_telemetry_test \
  tests.goal5211_global_bound_early_break_contract_test \
  tests.goal5172_native_inline_nearest_frontier_test

Ran 13 tests OK
```

POD:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
# POD_OK, NVIDIA RTX 4000 Ada Generation, driver 550.127.05

make build-optix
# completed successfully

python3 -m unittest tests.goal5377_frontier_status_probe_mode_test
# Ran 4 tests OK
```

POD evidence files:

- `Paper-reproduction-apps/x-hd-paper/results/xhd_goal5377_default_status_probe_pod.json`
- `Paper-reproduction-apps/x-hd-paper/results/xhd_goal5377_heavy_before_inline_prune_probe_pod.json`
- `Paper-reproduction-apps/x-hd-paper/results/xhd_goal5377_frontier_status_probe_mode_comparison.json`

## Same-Input Diagnostic

Input and author oracle:

```text
input1: /tmp/xhd_goal5234/data/dragon.ply
input2: /tmp/xhd_goal5234/data/asian_dragon.ply
points: 437,645 -> 3,609,600
grid_shape: 96 x 60 x 72
radius: 79.2156982421875
max_inline_points: 256
author raw OffloadingSize rows: 27,133,990
```

Observed RTDL counts:

| Route | Native symbol | RTDL kind2 rows | Ratio vs author | Parity |
|---|---|---:|---:|---|
| default inline-current-best prune | `v4` | 21,006,960 | 0.7741935484 | no |
| heavy-before-inline-prune probe | `v6` | 304,981,889 | 11.2398467384 | no |

Interpretation:

- The default RTDL surface under-counts the author oracle by 6,127,030 rows.
- The new `heavy-before-inline-prune` probe over-counts by 277,847,899 rows.
- Therefore the author `-lb` denominator is not explained by a simple
  "offload before prune" branch-order change.
- The new mode lands on the already-known no-inline/raw over-counting surface,
  not on the author status-machine surface.

## What This Does Not Prove

This goal does not prove:

- explicit author-compatible `-lb` support;
- row-count parity with author OffloadingSize;
- same-denominator memory parity;
- author RT-core algorithm parity;
- full X-HD paper reproduction;
- performance improvement.

## Why This Still Matters

The result is negative but useful. It narrows the remaining gap. The next
unknown is not merely whether heavy cells are classified before pruning; it is
the richer author status machine:

- author `cmin2` / current-best restoration by `in_q_idx`;
- `cmax2` MBR abort status;
- miss/offload queue update semantics;
- `loadBalanceProcessing` sort/reduce feedback into later state.

The new v6 probe mode should remain experimental and non-default. It is a
diagnostic switch, not a product route.

## Recommended Next Work

Do not continue tuning `heavy-before-inline-prune` as if it were close to
author `-lb`. It is not.

The next viable work is a stronger state-machine model or a decision to keep
`-lb` fail-closed:

1. Build an app-neutral RTDL status-machine replay/probe that can carry
   per-query current-best state by query row across queue updates.
2. Add explicit counters for cmax2/MBR abort analogs and miss/offload queue
   transitions.
3. Compare those counters to the Goal5374 oracle before claiming any `-lb`
   support.
4. If the status-machine model would require app-specific author behavior in
   RTDL core, keep `-lb` unsupported and document it as a paper-specific
   algorithmic gap.
