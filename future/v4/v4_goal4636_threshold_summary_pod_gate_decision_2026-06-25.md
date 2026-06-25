# V4 Goal4636 Threshold-Summary POD Gate Decision

Date: 2026-06-25

Status: `goal4636_threshold_summary_pod_gate_failed_no_promotion_not_release`

Decision: `reject_threshold_summary_promotion_keep_hausdorff_partial`

## Evidence

POD evidence:

- `future/v4/evidence/v4_goal4636_threshold_summary_pod_gate_2026-06-25/summary.json`
- `future/v4/evidence/v4_goal4636_threshold_summary_pod_gate_2026-06-25/README.md`

Review record:

- `future/v4/reviews/goal4636_threshold_summary_target_protocol_review_record_2026-06-25.md`

Machine-readable decision:

- `src/rtdsl/v4_goal4636_threshold_summary_decision.py`

## Gate Result

The serious POD gate ran at the predeclared shape:

- copies: `262144`;
- points per side: `1048576`;
- threshold: `0.4`;
- repeat/warmup: `5` / `1`;
- RT hardware: required;
- variants: Embree, legacy OptiX, productized prepared runner.

Failed checks:

- `runner_regressed_vs_legacy_phase_total`

Key comparisons:

| Comparison | Metric | Result | Floor | Status |
|---|---:|---:|---:|---|
| runner vs Embree | phase-total | `1.2759701868849942x` | `1.20x` | pass |
| runner vs Embree | wrapper-wall | `1.7376484711304498x` | `1.20x` | pass |
| runner vs legacy OptiX | phase-total | `0.9693326333237459x` | `0.98x` | fail |
| runner vs legacy OptiX | wrapper-wall | `0.9898664196438816x` | `0.98x` | pass |

Residency/runner evidence:

- runner Step-3 audit ready: `true`;
- both directed legs runtime-executed: `true`;
- both directed legs runtime trunk end-to-end: `true`;
- threshold rows materialized on host: `false`;
- internal device residency between RTDL phases: `true`.

## Interpretation

This is useful engineering evidence but not a measured V4 promotion.

The productized runner materially beats the same-contract Embree control, and
it proves the runtime/residency path is executing. However, the predeclared gate
also required no regression against the legacy app-front-door OptiX route. The
runner missed the phase-total floor (`0.969x < 0.98x`), so the gate fails.

Because the gate failed:

- `fixed_radius_threshold_summary_2d` is not promoted;
- `hausdorff_xhd` remains `partial_measured_operator_coverage`;
- the V4 measured surface count remains unchanged;
- the next Goal4636 action must select another generic target or write a new
  protocol that explicitly explains this legacy phase-total regression before
  any rerun.

## Goal-Level Decision Audit

Decision: reject threshold-summary promotion from this POD gate.

1. Was this decision stupid?
   - No. It follows the predeclared gate instead of rationalizing a near-miss
     as success.
2. If it were stupid, what action made it stupid?
   - It would be stupid to promote because the runner beat Embree while hiding
     the legacy phase-total failure. This decision does the opposite.
3. Is there another path that avoids being stuck on this thought?
   - Yes. Continue Goal4636 with another generic target, or return to threshold
     summary only under a new predeclared protocol that explains and fixes the
     legacy phase-total regression.
4. Can work start on a different path that truly solves the problem?
   - Yes. The immediate next path is to select a different generic operator
     coverage target, preferably one that is closer to the V4 device-array
     front-door scope and not dependent on CuPy unless Goal4637 is explicitly
     entered.

## Non-Authorization

This decision does not authorize:

- V4 release;
- V4 release candidate;
- broad V4 speedup;
- whole-Hausdorff speedup;
- all-benchmark speedup;
- measured catalog promotion;
- CuPy performance;
- Tier-3 support;
- public true-zero-copy;
- C ABI / embedding / non-Python host claims;
- Hausdorff-native or other app-specific kernels.
