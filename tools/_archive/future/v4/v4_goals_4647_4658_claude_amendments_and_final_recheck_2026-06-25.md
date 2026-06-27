# V4 Goals 4647-4658 Claude Amendments And Final Recheck

Date: 2026-06-25
Status: binding amendment record for the next V4 work
User instruction: re-open and recheck this record before declaring V4 complete.
Source review: `docs/reviews/claude_v4_goals_4647_4658_review_2026-06-25.md`
Reviewed proposal:
`future/v4/v4_goals_4647_4658_partner_promotion_and_all_app_gate_for_claude_review_2026-06-25.md`

## Verdict To Carry Forward

```text
verdict: approve_with_required_amendments
release_authorized: false
pod_spend_authorized: false
execute_as_written_authorized: false
expected_outcome_to_state_upfront: bounded_operator_v4_only + partner unification
```

Claude's review accepts the direction: promote real V2.14 CuPy/Numba partner
assets into the V4 front door, then run a serious app-level gate. It does not
approve the goal list as written. AM1-AM6 below must be applied before execution.

## AM1 - Partner Migration Is Not A V4 Speed Win

This is the central integrity lock.

V2.14 already had high-performance CuPy and Numba partner routes. Moving one of
those known-good routes behind a cleaner V4 front door is valuable product work,
but it does not prove V4 is faster than V2.14.

Rule:

- `partner_migration` rows prove `V4 front door unifies known-good partner route`.
- `partner_parity` rows prove `V4 did not regress a known-good partner route`.
- Neither row type may trigger `formal_high_performance_v4_supported`.
- Only runtime/operator gains that are new to V4, or newly fused generic V4
  operator wins against the proper V2.14/V3 denominator, may support "V4 faster
  than V2.14."

Required edits:

- Add this rule to the revised Goal4647/4648 boundary ledger.
- Enforce it in Goal4656 benchmark analysis.
- Enforce it again in Goal4658 final authorization.

Final V4 recheck question:

```text
Did any formal V4 speed claim rely on partner migration or partner parity?
If yes, block release wording and rewrite the conclusion.
```

## AM2 - The App-Level Bar Must Match Phase A Reality

Phase A showed many apps are backend-bound or near parity. A uniform whole-suite
geomean bar such as `>= 1.20x` would recreate the V3 trap: it asks V4 to win
where V4 has no physical lever.

Rule:

- Freeze separate classes before running:
  - fused-operator-addressable rows;
  - backend-bound parity rows;
  - partner-migration/parity rows;
  - no-route blockers;
  - deferred rows, if any.
- Set performance bars only where V4 has a real fused-operator lever.
- Backend-bound and partner-parity rows must have parity floors and explanation
  gates, not speedup demands.

Required edits:

- Revise Goal4653 so it does not freeze a single broad whole-suite geomean bar.
- The gate may still report total suite results, but formal high-performance
  authorization must come from the pre-frozen addressable subset, not from
  reinterpreting all rows after the run.

Final V4 recheck question:

```text
Was the release bar frozen around addressable V4 operator leverage, with parity
rules for backend-bound/partner rows, before any POD run?
```

## AM3 - Route Binding Must Precede Protocol Freeze

The original proposal froze the full app-level protocol before knowing which
apps actually had V4 routes. That order is backwards.

Rule:

- Goal4654 route binding / blocker declaration must happen before Goal4653
  app-level protocol freeze, or be merged into it as the first section.
- The frozen protocol must know, per app:
  - real V4 route;
  - no-route blocker;
  - required CuPy promotion;
  - required fixed Numba continuation;
  - backend-bound status;
  - deferred/excluded status.

Required edits:

- Reorder the revised chain:
  - inventory/contract;
  - partner certification;
  - catalog promotion;
  - app route binding/blocker declaration;
  - then app-level protocol freeze.

Final V4 recheck question:

```text
Was every benchmark app route-bound or blocker-labeled before the all-app
protocol and bars were frozen?
```

## AM4 - Quantify "Material Speedup" Before Running

The original Goal4650/4651 used "material speedup" without a number. That
violates the chain's own freeze-before-run rule.

Rule:

- Every promotion gate must define numeric thresholds before measurement.
- Examples may be `>= 1.20x`, `>= 1.50x`, or a per-surface frozen floor, but the
  chosen value must be written before the run and tied to denominator/scale.

Required edits:

- Add numeric pass bars to:
  - CuPy certification;
  - fixed Numba continuation certification;
  - any promoted V4 operator route.
- Do not use the word "material" without an explicit numeric definition.

Final V4 recheck question:

```text
Were all "material speedup" thresholds numeric, written before the run, and
preserved after seeing results?
```

## AM5 - Compress Goal4647 Into The Inventory Ledger

Goal4647 overlaps Goal4642/4643/4646, where current V4 truth and public wording
were already frozen. Re-freezing truth as a standalone goal risks process churn.

Rule:

- Do not run a standalone "truth freeze" goal unless new evidence exists.
- Make the current-truth record a thin first section of the V2.14 partner
  inventory goal.

Required edits:

- Merge the original Goal4647 into revised Goal4648 as a boundary ledger.
- Keep it to one page plus JSON rows.

Final V4 recheck question:

```text
Did we avoid creating a process-only freeze goal when a thin ledger was enough?
```

## AM6 - State The Expected Outcome Up Front

The most likely honest outcome is not broad high-performance V4. It is:

```text
bounded_operator_v4_only + partner unification
```

That outcome is not failure. It means V4 has a cleaner front door and certified
partner/catalog support, while broad app-level superiority remains unproven.

Rule:

- The revised goals must state this expectation before running.
- The final analysis must be allowed to land on bounded operator release without
  moving goalposts.

Required edits:

- Put the expected outcome in the revised goal chain introduction.
- Put the same expectation in the all-app protocol.
- Put it in the final Goal4658 review request.

Final V4 recheck question:

```text
Did we state before measurement that bounded operator V4 + partner unification
is the expected outcome, and did we avoid treating that as failure afterward?
```

## Revised Goal Chain Shape

The next version of the goals should be rewritten roughly as:

| Revised goal | Meaning |
| --- | --- |
| Goal4647 | V2.14 CuPy/Numba partner inventory with a one-page V4 truth/boundary ledger |
| Goal4648 | V4 partner promotion contract with numeric bars |
| Goal4649 | CuPy front-door certification under quantified gates |
| Goal4650 | Fixed Numba continuation certification under quantified gates |
| Goal4651 | V4 partner catalog promotion and regression gate |
| Goal4652 | App route binding or blocker declaration |
| Goal4653 | Full app-level protocol freeze, based on the bound routes/blockers |
| Goal4654 | Serious full app-level V2.14/V3/V4 POD benchmark |
| Goal4655 | Benchmark analysis with partner-migration lock |
| Goal4656 | User docs/tutorial rewrite based on measured truth |
| Goal4657 | Final 3-AI release or reframe authorization |

The exact numbering may keep Goal4658 if needed, but the dependency order must
follow the table above.

## Final V4 Completion Recheck

Before declaring V4 complete, open this file and answer every item below:

- [ ] AM1: No V4 speed claim relies on partner migration or partner parity.
- [ ] AM2: Bars are class-aware, not a naive whole-suite geomean trap.
- [ ] AM3: Every app was route-bound or blocker-labeled before protocol freeze.
- [ ] AM4: All material-speed thresholds were numeric and frozen before runs.
- [ ] AM5: Process-only truth-freeze churn was avoided.
- [ ] AM6: Expected outcome was stated upfront as bounded operator V4 + partner
      unification unless app-level evidence proves more.
- [ ] Correctness parity passed for every promoted row.
- [ ] Every ratio has a baseline denominator and scale.
- [ ] CuPy claims are only for V4-certified CuPy surfaces.
- [ ] Numba claims are only for fixed certified continuations, not arbitrary
      callbacks.
- [ ] No app-identity kernels were added.
- [ ] No benchmark app was silently skipped.
- [ ] The final decision was reviewed by 3 AI seats before any broad release
      wording or tag.

## Goal-Level Decision Audit

Decision:

Record Claude's `approve_with_required_amendments` review as binding and block
execution of the old Goal4647-4658 list until AM1-AM6 are applied.

1. Was I stupid?
   No for this decision. Accepting the amendments prevents the exact overclaim
   failure the user warned about.

2. What action would have made the decision stupid?
   Treating Claude's approval-with-amendments as approval-as-written, especially
   ignoring AM1 and using partner migration as a fake V4 speed win.

3. Was there another path?
   Yes: continue with the old proposal and hope the final analysis sorts it out.
   That would repeat V3-style goalpost drift.

4. Can I now take a better path?
   Yes. Rewrite the goal chain with AM1-AM6 first, then execute only the revised
   chain.

## Non-Authorization

This record does not authorize implementation, POD spend, broad V4 speedup
claims, CuPy performance claims, arbitrary Numba callback claims, app-level V4
speedup claims, C ABI/embedding claims, or release tagging. It only records the
required amendments and the final recheck gate.
