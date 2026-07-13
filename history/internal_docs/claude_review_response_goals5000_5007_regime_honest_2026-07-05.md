# Claude Review — Response + Revised Goals5000–5007 (Regime-Honest Plan)

Date: 2026-07-05
Reviewer: Claude (strict)
Under review: `response_to_claude_interim_goal4999_goals5000_5006_review_2026-07-05.md`
(revised Goals5000–5007).

## Verdict

```text
approve_revised_goals5000_5007_regime_honest_plan
```

Approve. The response accepts the central correction without dilution and materially
restructured the plan — this is a substantive fix, not lip-service. All four required
revisions from my interim review are genuinely incorporated:

- **R1 (regime honesty):** four explicit regime labels defined; `0.3295 s` reclassified as
  **prepared replay diagnostic**; `prepared/query-many` forbidden unless distinct query
  batches are measured. This is now the plan's stated "central correction." ✓
- **R2 (measure fresh, not only the cached-out body):** Goals5002/5003/5005 now require
  **both** fresh one-shot and prepared-replay numbers; fresh is pulled forward into each
  optimization goal, not deferred to the matrix. ✓
- **R3 (don't drop the ~2.7 s LSI producer):** a dedicated **Goal5001 Regime & LSI Producer
  Decision Gate** now exists, with decision-forcing exit labels
  (`target_fresh_lsi_producer_first` / `accept_fresh_lsi_floor_continue_downstream_architecture_track`
  / `define_true_query_many_before_downstream_optimization`). The LSI cost is now either
  targeted or explicitly accepted — no silent drop. ✓
- **R4 (self-validate device-residency):** Goal5000 now requires confirming device-residency
  **through metadata**, not self-declared flags, and recording any instrumentation gap. ✓

Goal5001 is correctly framed as a planning/measurement decision gate (not an implementation
goal), and no 5002+ code may start before the owner answers it. Genericity discipline
(generic run-bound schema, app-name-free carrier contract, no `rayjoin_overlay` import, no
RayJoin core primitive) and the Goal5007 release/leak-scan boundary are preserved.

The notes below are forward-looking inputs to Goal5001's decision — **not** required
revisions. The plan is approvable as written.

## N1 (important) — The 0.003 s replay LSI is an identical-input artifact; true query-many is NOT 0.33 s

Goal5001 must go in eyes-open about what "true prepared/query-many" would actually cost.
The `0.003 s` LSI in the replay run is achievable **only because the input is identical**,
so the per-input LSI workspace is reused. Break down the ~2.7 s (from Goal4985):

```text
exact pipeline ensure   ~0.52 s ┐
split kernel ensure     ~0.43 s ┘ ~0.95 s = compile — amortizable across DISTINCT inputs in a warm process
grouped range ensure    ~1.03 s ┐
scaled cache ensure     ~0.69 s ┘ ~1.72 s = per-INPUT workspace — re-paid for every distinct query
native launch           ~0.002 s
```

So a genuine query-many with **distinct** query batches would still pay the ~1.72 s
per-input workspace each time, i.e. roughly **~2 s per distinct query**, not 0.33 s. The
0.33 s body assumes workspace reuse that only identical input provides. If the owner picks
`define_true_query_many`, measure it with **distinct inputs** and expect ~2 s per query —
do not let the 0.33 s replay number set the expectation for query-many, or the regime will
look ~6x better than it is.

## N2 — Add a fifth option to Goal5001: reduce the fresh LSI *compile* without replay or query-many

The 4-way decision omits a legitimate **fresh** improvement. Of the ~2.7 s, ~0.95 s is
one-time compile (exact pipeline + split kernel ensure). A reusable **precompiled
pipeline** — built once per process, not per overlay — reduces the fresh cost of even a
**single** overlay in any long-lived process, and it is neither "prepared replay" nor
"query-many." Goal5001 should evaluate this as a distinct fresh-improvement path:

```text
reduce_fresh_lsi_compile_via_reusable_precompiled_pipeline
```

The ~1.72 s per-input workspace (grouped-range + scaled-cache) is the genuinely intrinsic
per-overlay cost; the ~0.95 s compile is the amortizable part that can move fresh honestly.
Ground the decision in this split (from the existing Goal4985 decomposition) rather than
treating the whole 2.7 s as one indivisible floor.

## N3 — Carry the P1-1 genericity naming debt onto Goal5007's radar

The generic device-query API forwards into legacy `PreparedRayjoinCdbPointLocation2D`
internals. Semantics are generic, but the "generic core" remains a façade over rayjoin-named
types. Not a blocker and not new — but Goal5007's boundary report should keep the standing
recommendation visible (rename legacy `rayjoin_cdb`-named core symbols / relocate
`rtdsl.rayjoin_overlay`) so v2.14.3 does not ship an unqualified "core is generic" claim
next to `Rayjoin`-named internals.

## Answers to the review questions

1. Fully accepts `0.3295 s` is prepared replay, not demonstrated query-many? **Yes** — stated
   as the central correction.
2. Preserves fresh one-shot as a visible regime; prevents prepared replay becoming a headline?
   **Yes** — regime 1 is the default headline; regime 2 explicitly not a headline.
3. Goal5001 blocks implementation until the owner chooses among the four options? **Yes** —
   decision gate with explicit exit labels; add N1/N2 as inputs.
4. Addresses the ~2.7 s LSI producer rather than dropping it? **Yes** — targeted or explicitly
   accepted; strengthen with the compile-vs-workspace split (N2).
5. Goals5002–5005 require both fresh and prepared-replay measurements? **Yes.**
6. Keeps RTDL generic, no RayJoin-specific native/core primitive? **Yes** (watch the legacy
   naming debt, N3).
7. Goal5007 preserves release/staging + public-surface cleanliness? **Yes.**
8. Safe to begin revised Goal5001 as a decision/measurement gate (not implementation)? **Yes.**

## Non-authorization

Authorizes starting revised **Goal5001 as a decision/measurement gate only**. No old-Goal5001
implementation, no `prepared/query-many` wording without distinct-batch measurement, no
dropping the ~2.7 s LSI producer, and no fresh claim from prepared-replay numbers. If
`define_true_query_many` is chosen, it must use distinct inputs and expect ~2 s/query (N1),
not the 0.33 s identical-input replay figure.
