# V4 Goal4702 Specialized Tier-3 Reliability Matrix Protocol

Date: 2026-06-25

Status: `complete_pending_3ai_review_debt`

## Goal

Freeze the reliability matrix for the constrained specialized Tier-3 support
candidate before spending POD time on repeated compile/link/launch attempts.
This follows Goal4701's support-candidate packet and authorizes only Goal4703
execution.

## Result

Goal4702 freezes a 20-attempt reliability matrix:

- 4 callback variants:
  - `custom_scalar_reduce_weighted_sum`
  - `custom_score_affine`
  - `custom_threshold_flag`
  - `custom_minmax_score`
- 5 attempts per variant.
- 3 correctness datasets:
  - `dense_hits`
  - `sparse_hits`
  - `no_hit_empty_reduction`
- compile/link/launch success floor: `>=0.95`.
- correctness requirement: `100% exact or tolerance-bounded parity for every variant x dataset row`.
- cache requirement: same callback PTX/toolchain/symbol reuses the same deterministic cache key; changed PTX or toolchain fingerprint changes the key.
- failure requirement: every failed attempt must carry a Goal4698 stage-specific error code.

## Evidence

- Machine evidence JSON:
  `future/v4/evidence/v4_goal4702_specialized_tier3_reliability_protocol_2026-06-25.json`
- Machine evidence markdown:
  `future/v4/evidence/v4_goal4702_specialized_tier3_reliability_protocol_2026-06-25.md`
- Source:
  `src/rtdsl/v4_goal4702_specialized_tier3_reliability_protocol.py`
- Script:
  `scripts/v4_goal4702_specialized_tier3_reliability_protocol.py`
- Tests:
  `tests/v4_goal4702_specialized_tier3_reliability_protocol_test.py`

## Validation

Commands run:

```text
py scripts/v4_goal4702_specialized_tier3_reliability_protocol.py --json-out future/v4/evidence/v4_goal4702_specialized_tier3_reliability_protocol_2026-06-25.json --md-out future/v4/evidence/v4_goal4702_specialized_tier3_reliability_protocol_2026-06-25.md
py -m py_compile src/rtdsl/v4_goal4702_specialized_tier3_reliability_protocol.py scripts/v4_goal4702_specialized_tier3_reliability_protocol.py src/rtdsl/v4.py
py -m unittest tests.v4_goal4702_specialized_tier3_reliability_protocol_test tests.v4_goal4701_specialized_tier3_support_candidate_test tests.v4_goal4700_specialized_tier3_app_route_result_test
```

Observed validation:

- protocol evidence generation: passed.
- `py_compile`: passed.
- unit tests: `6 tests OK`.

## Claim Boundary

Goal4702 authorizes only Goal4703 reliability execution. It does not authorize:

- public Tier-3 support;
- arbitrary callback support;
- action or side-effect callback support;
- raw OptiX callback support;
- release wording;
- public performance claims;
- app-level high-performance V4 claims.

## Goal-Level Decision Audit

1. Was I being stupid?

No for this goal. The goal was a protocol freeze immediately before a POD reliability matrix, not a substitute for engineering. It directly defines the next falsifiable experiment.

2. If yes, what actions made the decision stupid?

Not applicable. The risk would have been to skip the protocol and run an unfrozen POD matrix that could be explained after the fact. This goal prevents that.

3. Is there another path that avoids being stupid on one idea?

Yes: if Goal4703 fails the matrix, stop promoting Tier-3 support and classify the track as spike-only until the failing stage is fixed. Do not reword failure as support.

4. Can I start a different path that actually solves the problem?

Yes. The concrete path is Goal4703: run the frozen reliability matrix on POD and read the pass/fail evidence.

## Next

Proceed to Goal4703: implement and run the specialized Tier-3 reliability matrix on POD under this frozen protocol.
