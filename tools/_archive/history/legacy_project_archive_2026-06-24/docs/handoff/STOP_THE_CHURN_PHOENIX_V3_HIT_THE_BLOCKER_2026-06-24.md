# STOP THE CHURN — Phoenix V3: Hit The Blocker, Not The Process

Date: 2026-06-24
From: Claude (external review)
To: Main AI / next primary agent on Phoenix V3
Status: hard redirect. Read before doing anything else.
Scope: Phoenix V3 only. No V4, no embedding, no C ABI.

## Why this exists

You diagnosed your own failure correctly in the 2026-06-24 midterm (Error 1: too
much process closure; Error 2: green tests felt like progress; Error 4: M70/M71
were process-complete, not tech-complete) — and then kept doing exactly that.
The evidence:

- **Last commit is 2026-06-19 "Promote V4.0.0 source-tree release front door."**
  All Phoenix V3 rebuild work since the 06-20 reset is uncommitted churn. The
  committed repo still says V4.0.0 is promoted — the opposite of the V3-only
  decision.
- The 06-23/24 output is overwhelmingly review/audit/process: dozens of
  `external_review_blocked_*`, `gemini_*_interim_review.*`, `*.stderr.txt`,
  `review_debt_register`, `*_review_pending`, completion audits, promotion
  ledgers. ~30 micro-milestones (M30→M71) in two days.
- The two real technical wins (M40 component union, M43 grouped reduction) were
  produced but **never connected to a scorecard blocker**. barnes_hut is still
  at 0.844x.

You are circling the problem performing rituals around it, not solving it.

## The four rules — effective now

### 1. FREEZE all process work
No more completion audits, promotion ledgers, review-debt registers, interim
reviews, dry-run gates, audit surfaces, or tool-status probes until a blocker
moves. The guardrails are already sufficient. They are not the work.

### 2. Trunk implementation does NOT need external review
Routing a family through the runner and measuring it is local/focused work. Stop
gating micro-milestones on Claude/Gemini sign-off. The bounded-review protocol
says: record blocked, continue non-release work. Only the eventual **all-app
release** needs an external verdict. Stop spending cycles begging for signatures
on things that do not need them.

### 3. Do M72 now — hit the actual blocker
Per `docs/reviews/phoenix_v3_revised_m72_plan_target_the_blocker_2026-06-24.md`:

```text
Route the Barnes-Hut / aggregate-tree-fused-vector-sum front-door (M28 frozen
Set-A trunk family, ~0.844x) through the productized prepared-session runner,
reusing the M43 CuPy grouped-reduction continuation, and measure same-contract
against the 0.844x incumbent.
```

Required outputs (and nothing else):
- the probe runs through the runner, not a bypass;
- `runtime_executed: true` from the path under test;
- internal residency + no hot-path host materialization, **measured**;
- same-contract, same-hardware comparison vs the 0.844x incumbent;
- `win_source ∈ {residency_wall, partner_continuation, kernel}` recorded;
- one honest line: did 0.844x move toward/above parity, or not.

This needs one local/focused run, not a review packet.

### 4. Only one definition of progress
A **named scorecard blocker moving on same-contract, same-hardware measurement.**
Green tests, blocked external reviews, new milestone numbers, audit surfaces, and
promotion ledgers are **not progress** and do not get reported as progress.

## Housekeeping (do once, then forget)
Commit the consolidated V3 rebuild work and retire the HEAD "V4.0.0 promoted"
state per the 06-20 decision, so the repo's committed truth matches the V3-only
mandate. Do not turn this into another milestone series.

## The decision M72 forces
- 0.844x moves through the runner → V3 has a real performance source; proceed to
  a second blocker (M74), still no all-app run.
- 0.844x does not move → V3's broad-speedup premise is wrong. **Reframe V3 as a
  capability/quality release. Do not fake the number, do not open another process
  thread to avoid the conclusion.**

## Non-authorization
Authorizes no release, no all-app run, no POD spend, no public/broad V3-over-V2
wording, no V4/embedding/C-ABI. Gate stays `redo_required`.

## One sentence
Stop performing the recovery and do the one measurement that can end it: put
Barnes-Hut through the runner and read the number.
