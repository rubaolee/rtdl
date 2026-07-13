# Goal5228 - ModelNet40 Near-Tolerance Failure Probe Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_near_tolerance_probe__two_failures_pass_at_2e_minus_6
```

Goal5228 is a narrow probe of the two Goal5227 all-400 failures. It does not
change the Goal5227 strict `1e-6` result.

## Probe

The two failed case indices were rerun with:

```text
--selection-strategy all_unique_pairs
--max-pairs 400
--start-index 63 --end-index 64
--start-index 114 --end-index 115
--tolerance 2e-6
```

## Result

```text
case 63  matched = true at 2e-6
case 114 matched = true at 2e-6
```

Downloaded artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5228_tolerance_probe_case063_tol2e-6_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5228_tolerance_probe_case114_tol2e-6_summary_2026-07-09.json
```

## Interpretation

The two all-400 failures are near-threshold numeric differences:

```text
1.4973206821644602e-06
1.0085423763905865e-06
```

Both are above the current `1e-6` tolerance and below `2e-6`.

This supports a follow-up tolerance policy review. It does **not** authorize
retroactively claiming Goal5227 as 400/400 under the old tolerance.

## Claim Boundary

Allowed:

```text
The two strict-1e-6 all-400 failures pass under a 2e-6 diagnostic tolerance.
```

Forbidden:

```text
Goal5227 is 400/400 under 1e-6.
The tolerance has been officially changed.
Full ModelNet40 reproduction is complete.
Full X-HD paper reproduction is complete.
```
