# V4 Goal4704 Specialized Tier-3 Support Wording Gate

Date: 2026-06-25

Status: `complete_pending_3ai_review_debt`

## Goal

Convert the Goal4696-Goal4703 specialized Tier-3 evidence chain into a bounded
wording gate. The purpose is to prevent a support candidate from being presented
as public Tier-3 support, arbitrary callback support, raw OptiX callback support,
or a performance/release claim.

## Result

Validation status: `passed`

Candidate label:

`specialized_numba_scalar_callback_support_candidate`

Allowed internal wording:

- specialized Tier-3 support candidate
- module-specialized Numba C-ABI scalar callback route
- passed one app-route gate and one 20-attempt reliability matrix
- not public support and not release wording

Prohibited public wording:

- V4 supports arbitrary callbacks
- V4 supports raw OptiX callbacks
- Tier-3 callbacks are public API
- custom callback path is a V4 performance win
- callback support is release-ready
- app-level high-performance V4 is proven by Tier-3

Remaining public-support gates:

- external 3-AI review of Goals4696-4703
- source-level PTX canonicalization or explicit artifact-level cache documentation
- negative user-facing validation for rejected callback shapes
- bounded user docs with examples that compile in a clean environment
- final support authorization separate from V4 release authorization

## Evidence

- JSON:
  `future/v4/evidence/v4_goal4704_specialized_tier3_support_wording_2026-06-25.json`
- Markdown:
  `future/v4/evidence/v4_goal4704_specialized_tier3_support_wording_2026-06-25.md`
- Source:
  `src/rtdsl/v4_goal4704_specialized_tier3_support_wording.py`
- Script:
  `scripts/v4_goal4704_specialized_tier3_support_wording.py`
- Tests:
  `tests/v4_goal4704_specialized_tier3_support_wording_test.py`

## Validation

Commands run:

```text
py scripts/v4_goal4704_specialized_tier3_support_wording.py --json-out future/v4/evidence/v4_goal4704_specialized_tier3_support_wording_2026-06-25.json --md-out future/v4/evidence/v4_goal4704_specialized_tier3_support_wording_2026-06-25.md
py -m unittest tests.v4_goal4704_specialized_tier3_support_wording_test tests.v4_goal4703_specialized_tier3_reliability_result_test tests.v4_goal4702_specialized_tier3_reliability_protocol_test
py -m py_compile src/rtdsl/v4_goal4704_specialized_tier3_support_wording.py scripts/v4_goal4704_specialized_tier3_support_wording.py src/rtdsl/v4.py
```

Observed:

- evidence generation: passed.
- unit tests: `7 tests OK`.
- `py_compile`: passed.

## Front-Door Boundary Update

`claim_boundary_v4()` now exposes:

- `tier3_specialized_callback_candidate_label`
- `tier3_specialized_callback_candidate_status`
- `tier3_specialized_callback_public_support_authorized: false`

The existing public-support and raw-callback claim flags remain false.

## Claim Boundary

Goal4704 does not authorize:

- public Tier-3 support;
- arbitrary callbacks;
- raw OptiX callbacks;
- action/side-effect callbacks;
- V4 release wording;
- app-level speed claims;
- broad V4 performance claims.

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal closes a real risk: Goal4703 is encouraging evidence, but without
a wording gate it could be overstated as public support.

2. If yes, what actions made the decision stupid?

Not applicable. A small validation bug in the first run checked `support candidate`
against a machine label containing `support_candidate`; that was fixed before
completion and did not change the boundary.

3. Is there another path that avoids being stupid on one idea?

Yes. Keep the candidate visible in the machine boundary, but keep all public
support, release, and performance flags false until external review and
remaining hardening gates close.

4. Can I start a different path that actually solves the problem?

Yes. Goal4705 should address the source-level PTX cache-canonicalization issue
revealed during Goal4703 instead of pretending the support candidate is done.

## Next

Proceed to Goal4705: source-level PTX canonicalization and repeated compile
cache-stability gate.
