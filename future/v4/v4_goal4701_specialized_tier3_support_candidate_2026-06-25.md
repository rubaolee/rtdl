# V4 Goal4701: Specialized Tier-3 Support Candidate

Date: 2026-06-25
Status: `goal4701_specialized_tier3_support_candidate_packet_not_public_support`

## Result

Goal4701 packages Goals4696-4700 as a narrow support candidate:

- candidate label: `specialized_numba_scalar_callback_support_candidate`
- scope: module-specialized Numba C-ABI scalar device callback called as a
  direct device function from an RTDL-generated OptiX hit-program route
- next goal: `Goal4702 specialized Tier-3 reliability matrix protocol`

Evidence:

- `future/v4/evidence/v4_goal4701_specialized_tier3_support_candidate_2026-06-25.json`
- `future/v4/evidence/v4_goal4701_specialized_tier3_support_candidate_2026-06-25.md`

## Evidence Chain

- Goal4689: minimal launch correctness for scalar callback
- Goal4691: SBT direct-callable overhead measured yellow at `1.6705538933080346x`
- Goal4692: pivot away from SBT direct-callable support
- Goal4693: specialized hit-program callback correctness
- Goal4695: specialized hit-program callback overhead passed at
  `1.0355240926982583x`
- Goal4696: productization decision for constrained specialized candidate
- Goal4697: API contract and negative validation scaffold
- Goal4698: compile/cache/error-reporting scaffold
- Goal4699: app-route validation protocol frozen
- Goal4700: weighted-sum app-route POD gate passed against Tier-2 denominator

## Satisfied Gates

- single scalar callback PTX generation
- OptiX module composition and launch correctness
- specialized hit-program overhead under `1.50x` focused gate
- one weighted-sum app-route parity/performance gate passed
- fail-closed rejection for arbitrary Python/action/external-memory/dynamic-SBT
  shapes
- public support flags remain false

## Missing Before Public Support

This is the important part: Goal4700 is strong, but it is not enough for public
support.

Still required:

- external 3-AI review of Goals4696-4700
- `20` compile/link/launch attempts across at least `4` accepted scalar
  callback variants
- dense/sparse/no-hit correctness datasets for the candidate route
- cache reuse and error-reporting behavior tested under repeated compiles
- user-facing docs wording reviewed and bounded
- final release/support authorization gate

## Verification

Local verification passed:

- `py scripts/v4_goal4701_specialized_tier3_support_candidate.py --json-out future/v4/evidence/v4_goal4701_specialized_tier3_support_candidate_2026-06-25.json --md-out future/v4/evidence/v4_goal4701_specialized_tier3_support_candidate_2026-06-25.md`
- `py -m unittest tests.v4_goal4701_specialized_tier3_support_candidate_test tests.v4_goal4700_specialized_tier3_app_route_result_test tests.v4_goal4699_specialized_tier3_app_route_protocol_test`
  - result: `7 tests OK`
- `py -m py_compile src/rtdsl/v4_goal4701_specialized_tier3_support_candidate.py scripts/v4_goal4701_specialized_tier3_support_candidate.py src/rtdsl/v4.py`

## Boundary

Not authorized:

- public Tier-3 support
- arbitrary callback support
- raw OptiX callback support
- broad V4 speedup wording
- whole-application speedup wording
- V4 release or tag claims

## Goal-Level Decision Audit

1. Was I being stupid?
   No. I did not convert one successful app-route into public support.

2. If yes, what action made it stupid?
   The bad action would have been to skip the reliability matrix and external
   review because Goal4700 looked good.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Treat this as a support candidate and explicitly list the remaining
   gates before support.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4702 should freeze the reliability matrix protocol before more
   POD execution.
