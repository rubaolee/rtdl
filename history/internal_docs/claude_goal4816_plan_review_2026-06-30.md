# Claude Review — Goal4816 v2.14 RayJoin Section 5.7 Numba Paper Reproduction Plan

Date: 2026-06-30
Reviewer: Claude (independent external reviewer)
Under review: `history/internal_docs/goal4816_v2_14_rayjoin_section57_numba_paper_reproduction_plan_2026-06-30.md`

## Verdict

```text
verdict: approve_with_required_amendments
goal4816_A: authorized to start (read-only paper/source contract extraction)
goal4816_B onward: not authorized until the 4 amendments below are applied
implementation / POD / runtime edits: not authorized
```

Strong, disciplined, and — unusually — **factually accurate where I checked it**.
Goal4816-A (read-only paper + author-source contract extraction) is the correct
first step and may begin. But before Goal4816-B, the document must close one
real gap that is directly inherited from the Goal4807 finding: it lists
RayJoin-specific **bundled helpers** as if they were generic v2.14 primitives,
and its classification taxonomy omits the `bundled_rayjoin_helper` category.

## What I independently verified (not trusting the doc)

- **Goal4380 numbers are exact.** `…/section57_overlay/section57_overlay_summary.md`
  contains County×Zipcode `5.521469 / 5.782340 / 15.121065` and Block×Water
  `27.943863 / 28.649871 / 53.792848`, count-match True — matching the doc.
  Note OptiX is marginally **slower** than author on both; the doc honestly says
  "near … process wall," not "faster." Good.
- **No goal-number collision:** the only `goal4816` file is this plan.
- **Reusable assets exist:** `rayjoin_overlay.py::_run_lsi_rows /
  _run_point_location_faces / _PreparedPointLocationRunner` (verified earlier),
  and the Numba functions (`describe_rayjoin_v2_6_numba_compact_mask_continuation`,
  `run_rayjoin_v2_9_numba_side_aware_topology_reference`,
  `filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba`).

## Required amendments (apply before Goal4816-B)

### A1 — The listed "primitives to reuse" are bundled RayJoin helpers, not generic primitives
The section "Existing v2.14 Primitives And Code To Reuse" lists
`rayjoin_overlay.py::_run_lsi_rows`, `_run_point_location_faces`, and
`_PreparedPointLocationRunner` as primitives. These are the **same
`rayjoin_overlay` bundled RayJoin-specific functions that Goal4807 classified as
`bundled_rayjoin_helper`** — app-identity code, not generic RTDL operators.
**Re-label them explicitly as `bundled_rayjoin_helper`** in that section, so they
are not read as generic v2.14 primitives.

### A2 — Add `bundled_rayjoin_helper` to the Goal4816-B classification taxonomy
Goal4816-B classifies each phase as `existing_v2_14_primitive` /
`numba_partner_continuation` / `paper_app_logic` / `author_baseline_only` /
`missing_input` / `missing_v2_14_capability`. It is **missing
`bundled_rayjoin_helper`**, which means LSI/PIP-via-`rayjoin_overlay` would be
mis-filed under `existing_v2_14_primitive`. Add `bundled_rayjoin_helper` as a
distinct category, carried verbatim from the Goal4807 review.

### A3 — State the standard in the Objective (decide, as Goal4806 had to)
"Using existing RTDL v2.14 primitives" is ambiguous between two very different
reproductions, and the result means different things in each:
- **(a) Honest bundled-helper reproduction:** run v2.14's bundled
  `rayjoin_overlay`. This proves "RTDL ships a RayJoin overlay helper that
  matches the author," and is partly **circular** (RTDL's own RayJoin code vs the
  author's RayJoin). It does **not** prove "v2.14 + Numba + generic primitives
  reproduce Section 5.7."
- **(b) Generic-primitive + Numba reproduction:** no bundled helper. But Goal4807
  showed the generic surface lacks LSI/PIP/overlay operators, so this likely
  resolves to `missing_v2_14_capability` for the LSI/PIP stages.

State which standard Goal4816 holds, and add a top-level boundary: **do not
present a `bundled_rayjoin_helper` result as generic-primitive or user-language
reproduction.** (Goal4816-C already half-says this; promote it to a hard
boundary.)

### A4 — Make the final labels capture the bundled-vs-generic distinction
Goal4816-E's final labels (`full_section57_reproduction`,
`bounded_2_of_8_available_input_reproduction`, etc.) do not record whether the
reproduction used the bundled helper or generic primitives — the distinction
that determines what was actually proven. Either add a
`bundled_helper_reproduction_not_generic` qualifier, or require each final label
to state the route class used.

## Note (non-blocking)

- The paper (`C:\Users\…\Downloads\ics24 (1).pdf`) and determinism summary live
  in user-local Downloads, not in the repo. Goal4816-A should copy the relevant
  contract/quotes into the in-repo notes file, since Downloads paths are not
  reproducible evidence.

## Answers to the seven questions

1. **Goal number correct / avoids 4807-4815 collision?** Yes — verified no
   collision; Goal4816 reasoning is correct.
2. **Goal4380 summary accurate?** Yes — 2/8 exact-ready, the two pairs' numbers
   verified exact, "near process wall" honest, 6/8 input gap, not full
   reproduction. Accurate.
3. **Requires reading paper §3.2/§5.7 + author source before coding?** Yes —
   Goal4816-A is read-only contract extraction; "no implementation step is valid
   until these reading notes exist." Correct.
4. **Reusable assets accurate / nothing key missed?** Assets exist, but **mis-
   labeled** — the `rayjoin_overlay` ones are bundled helpers (A1/A2), not generic
   primitives.
5. **Boundaries hard enough?** Yes, strong (no `src/rtdsl`/`src/native`/release-
   surface edits; no scalar-as-overlay; no 2/8-as-full; no process-wall-as-hot-
   parity; capability gap not patch). Add the bundled-vs-generic boundary (A3).
6. **PIP determinism / SoS tie-break handled correctly?** Yes — must come from
   paper/author source/author clarification, no silently invented RTDL policy,
   `blocked_by_pip_tie_break_gap` is a live label. Correct and strong.
7. **Authorize Goal4816-A?** Yes — read-only paper/source extraction is correct
   and independent of A1-A4. Require A1-A4 before Goal4816-B.

## Non-authorization

Authorizes only Goal4816-A (read-only). No implementation, no POD, no
`src/rtdsl/**` / `src/native/**` / v2.14-release edits, no new RayJoin-specific
primitive, no reproduction/performance claim, and no presenting bundled-helper
output as generic-primitive reproduction.
