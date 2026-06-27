# V4 Goal4657 Final Release Or Reframe Authorization

Date: 2026-06-25

Status: `goal4657_pending_external_review`

## Final Decision Requested

Current evidence supports this verdict:

```text
bounded_operator_v4_release_only
```

Current evidence does not support:

```text
formal_high_performance_v4_release_authorized
```

## Why

Goal4639 proves a bounded operator surface:

- `8/8` measured operator surfaces passed;
- `4/4` strong operator families passed;
- most operator rows are `1.2x-1.7x` against stated partner/CPU baselines;
- two very large rows are scale-dependent algorithmic-complexity wins, not
  whole-application proof.

Goal4654/Goal4655 blocks formal app-level high-performance V4:

| App | V4/V2.14 | V4/V3.0.2 | Current reading |
| --- | ---: | ---: | --- |
| RTDBSCAN | `1.070x` | `1.084x` | Modest gain, below formal high-performance bar. |
| RayDB-style | `0.994x` | `1.000x` | Parity, not a V4 speed win. |
| Triangle counting | `15.548x` | `1.117x` | Historical route evolution plus modest V4 increment. |
| LibRTS spatial index | `0.999x` | `1.001x` | Parity, not a V4 speed win. |

Goal4656 corrected public docs and machine boundaries so current V4 does not
claim final app-level high-performance release status.

## Release/Reframe Options

| Option | Authorized? | Reason |
| --- | --- | --- |
| `formal_high_performance_v4_release_authorized` | No | App-level evidence does not support it. |
| `bounded_operator_v4_release_only` | Yes | Operator catalog and public docs are bounded and tested. |
| `partner_promotion_continuation_required` | Yes, as follow-up | Partner support is useful but not sufficient for V4 speed claims. |
| `no_go_reframe_required` | No | V4 still has useful bounded operator value; the correct reframe is bounded operator V4 plus future app-level engineering. |

## Current Machine Truth

```text
formal_release_authorized: false
release_authorized: false
bounded_operator_surface_available: true
app_level_high_performance_authorized: false
goal4655_decision_label: bounded_operator_v4_only__app_level_high_performance_not_supported
```

## Evidence Packet

- `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.md`
- `future/v4/v4_goal4654_full_app_level_v2_14_v3_v4_pod_benchmark_2026-06-25.md`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/summary.json`
- `future/v4/v4_goal4655_full_app_level_benchmark_analysis_2026-06-25.md`
- `future/v4/v4_goal4656_public_docs_machine_boundary_correction_2026-06-25.md`
- `future/v4/reviews/antigravity_v4_goal4656_public_docs_machine_boundary_review_2026-06-25.md`

## Verification

Goal4656 verification:

```text
59 tests OK
```

Current public/machine wording scan found no old release-authorized wording in
the current public/machine paths. Historical review artifacts retain their
original wording and are not current user-facing truth.

## Final Authorization Text

If reviewers accept this packet, the allowed current V4 statement is:

```text
RTDL V4 currently exposes a bounded operator surface with 8 measured generic
RT-core operators. The current app-level V2.14/V3.0.2/V4 evidence does not
support formal app-level high-performance V4 release wording.
```

## Non-Authorization

This packet does not authorize formal app-level high-performance V4 release
wording, broad speedup wording, whole-application speedup wording,
all-benchmark speedup wording, public true-zero-copy wording, Tier-3 callback
support, raw OptiX callback support, CuPy blanket performance claims, C ABI,
embedding, non-Python host binding, app-specific native kernels, or a release
tag.

## Next Engineering Track

The next track must be app-level performance engineering, not release wording:

1. select an app-level blocker where a generic V4 operator route can plausibly
   move the measured row;
2. implement the route as reusable generic operator composition, not an
   app-identity kernel;
3. rerun V2.14/V3.0.2/V4 same-hardware app-level comparison with parity;
4. reopen formal high-performance authorization only if the new evidence passes.
