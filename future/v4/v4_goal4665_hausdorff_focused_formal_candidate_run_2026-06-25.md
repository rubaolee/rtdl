# V4 Goal4665 Hausdorff Focused Formal-Candidate Run

Date: 2026-06-25

Status: `goal4665_hausdorff_focused_run_complete_failed_formal_bar`

Decision label:

```text
hausdorff_formal_candidate_fails_focused_bar
```

## Purpose

Goal4665 ran the Goal4664 frozen Hausdorff protocol on the same RT hardware.
This was a focused test, not a full all-app rerun.

Machine summary:

```text
future/v4/evidence/v4_goal4665_hausdorff_focused_20260625/summary.json
```

Raw rows:

```text
future/v4/evidence/v4_goal4665_hausdorff_focused_20260625/
```

## Frozen Bars

The bars were frozen in Goal4664:

```text
V4/V3.0.2 hot speedup >= 1.20x
V4/V2.14 primary metric speedup >= 1.20x
prepare no-regression floor where comparable >= 0.80x
correctness parity required
```

The V4 route is the official generic composition:

```text
V4 point-group nearest-witness + Torch global_argmax_u32_f64
```

No Hausdorff-specific native kernel was added.

## Results

| Points/side | Correct | V4/V3.0.2 hot | V4/V2.14 primary | V4/V3.0.2 prepare | Result |
|---:|---|---:|---:|---:|---|
| 65,536 | yes | 1.278x | 28,878.690x | 0.479x | hot passes, prepare fails |
| 262,144 | yes | 0.649x | 147,945.197x | 0.711x | fails formal bar |

Large-scale correctness probe:

```text
1,048,576 points/side, V4 coordinate-normalized span 1,000,000: correctness passed
```

That row remains a correctness-boundary probe, not a speed claim.

## Interpretation

Hausdorff does not currently provide the missing formal high-performance V4
evidence.

The good news:

- the V4 official route exists;
- correctness passes at 65,536 and 262,144 points/side;
- V4 still massively beats the V2.14 Embree primary metric;
- the 1M coordinate-normalized V4 exactness probe passes.

The blocking result:

- the serious 262,144-point row fails the V4/V3.0.2 hot bar;
- V4 prepare is slower than the frozen no-regression floor at both measured
  scales;
- therefore this cannot trigger a full all-app rerun or a high-performance
  release claim.

## Next Engineering Need

The next useful work is not another all-app run. It is one of:

1. reduce V4 Torch route overhead for Hausdorff;
2. certify a V4 CuPy continuation/front door for the same generic route;
3. select another app-level target with a stronger generic V4 lever.

## Non-Authorization

This goal does not authorize V4 release, formal high-performance V4 wording,
broad speedup wording, whole-application speedup wording, unrestricted exact
Hausdorff wording, public true-zero-copy claims, arbitrary callbacks, C ABI,
embedding, non-Python hosts, or app-specific native kernels.
