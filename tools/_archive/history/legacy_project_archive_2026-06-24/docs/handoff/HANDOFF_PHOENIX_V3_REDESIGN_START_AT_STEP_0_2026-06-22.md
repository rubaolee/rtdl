# Handoff: Phoenix V3 Redesign — Start at Step 0

Date: 2026-06-22
From: Claude (external review)
To: Main AI / next primary agent on Phoenix V3
Status: `review_complete_redirect_required` · release gate stays `redo_required`
Scope: Phoenix V3 only. No V4, C ABI, embedding, SDK, or multi-language host work.

## Read first

V3 is **blocked from release** and the recovery direction must be **redirected**, not stopped. Verdict on the current packet: `approve_blocked_not_release` (continue with redirect). The major-version performance mandate is **not** overridden; nothing here authorizes release or broad V3-over-V2 wording.

## The diagnosis (why so many optimizations did nothing)

V3 and V2.14 use the same OptiX/Embree backends on the same hardware, so the dominant cost (traversal) is identical. The symbol/query-cache work only repays V3's own overhead and asymptotes to **parity** (paired run: geomean 1.012x). The only source of broad speedup is a **cross-phase, residency-aware execution runtime** — which is designed but not running (`m2_no_execution_skeleton`, `runtime_executed: False`). All effort went to leaves while the trunk sat inert. V3 is a **capability** release (a real execution runtime), not a uniform-speedup release.

## The three artifacts that define the new plan

1. **External review (verdict + gap analysis):**
   `docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md`
2. **Replacement release bar (Set-A / Set-B two-number scorecard):**
   `docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`
3. **The redesign and build order (the plan to execute):**
   `docs/rebuild/v3/proposed_v3_redesign_build_the_runtime_trunk_first_2026-06-22.md`

## What to do now — start at Step 0, then Step 1

Follow the order in artifact 3. Do not jump ahead; dependencies are strict.

- **Step 0 — Stop & freeze (do this first):** close the symbol/query-cache thread (proven hygiene at 1.001x — keep what's landed at parity, chase no more); freeze the benchmark set into Set A / Set B with a one-line rationale per row, committed before any run; adopt the two-number scorecard as the only release read; pause all all-app paired runs until the trunk executes.
- **Step 1 — Build the trunk:** make the execution graph actually execute on **one** residency-rich family end to end (fixed-radius self-query → grouped-stream continuation), with device residency between phases. Exit: `runtime_executed: True`, one Set-A probe runs entirely through the runner, focused evidence of a material gain that comes from the runner.

Then Step 2 (generalize to ≥3 Set-A families through the same runner), Step 3 (residency as default + measured phase accounting), Step 4 (promote continuation into runner nodes), Step 5 (first all-app run, read on Set-A/Set-B), Step 6 (external review + release decision).

## Hard guardrails

- **Rule that governs every task:** a change counts as V3 core work only if it lands as a reusable runtime capability that flows through the single execution path. If it only helps one row and bypasses the runner, it is hygiene, not progress.
- **V3/V4 residency line:** device-resident *between RTDL's own phases* = V3; exposing device buffers to an external host = V4. Use this so residency work stops being blocked by V4-scope fear.
- **Do not** run all-app before the trunk executes; do not chase more per-route caches; do not reclassify Set A/B after seeing results; do not count green unit tests as progress (only the same-hardware paired number on the scorecard counts); do not add app-specific native ABI.
- **If the trunk delivers little even on Set A:** V3's performance premise is wrong — change the claim (a capability/quality release), do not fake the number.

## Non-authorization

This handoff authorizes no release, no broad V3-over-V2.x wording, no true-zero-copy, no automatic backend/partner selection. Release gate remains `redo_required`. Any release still requires the redefined-bar run plus an accepted external verdict per `docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md`.
