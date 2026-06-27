# V4 Goal4655 Full App-Level Benchmark Analysis

Date: 2026-06-25
Status: analysis complete, not release authorization

Source benchmark:

```text
future/v4/v4_goal4654_full_app_level_v2_14_v3_v4_pod_benchmark_2026-06-25.md
future/v4/evidence/v4_goal4654_serious_20260625_2/summary.json
```

Machine-readable analysis:

```text
future/v4/evidence/v4_goal4655_full_app_level_benchmark_analysis_2026-06-25.json
```

## Decision

```text
decision_label: bounded_operator_v4_only__app_level_high_performance_not_supported
formal_high_performance_v4_supported: false
public_speedup_claim_authorized: false
whole_app_high_performance_claim_authorized: false
```

V4 remains a bounded operator release plus partner/front-door unification at
this point. The Goal4654 app-level run does not support a formal broad
high-performance V4 claim.

## App Classification

| App | V4/V2.14 hot | V4/V3.0.2 hot | Class | Interpretation |
| --- | ---: | ---: | --- | --- |
| `rt_dbscan` | 1.070x | 1.084x | `modest_runtime_gain_below_formal_bar` | Real but below the frozen 1.20x V4/V2.14 bar. |
| `raydb_style` | 0.994x | 1.000x | `parity_not_v4_speed_win` | App-level route is essentially parity. |
| `triangle_counting` | 15.548x | 1.117x | `historical_route_evolution_plus_modest_v4_increment` | Large V4/V2.14 delta mostly already exists by V3.0.2; V4 adds a modest increment. |
| `librts_spatial_index` | 0.999x | 1.001x | `parity_not_v4_speed_win` | App-level route is essentially parity. |

## Blocking Reasons

- `old_version_optix_uses_v4_compatibility_native_library`
- `most_full_app_rows_do_not_pass_frozen_speed_bar`
- `insufficient_independent_true_v4_app_wins`

## What This Means

This result is useful and honest:

- The app-level benchmark now exists and is not toy-scale.
- It prevents overstating operator-level wins as whole-app wins.
- It shows V4 does have a real product surface, but the current four full app
  rows do not justify "formal high-performance V4" wording.

The right public framing remains:

```text
V4.0 is a bounded generic operator release with measured operator-level wins and
certified partner/front-door improvements. Full app-level high-performance
claims remain unsupported by the current Goal4654/4655 evidence.
```

## Goal-Level Decision Audit

1. Was I being stupid?
   - No for this decision. The analysis follows the frozen Goal4653 bars and
     refuses to convert parity or historical route evolution into a new V4 win.
2. If yes, what action made it stupid?
   - The known stupid action would be to headline `15.548x` triangle and ignore
     that V4/V3.0.2 is only `1.117x` while three other apps are parity/modest.
3. Is there another path that avoids getting stuck on a bad premise?
   - Yes: classify every row by claim class and preserve the native-provenance
     blocker.
4. Can I now try the different path that actually solves the problem?
   - Yes. Goal4656 should rewrite user docs around bounded operator V4 truth,
     not broad app-level speed.

## Non-Authorization

Goal4655 does not authorize V4 final release wording, public whole-app speedup
claims, broad V4 high-performance claims, CuPy blanket claims, arbitrary Numba
callback claims, C ABI, embedding, or true-zero-copy claims.
