# Goal3388 - Boundary-Event Tolerance Signal Slice Sweep

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3386 proved a narrow constructive signal on one 512-chain CDB slice, but
Claude's Goal3387 review correctly flagged two next gates:

1. Test larger CDB slices.
2. Replace the hard `zero_boundary_candidate_count == 2` rule with an explicit
   deterministic tolerance policy.

Goal3388 runs that next bounded gate over three live OptiX slices from
`br_county.cdb`: 512, 1024, and 2048 chains starting at chain 256.

## Route

The route is still a Python/RTDL/CuPy continuation over generic columns:

1. Generate candidate rows from live OptiX candidate device columns.
2. Generate boundary-event rows from live OptiX first-boundary-event device
   columns.
3. Select points using only candidate counts and strict-zero boundary-event
   counts.
4. For selected points, keep candidate pairs that have a boundary event with
   `abs(crossing_t) <= 1e-5`.
5. Pass all unselected candidate rows through unchanged.
6. Compare the output to a live exact OptiX oracle only for evaluation.

The selected-point signal is:

```text
candidate_count > strict_zero_boundary_candidate_count
and strict_zero_boundary_candidate_count <= 2
```

The filter is:

```text
selected_candidate_pair_has_boundary_crossing_t_within_tolerance
```

with `crossing_tolerance = 1e-5`.

## Evidence

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`06945a9e05c0b26324376334d78dd25d94127f81`

Artifact:
`docs/reports/goal3388_boundary_event_tolerance_signal_slice_sweep_2026-06-04.json`

## Results

| Chains | Candidate rows | Boundary-event rows | Exact rows | Extras before filter | Selected points | False-positive selected points | Missed true-extra points | Dropped rows | Filtered rows | Match |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | --- |
| 512 | 1429 | 4836 | 1417 | 12 | 10 | 633, 634, 635 | none | 12 | 1417 | true |
| 1024 | 2844 | 16173 | 2827 | 17 | 15 | 633, 634, 635 | none | 17 | 2827 | true |
| 2048 | 5672 | 34133 | 5619 | 53 | 40 | 633, 634, 635 | none | 53 | 5619 | true |

All three rows match the live exact OptiX oracle with zero missing rows and zero
extra rows after filtering.

## Interpretation

Goal3388 is a stronger scale signal than Goal3386, but it is also more honest
about what the signal does:

- Goal3386 selected exactly the true-extra points on the 512-chain slice.
- Goal3388 intentionally allows a small, stable over-selection set
  (`633, 634, 635`) because those points contain legitimate near-zero boundary
  events that strict zero alone would misclassify.
- The explicit `1e-5` tolerance preserves those near-boundary exact rows while
  still dropping every candidate extra on all three slices.

This is useful because the decision is no longer a fixed point-id list or a
slice-specific hard equality rule. It is a generic candidate/boundary-event
policy over device columns, with the exact oracle kept outside the signal.

## Boundary

This does not authorize a native default route. It also does not authorize release,
public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, RT-core speedup,
or true-zero-copy claims.

The next gates are:

- additional RayJoin dataset families, not only `br_county`;
- larger/full CDB slices;
- a documented deterministic tolerance policy for `crossing_t`;
- stress tests for boundary-event overflow behavior;
- external review before any route-promotion proposal.
