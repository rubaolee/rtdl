# Claude Review — V4 Goals 4647-4658 (Partner Promotion And All-App Gate)

Date: 2026-06-25
Reviewer: Claude (independent external reviewer)
Under review: `future/v4/v4_goals_4647_4658_partner_promotion_and_all_app_gate_for_claude_review_2026-06-25.md`
Companions: `claude_v4_0_0_release_review_2026-06-25.md`, `rtdl_v4_0_three_tier_fused_architecture_design_2026-06-24.md`

## Verdict

```text
verdict: approve_with_required_amendments
release_authorized: false
pod_spend_authorized: false
expected_outcome_to_state_upfront: bounded_operator_v4_only + partner unification
```

This is a strong, discipline-laden chain — the best-structured goal proposal in
the V3/V4 history. Approve it, with six required amendments before execution. The
amendments are integrity fixes (so the chain cannot be read as a broad-speedup
win it will not produce), not nitpicks.

## Credit (what this chain got right)

- Distinguishes **V2.14 historical partner success from V4 certified support** —
  no reusing old ratios, must re-migrate and re-certify under V4 contracts.
- **Correctness parity as a hard gate**, equal to performance.
- **Records baseline denominator + scale** for every measured result (my A3).
- **No post-hoc reclassification; freeze bars before runs.**
- **No app-identity kernels; no skipping apps** (record `no_v4_app_route_blocker`).
- **Arbitrary Numba callback stays out** (Tier-3 spike only); only fixed
  continuation operators promoted.
- **Separates win categories** (true V4 operator / partner-migration /
  algorithmic-complexity / parity / regression / no-route) — exactly my A2.
- Keeps `no_go_reframe_required` as a live decision label.

## Required amendments

### AM1 — Forbid partner-migration / partner-parity wins from supporting "V4 faster than V2.14" (the central integrity fix)
A CuPy grouped-reduction win is a **CUDA-core (partner) win, not an RT-core V4
win.** If V4's route for an app is "RT traversal + CuPy continuation" and
V2.14's route was the *same partner*, then V4/V2.14 ≈ 1.0x — there is no V4 gain,
because it is the same work behind a new front door. So **partner promotion
cannot, by construction, make V4 beat V2.14 on apps where V2.14 already used that
partner.** The chain separates the categories in Goal4656, but Goal4658's
`formal_high_performance_v4_supported` label must be **explicitly forbidden from
firing on partner-migration or partner-parity rows.** Partner promotion proves
"V4's front door unifies access to known-good partner routes" — a real product
value — but **not** "V4 is faster than V2.14." State this in Goal4647 and enforce
it in Goal4656/4658.

### AM2 — Goal4653 frozen bars must match the Phase A reality, or the gate is designed to fail
Phase A proved most apps are backend-bound → V3 ≈ V2.14 parity, and only the
fused Tier-2 operators add anything. So the expected all-app result is "a few
fused-operator-addressable apps win modestly, most parity, barnes_hut/rayjoin
excluded." If Goal4653 freezes a **uniform whole-suite geomean threshold** (e.g.
a V3-style 1.20x), the gate is built to fail on workloads that physically cannot
win — the exact V3 trap. **Set the bar around the fused-operator-addressable
subset (Set-A-style), with parity-with-explanation on backend-bound and
partner-parity rows.** Do not demand uniform suite-wide speedup.

### AM3 — Reorder: route binding (Goal4654) must precede the protocol freeze (Goal4653)
You cannot freeze a meaningful all-app protocol (4653: apps, routes, bars) before
knowing which apps even have a V4 route and which are `no_v4_app_route_blocker`
(4654). As written, 4653 freezes a 10-app protocol before 4654 may reveal 4 of
them are blockers. **Merge 4654 into 4653, or run 4654 first**, so the frozen
protocol reflects actual route availability.

### AM4 — Quantify "material speedup" before running (the chain violates its own freeze rule)
Goal4650 ("at least two surfaces show material speedup") and Goal4651 ("at least
one produces material runtime-sourced speedup") leave **"material" undefined**.
The chain's own rule says freeze bars before runs. **Define the material
threshold numerically** (e.g. ≥1.2x or ≥1.5x vs stated baseline) in 4649/4650/4651
before any POD, or it gets reinterpreted after results.

### AM5 — Compress Goal4647 (it overlaps the already-frozen Goal4642/4643/4646 truth)
The current truth and scope were just frozen in Goal4642/4643 and corrected in
Goal4646. Goal4647 risks being a restatement. **Make it a one-page boundary
ledger appended to Goal4648, not a standalone goal** — otherwise it is the
freeze-the-truth-again process motion the chain is trying to avoid.

### AM6 — State the expected outcome upfront
Per Phase A, the most likely honest result of this entire chain is
`bounded_operator_v4_only` + partner unification, **not**
`formal_high_performance_v4_supported`. **Write that expectation into Goal4647/4653
upfront**, so a not-broad result is a confirmation, not a disappointment that
tempts goalpost-moving. The chain must be equally happy landing on
`bounded_operator_v4_only`.

## Answers to the seven questions

1. **Continues correctly after Goal4646?** Yes, with AM3 reorder and AM5 compression.
2. **Preserves V2.14-historical vs V4-certified distinction?** Yes — strongly. AM1 sharpens what a partner win can and cannot claim.
3. **CuPy / fixed Numba handled without pretending arbitrary callbacks are supported?** Yes — correct. Tier-3 stays spike-only; fixed operators only.
4. **Is the app-level gate strict enough?** Structurally yes, but only after AM2 (bar matched to Phase A reality) and AM1 (partner-parity ≠ V4 win). Without those, it can either be built to fail or be passed by relabeled partner wins.
5. **Any process churn?** Document-to-measurement ratio is high (≈7 docs / 5 measurement goals). Most docs are legitimate gates, but Goal4647 is redundant (AM5). Keep the freeze/contract/protocol docs thin.
6. **Are labels/forbidden actions strong enough to prevent another V3-style overclaim?** Close — the missing lock is AM1 (the partner-migration-is-not-a-V4-win rule). Add it and yes.
7. **Merge/split/remove/reorder?** Merge 4647→4648 (AM5); merge/reorder 4654 before 4653 (AM3); quantify bars in 4649-4651 (AM4). No goal needs removal.

## One note on the V3 column
V3 ≈ V2.14 (parity, proven). So in Goal4655/4656 the V4-vs-V3 and V4-vs-V2.14
columns will be ≈ the same comparison; the V3 column is mostly redundant. Keep it
for completeness, but do not interpret small V4-vs-V3 differences as meaningful —
they are noise around parity.

## Non-authorization

Approving this chain (with amendments) authorizes only its *execution as a gated
investigation* — no implementation shortcut, no POD spend before Goal4653 review,
no public/broad/near-OptiX wording, no CuPy performance claim before Goal4650, no
arbitrary-callback claim, no C-ABI/embedding, no app-identity kernels, no release
tag without Goal4658 3-AI authorization.
