# V4 Goal4664 Next Performance Target Selection

Date: 2026-06-25

Status: `goal4664_select_hausdorff_xhd_for_focused_formal_candidate_protocol`

## Purpose

After Goal4663, the project needs real performance engineering, not another
all-app rerun and not another parity wrapper. Goal4664 selects the next
app-level target and freezes the conditions for a focused Goal4665 run.

Machine evidence:

```text
future/v4/evidence/v4_goal4664_next_performance_target_selection_2026-06-25.json
```

## Selection

Selected app:

```text
hausdorff_xhd
```

Decision label:

```text
select_hausdorff_for_goal4665_focused_formal_candidate_run
```

Why this target:

- It has an official V4 route through generic operator composition:
  point-group nearest-witness plus Torch `global_argmax_u32_f64`.
- It avoids an app-specific Hausdorff native kernel.
- Existing exploratory evidence shows correctness-passing 262,144
  points/side hot-path speedup over V3.0.2 CuPy:

```text
V4/V3.0.2 hot = 1.260x
```

- It also has a meaningful correctness boundary at 1,048,576 points/side:
  unnormalized rows fail exactness; coordinate-normalized V4 passes exactness.

Why not RTNN:

- RTNN V4 candidate exists and validates, but serious rows are parity/slower:
  `262144` is ~parity and `1048576` is below `1.0x` vs both V2.14 and V3.0.2.
- Continuing RTNN as a performance target would be fake progress.

Why not full all-app:

- Current changed rows cannot overturn Goal4655.
- Running the whole suite now would spend POD time to reconfirm known no-go
  evidence.

## Frozen Goal4665 Protocol

Goal4665 may run a focused Hausdorff formal-candidate check under this frozen
protocol.

Route:

```text
official V4 point-group nearest-witness + Torch global_argmax_u32_f64
```

Forbidden shortcut:

```text
no Hausdorff-specific native kernel
```

Primary correctness-passing performance scales:

```text
65,536 points/side
262,144 points/side
```

Primary metric:

```text
hot_device_sec for prepared/reuse route
```

Secondary metrics:

```text
scene_prepare_sec
materialize_sec
wall/cold when available
```

Minimum bars:

```text
V4/V3.0.2 hot speedup >= 1.20x
V4/V2.14 primary metric speedup >= 1.20x
prepare no-regression floor where comparable >= 0.80x
correctness parity required
```

Large-scale correctness probe:

```text
1,048,576 points/side coordinate-normalized V4 correctness
```

This large-scale row is a correctness-boundary probe, not a speed claim.

## Non-Authorization

This target selection does not authorize release, broad V4 speedup wording,
whole-application speedup wording, full all-app rerun, unrestricted exact
Hausdorff wording, public true-zero-copy claims, arbitrary callbacks, C ABI,
embedding, non-Python hosts, or app-specific native kernels.
