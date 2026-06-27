# V4 Goal4710 Custom Scored App Protocol

Date: 2026-06-25

Status: `complete_pending_3ai_review_debt`

## Goal

Freeze the focused app-level benchmark protocol for:

`ray_triangle_custom_scored_accumulation`

The protocol exists to test whether V4's constrained specialized scalar
callback fusion produces a real V4-over-V2/V3 app-level win. It blocks POD
timing unless baselines, callbacks, scales, correctness gates, numeric bars, and
kill conditions are fixed first.

## Protocol Summary

Primary callbacks:

- `affine_score`
- `threshold_score`
- `minmax_score`

Control callback:

- `weighted_sum`

Regimes:

- `dense_hits`
- `sparse_hits`
- `no_hit_empty_reduction`

Scales:

- `262144`
- `524288`

Baselines:

- V2.14 strongest available route at `/root/rtdl_v2_14_tag`
- V3.0.2 strongest available route at `/root/rtdl_v3_0_2_tag`
- V4 specialized callback candidate at `/root/rtdl_v4_candidate_pod`
- V4 Tier-2 built-in weighted-sum control row where semantically comparable

## Pass Conditions

- correctness must pass for every callback x regime x scale x implementation row.
- primary custom-callback geomean speedup over strongest V2.14 baseline must be `>=1.50x`.
- primary custom-callback geomean speedup over strongest V3.0.2 baseline must be `>=1.20x`.
- every primary callback must be `>=1.10x` over the strongest V3.0.2 baseline in both dense and sparse regimes.
- `weighted_sum` is a control row only and cannot by itself support the app-level claim.
- all denominators and fallback selections must be recorded before reading V4 timing.

## Kill Conditions

- any correctness failure kills the goal.
- if V2/V3 denominator discovery is missing or only a known-slow fallback is used without proof no stronger route exists, the result is invalid.
- if the win comes only from `weighted_sum` or operator-only rows, the app-level claim is invalid.
- if primary custom-callback geomean over V3.0.2 is `<1.20x`, do not continue toward high-performance wording.
- if any primary callback regresses below `0.95x` versus V3.0.2, stop and diagnose before more POD spend.

## Evidence

- JSON:
  `future/v4/evidence/v4_goal4710_custom_scored_app_protocol_2026-06-25.json`
- Markdown:
  `future/v4/evidence/v4_goal4710_custom_scored_app_protocol_2026-06-25.md`
- Source:
  `src/rtdsl/v4_goal4710_custom_scored_app_protocol.py`
- Script:
  `scripts/v4_goal4710_custom_scored_app_protocol.py`
- Tests:
  `tests/v4_goal4710_custom_scored_app_protocol_test.py`

## Validation

Commands run:

```text
py scripts/v4_goal4710_custom_scored_app_protocol.py --json-out future/v4/evidence/v4_goal4710_custom_scored_app_protocol_2026-06-25.json --md-out future/v4/evidence/v4_goal4710_custom_scored_app_protocol_2026-06-25.md
py -m py_compile src/rtdsl/v4_goal4710_custom_scored_app_protocol.py scripts/v4_goal4710_custom_scored_app_protocol.py src/rtdsl/v4.py
py -m unittest tests.v4_goal4710_custom_scored_app_protocol_test tests.v4_goal4709_formal_hp_app_target_selection_test tests.v4_goal4708_app_value_route_selection_test
```

Observed:

- evidence generation: passed.
- `py_compile`: passed.
- unit tests: `6 tests OK`.

## Claim Boundary

Goal4710 authorizes only Goal4711 focused POD benchmarking under this protocol.
It does not authorize:

- app-level speed claims;
- all-app benchmarking;
- public Tier-3 support;
- raw OptiX callbacks;
- arbitrary callbacks;
- V4 release wording;
- formal high-performance V4 wording.

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal freezes strict bars before POD and prevents reading a weak result
as a high-performance app win.

2. If yes, what actions made the decision stupid?

Not applicable. The main risk would have been treating weighted-sum, an existing
operator control, as primary evidence. The protocol explicitly forbids that.

3. Is there another path that avoids being stupid on one idea?

Yes. If denominator discovery shows V2/V3 already have an equivalent fused route,
Goal4711 must classify the target as not a V4-specific speed win.

4. Can I start a different path that actually solves the problem?

Yes. Goal4711 is the falsifiable focused benchmark: run the protocol and read
the numbers.

## Next

Proceed to Goal4711: ray-triangle custom scored accumulation focused POD
benchmark.
