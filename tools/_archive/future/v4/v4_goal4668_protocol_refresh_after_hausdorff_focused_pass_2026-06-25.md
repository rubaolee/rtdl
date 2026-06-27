# V4 Goal4668 - Protocol Refresh After Hausdorff Focused Pass

Date: 2026-06-25

Status: protocol refreshed; full app rerun Go; no release authorization

Decision label:
`protocol_refreshed__full_app_rerun_go_after_hausdorff_focused_pass__no_release`

## Bottom Line

Goal4668 updates the app-level benchmark protocol after Goal4667. Hausdorff XHD
is no longer a partial control row: it is now a full app-level candidate row
because the focused V4 route clears the frozen bars at both 65,536 and 262,144
points/side and preserves the 1M correctness-boundary probe.

This authorizes the next engineering step: a serious full app-level V2.14 /
V3.0.2 / V4 rerun under the refreshed protocol.

It does not authorize V4 release or public high-performance wording.

## Evidence

Machine evidence:

`future/v4/evidence/v4_goal4668_protocol_refresh_after_goal4667_2026-06-25.json`

Source focused evidence:

`future/v4/evidence/v4_goal4667_hausdorff_multiblock_argmax_20260625/summary.json`

Protocol code:

`src/rtdsl/v4_app_benchmark_protocol.py`

## Protocol Change

Before Goal4668:

- full app candidate rows: `4`;
- partial controls: `4`;
- Hausdorff XHD: partial control / correctness-boundary row.

After Goal4668:

- full app candidate rows: `5`;
- partial controls: `3`;
- Hausdorff XHD: full app candidate row with a custom frozen bar:
  - correctness required;
  - V4/V2.14 primary metric speedup `>=1.20x`;
  - V4/V3 hot speedup `>=1.20x`;
  - prepare no-regression floor `>=0.80x`;
  - 1M coordinate-normalized correctness-boundary probe required;
  - partner migration does not count as a win;
  - app-specific native kernel remains forbidden.

The new full candidate set is:

- RTDBSCAN;
- RayDB-style;
- Triangle counting;
- LibRTS spatial index;
- Hausdorff XHD.

Partial/control rows remain:

- robot collision;
- contact manifold;
- RTNN.

Visible blockers/deferred rows remain:

- spatial rayjoin;
- Barnes-Hut.

## Validation

Command:

```text
py -m unittest tests.v4_goal4653_app_level_protocol_test tests.v4_goal4667_hausdorff_adaptive_argmax_test tests.v4_goal4652_app_route_binding_test tests.v4_frontdoor_test
```

Result:

`25 tests OK`

## Claim Boundary

Authorized:

- Goal4669 full app-level benchmark rerun request under the refreshed protocol.

Not authorized:

- V4 release;
- formal high-performance V4;
- broad V4 speedup wording;
- whole-app speedup wording;
- public true-zero-copy wording;
- app-specific native kernels;
- C ABI / embedding / non-Python host claims.

## Next Step

Goal4669 should run the full app-level benchmark under the refreshed protocol.
The output must classify every row as true V4 win, partner migration, algorithmic
complexity/control, parity, regression, or blocked. Release remains unauthorized
until that full scorecard and external/debt review are complete.
