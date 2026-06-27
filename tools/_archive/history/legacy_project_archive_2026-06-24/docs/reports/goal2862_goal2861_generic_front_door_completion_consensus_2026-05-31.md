# Goal2862: Goal2861 Generic Front-Door Completion Consensus

Status: accepted for the internal v2.5 development lane.

Date: 2026-05-31

## Scope

This consensus covers Goal2861, which adds generic partner-column front doors
for the remaining promoted v2.5 continuation operations:

- `grouped_argmin_f64_partner_columns`
- `grouped_argmax_f64_partner_columns`
- `grouped_topk_f64_partner_columns`
- `bounded_collect_finalize_i64_partner_columns`

Together with the existing grouped-vector-sum and scalar segmented adapters,
`v2_5_triton_front_door_coverage()` now reports 10/10 promoted benchmark apps
as adapter-front-door-ready.

## Evidence

Implementation report:

- `docs/reports/goal2861_v2_5_generic_partner_front_door_completion_2026-05-31.md`

External review:

- `docs/reviews/goal2862_gemini_review_goal2861_generic_front_door_completion_2026-05-31.md`

Handoff:

- `docs/handoff/HANDOFF_GEMINI_GOAL2861_GENERIC_FRONT_DOOR_COMPLETION_REVIEW_2026-05-31.md`

Validation recorded by Goal2861:

- Local focused structural/front-door tests passed.
- Pod executable Triton wrapper tests passed on `69.30.85.171:22167`.
- The pod run exercised grouped argmin, grouped argmax, grouped top-k, and
  bounded collect/finalize through the new generic adapter front doors.

## Verdict

Codex implementation verdict: `accept-with-boundary`.

Gemini independent review verdict: `accept-with-boundary`.

Consensus verdict: `accept-with-boundary`.

## Boundary

Goal2861 improves v2.5 usability and app migration ergonomics. It does not
authorize public speedup claims, final release claims, true zero-copy wording,
or automatic Triton selection where partner-selection guidance says another
same-contract path is faster.

The native engine remains app-agnostic. The new APIs are generic
partner-column continuations only.
