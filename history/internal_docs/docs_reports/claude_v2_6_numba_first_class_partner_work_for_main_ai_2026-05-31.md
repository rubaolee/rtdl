# v2.6 Work Plan for Main AI: Numba as a First-Class Partner (Neutral-Seam-Gated, Benchmark-Demonstrated)

Author: Claude (independent reviewer / design)
Date: 2026-05-31
Audience: Main AI (coordination / consensus), Gemini (second reviewer)
Status: planning / work-definition note for v2.6. Not a v2.5 release artifact.

This note authorizes nothing: not v2.5 or v2.6 release, not public/whole-app/broad-RT-core/Triton/Numba speedup wording, not true-zero-copy wording, not automatic partner selection, not paper-reproduction, not app-specific native engine logic. Any release still requires an explicit user-requested release packet and a fresh 3-AI consensus.

Companion context:
- `docs/reports/v2_5_partner_choice_and_multi_partner_composition_design_2026-05-29.md` (Principle 1 and the §3.3 neutral-seam leak; with its Post-Goal2896 correction)
- `docs/reports/claude_v2_5_closeout_and_v3_0_residency_first_roadmap_2026-05-31.md` (the C-3 seam decision this work depends on)
- `docs/reviews/goal2773_claude_review_v2_5_status_next_goals_2026-05-31.md` (original numba/CuPy partner-set mismatch)

## 1. One-paragraph summary

In v2.6, bring Numba to the same *kind* of first-class partner support that CuPy has today, on the principle that partner choice belongs to the user: if RTDL claims Numba is a partner, that claim must be **demonstrated by a benchmark app actually routing a real continuation phase through Numba with correctness parity**, not merely declared in a matrix. The work is **gated on closing the neutral-buffer-seam leak** (Principle 1, design §3.3): until the handoff stops coercing columns to torch tensors and instead hands out a neutral `__cuda_array_interface__`/DLPack buffer, a Numba CUDA array is a second-class partner that pays a torch conversion. Numba CUDA device arrays expose `__cuda_array_interface__`, so the seam fix is exactly what makes genuine Numba support possible. Scope is deliberately narrow: support the continuation shapes a benchmark app exercises, with a reference-parity test each and **no performance claim** — same claim discipline applied to Triton.

## 2. Current state (verified in code)

- **Numba is implemented but idle.** `src/rtdsl/numba_partner_continuation.py` has real `@cuda.jit` kernels for exactly two ops — `run_numba_segmented_count_i64`, `run_numba_segmented_sum_f64` — plus `numba_partner_available()` and validation kernels.
- **Numba is the declared fallback partner.** `partner_continuation_protocol.py`: `V2_5_FALLBACK_PARTNER = "numba"`. It appears in the partner support matrix, conformance matrix, execution-path policy, and neutral-seam consumer list.
- **Runtime-validated, but only as a 2-op correctness smoke.** Goal2875 installed Numba 0.65.1 on the RTX A5000 pod and recorded `conformance_status = POD_RUNTIME` for those two ops; everything else numba-wise is descriptor-only or unrecorded.
- **Not used by any app in a load-bearing way.** Numba is referenced in only one of the ten benchmark apps (`raydb_style`), as an available option, not a measured results path. The actual non-Triton workhorse across apps (DBSCAN union-find, Hausdorff) is **CuPy**.

So today: Numba = declared fallback + 2-op runtime smoke + zero app usage. CuPy = the real partner that benchmark apps depend on. "Same-level support" means closing that gap honestly.

## 3. Why this is correct (and where the discipline must hold)

- **Correct in principle.** Partner choice belongs to the user (design Principle 1). Numba `@cuda.jit` is a mainstream way for Python users to write custom CUDA kernels; some users prefer it to CuPy/Triton. Supporting it as a *choosable* partner serves real users and is consistent with "no partner is forced."
- **"Demonstrated by benchmark apps" is the right proof of support.** A declared matrix row is not support; an app that selects Numba and produces correct results is. This is the same lesson from the Triton review chain: metadata-declared support ≠ real support.
- **Support must NOT slide into performance endorsement.** This is the load-bearing caveat. After Goal2896 (primitive-first beats partners on fusible reductions; partners are for unfused continuations, chosen by same-contract evidence), "Numba is supported (an app runs it correctly)" must never be read as "Numba is fast" or "use Numba." No Numba speedup wording without a separate same-contract gate. Hold exactly the discipline applied to Triton.

## 4. The prerequisite: close the neutral-buffer-seam leak (C-3)

This is the gate. Per design §3.3, the v2.5 hit-stream handoff coerces columns to torch tensors (`_maybe_torch_column`, `gather_typed_payload_columns_for_hit_stream`). A CuPy array or a Numba CUDA device array therefore runs through a torch conversion — "torch/Triton, or pay a copy." Consequences for this work:

- Without the seam fix, "Numba support" would mean "Numba via a torch round-trip," which is second-class and contradicts Principle 1.
- Numba CUDA device arrays expose `__cuda_array_interface__`; CuPy arrays do too. The neutral seam (DLPack / `__cuda_array_interface__` descriptor, which `RtdlBufferDescriptor` was started to be) is precisely what lets both be consumed without torch in the middle.
- Therefore the Numba-first-class goal and the neutral-seam fix are the same work seen from two angles. **Do the seam fix first; it simultaneously upgrades CuPy and Numba to genuine first-class partners.**

If the project instead chose (in the v2.5 closeout C-3 decision) to *scope the seam out of v2.5*, then v2.6 must do it as its opening item — Numba-first-class is not achievable without it.

## 5. Scope guards (avoid the Triton "wide surface nobody uses" trap)

- **Cover the ops a benchmark app exercises, not exhaustive op parity.** Do not reimplement every continuation op in Numba "for completeness." Pick one app + the continuation shape(s) it actually routes through a partner, and make Numba a real choice there.
- **One demonstrating app is enough for the v2.6 claim.** "Same-level as CuPy" means "same level on the demonstrated path," not "Numba everywhere CuPy is."
- **Every Numba op ships with its CPU/reference parity path** (Principle 2: the universal partner-free path). No op is Numba-only.
- **No performance work in this goal.** Correctness + choosability only. A separate same-contract gate (the C-2 method) may later measure Numba vs CuPy vs reference if a user cares, but that is not part of declaring support.

## 6. Sequenced work (goal numbers are placeholders)

| # | Item | Type | Exit gate |
| --- | --- | --- | --- |
| N-0 | Close the neutral-buffer-seam leak: hand out a neutral `__cuda_array_interface__`/DLPack descriptor; partners (torch/CuPy/Numba/raw) consume without torch coercion; copy vs borrow is runtime-observed and labeled (reuse the Goal2883/2889 pointer-evidence + lease pattern) | architecture | a CuPy array and a Numba CUDA array each pass through the seam with no torch conversion on the path; transfer status is measured, not assumed |
| N-1 | Bring Numba op coverage to the continuation shape(s) the chosen demonstrating app needs (start from the existing 2 reduction ops; add only what the app uses) | runtime | each Numba op has a CPU-reference parity test; `numba_partner_available()` gates cleanly |
| N-2 | Wire one benchmark app to route a real continuation phase through Numba as a *selectable* partner (parameter at the continuation boundary, never hardcoded), matching the CPU reference exactly | app integration | the app runs end-to-end on Numba with `matches_cpu_reference == true`; partner is user-selected; reference path still runs with no partner |
| N-3 | Update the partner conformance matrix + readiness snapshot so Numba's demonstrated ops carry pod-runtime conformance and an app-usage reference, keeping `release_conformance_complete=false` and no speedup/auto-select authorization | docs/policy | matrix shows Numba at parity-of-*kind* with CuPy on the demonstrated path; all blocked actions intact |
| N-4 | Record an honest v2.6 closeout line: "Numba is a first-class, user-selectable partner demonstrated by `<app>` with correctness parity; no performance claim" | docs | closeout states delivered/not-delivered; no Numba speedup wording |

## 7. Acceptance criteria

- The neutral seam hands a Numba CUDA array (and a CuPy array) to a partner continuation **without a torch conversion on the data path**, with copy/borrow status runtime-measured and labeled (not asserted).
- At least one benchmark app runs a real continuation phase on Numba, **user-selected**, producing results that match the CPU reference exactly, with the partner-free reference path still intact.
- Every Numba op exposed has a reference-parity test; no Numba-only op exists.
- The conformance matrix/readiness snapshot reflects Numba's demonstrated support honestly, keeps `release_conformance_complete=false`, and authorizes no speedup/auto-selection.
- No document implies Numba is fast or recommended; support and performance remain separate, as for Triton.

## 8. Explicit non-goals / boundaries

- Not exhaustive Numba parity across all continuation ops.
- Not a Numba performance claim, benchmark win, or partner recommendation.
- Not automatic Numba (or any) partner selection — selection stays explicit and the app's.
- Not a v2.5 or v2.6 release authorization.
- Not paper-reproduction, not app-specific native engine logic (engine stays app-agnostic; Numba is partner-side continuation only).

## 9. Dependencies and sequencing relative to v2.5

- N-0 (neutral seam) is the same item as the v2.5 closeout decision C-3. If C-3 chose to fix the seam in v2.5, N-0 is already done and v2.6 starts at N-1. If C-3 scoped the seam out, N-0 is v2.6's first item and everything else follows it.
- This work should not block the v2.5 closeout; it is a v2.6 lane. Keep the v2.5 closeout honest about Numba's *current* state ("implemented fallback, 2-op smoke, not app-used") and let v2.6 deliver the first-class upgrade.

## 10. Questions for Main AI / Gemini

1. Do you accept Numba-first-class as a v2.6 goal, gated on the neutral-seam fix and demonstrated by one app (not exhaustive op parity)?
2. Which app should be the Numba demonstrator? (RayDB already references Numba and uses fusible scalar reductions — easy but low-value; a Tier B/unfused continuation would be a stronger demonstration but more work. Recommend the simplest app that exercises a *real* continuation, to prove the seam and selection mechanics, not to chase a hard kernel.)
3. Was the neutral seam fixed in the v2.5 closeout (C-3a) or scoped out (C-3b)? That decides whether N-0 is already done.
4. Do you agree support and performance must stay strictly separated for Numba (no speedup wording from this work), consistent with the Triton discipline?
5. Any objection to keeping the demonstrating-app set to one for the v2.6 "same-level" claim, with broader Numba coverage deferred to demand?

## 11. Bottom line

Yes — Numba should get the same *kind* of first-class, user-selectable support CuPy has, in v2.6, because partner choice is the user's and genuine support means a benchmark app actually runs it correctly. The work is gated on closing the neutral-buffer-seam leak (Principle 1 / §3.3), which Numba's `__cuda_array_interface__` arrays make both necessary and sufficient — and which simultaneously upgrades CuPy to a true first-class partner. Scope it to one demonstrating app and the ops it uses, ship a reference path for each, and hold the line that support is not a performance claim. That delivers "we really support Numba," demonstrated, without repeating the wide-surface-nobody-uses pattern or the support-equals-fast overclaim.
