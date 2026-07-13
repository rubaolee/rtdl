# Goal5371 - X-HD Inline / Global-Bound lb Probe

Date: 2026-07-09

Status: `implemented_review_pending`

## Verdict Label

```text
inline_and_global_bound_lb_probes_ready__author_denominator_still_unmatched
```

Exit label:

```text
inline_payload_and_existing_global_bound_do_not_explain_author_offloading_size
```

## Purpose

Goal5368 showed that no-inline raw kind2 rows are far larger than the author
`OffloadingSize`.  Goal5367 showed that RTDL's author-radius materialized
inline/offload rows are smaller than the author denominator.

Goal5371 tests two narrower explanations:

```text
1. Is the 21,006,960 RTDL count a materialization / host sort artifact?
2. Does RTDL's existing generic global-bound early break approximate the
   author's cmax2 abort behavior?
```

## Implementation

Generic probe changes:

```text
run_xhd_cell_mbr_frontier_kind_count_probe.py
  --inline-nearest
  --collect-inline-stats
  --global-bound-early-break
```

Generic wrapper change:

```text
cell_mbr_nearest_frontier_native_3d_optix_columns
```

now tolerates missing nearest columns only when:

```text
allow_overflow_telemetry = true
overflow_telemetry_only = true
```

This is a generic telemetry-only path.  Normal inline-nearest paths still
require nearest columns and fail closed if they are absent.

## POD Runs

POD:

```text
host = 213.173.108.24
port = 13502
GPU = NVIDIA RTX 4000 Ada Generation
remote workspace = /tmp/rtdl_goal5364
```

Input:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
preprocessing = translate_each_input_to_min_bound
grid_shape = 96,60,72
radius = 79.2156982421875
max_inline_points = 256
frontier_row_capacity = 0
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5371_dragon_asian_lb256_author_radius_inline_kind_count_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5371_dragon_asian_lb256_author_radius_inline_global_bound_kind_count_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5371_inline_global_bound_lb_probe.json
```

## Key Numbers

```text
author OffloadingSize                         = 27,133,990
RTDL author-radius materialized rows          = 21,006,960
RTDL author-radius inline count-only kind2    = 21,006,960
RTDL inline + global-bound count-only kind2   = 21,006,960
RTDL no-inline raw kind2 from Goal5368        = 304,981,889
```

Ratios:

```text
inline / author        = 0.7741935483870968
inline+bound / author  = 0.7741935483870968
no-inline / author     = 11.239846738352892
```

Global-bound:

```text
global_bound_early_break_count = 0
global_bound_distance = 0.0
```

## Interpretation

The materialization / host-sort hypothesis is rejected:

```text
inline count-only kind2 = prior materialized author-radius rows = 21,006,960
```

The existing RTDL global-bound hypothesis is rejected for this probe:

```text
global-bound changes neither the kind2 row count nor early-break count.
```

The next required alignment is author shader status-machine semantics, not
another scalar radius or existing global-bound toggle:

```text
dynamic cmin2 updates
cmax2 abort status
miss/offload queue updates
load-balance post-processing over offloaded cells
```

## Validation

Commands:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 upload ...
python3 run_xhd_cell_mbr_frontier_kind_count_probe.py ... --inline-nearest
python3 run_xhd_cell_mbr_frontier_kind_count_probe.py ... --inline-nearest --global-bound-early-break
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5371_inline_global_bound_lb_probe.py
py -m py_compile src\rtdsl\partner_continuations.py Paper-reproduction-apps\x-hd-paper\scripts\run_xhd_cell_mbr_frontier_kind_count_probe.py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5371_inline_global_bound_lb_probe.py
py -m unittest tests.goal5371_inline_global_bound_lb_probe_test tests.goal5369_lb_queue_state_requirements_test tests.goal5370_author_like_queue_state_reference_test
```

Result:

```text
Ran 8 tests OK
```

The local Python runtime printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Claim Boundary

Allowed:

```text
Goal5371 adds generic inline/global-bound modes to the count-only probe and
shows that neither inline payload counting nor existing generic global-bound
early break explains author OffloadingSize.
```

Not authorized:

```text
explicit -lb support
row-count parity
same-denominator memory parity
Figure 7 reproduction
Figure 11 reproduction
author RT-core algorithm parity
RTDL/author performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```

## Next Work

The next implementation should model or instrument the author shader status
machine rather than using the existing global-bound flag:

```text
1. Encode author-like per-ray status:
   kInit / kOffloading / kAborted
2. Carry dynamic cmin2 inside traversal.
3. Apply author cmax2 max-distance abort before offload append.
4. Preserve miss/offload queue update semantics.
5. Compare raw offload rows against author OffloadingSize.
```

If that is too invasive for RTDL core, instrument the author binary to expose
the raw offload rows and per-source status so RTDL can compare against the
stronger oracle.
