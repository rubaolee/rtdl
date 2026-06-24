# Claude Review: Goal4390 v2.14 App-Author Implementation Strategy

Date: 2026-06-15

Reviewer: Claude (Sonnet 4.6)

Primary document reviewed: `docs/learn/v2_14_app_author_implementation_strategy.md`

Supporting documents consulted:
- `docs/release_reports/v2_14/public_rt_vs_embree_comparison.md`
- `docs/release_reports/v2_14/public_wording_boundaries.md`
- `docs/learn/benchmark_partner_reference_matrix.md`
- `docs/reports/goal4389_rtdbscan_partner_dual_implementation_2026-06-15.md`

---

Verdict: **accept-with-boundary**

The document is structurally correct and enforces all four core design principles. It requires fixes in three narrow areas before it can join the v2.14 public release packet without risk of misuse. None of the fixes require structural changes.

---

## Findings

### F1 — Primitive-first design: PASS

Step 1 correctly identifies the RT-shaped kernel as the starting point. The decision table opens with "Can an RTDL primitive directly express the answer? Use the primitive and stop there." Step 1 warns explicitly: "do not add a partner just because a GPU array library is available." Step 7 distinguishes good primitive candidates from bad app-specific ones. The primitive-first framing is consistent throughout the seven steps. No overclaim or bypass opportunity found.

### F2 — Explicit partner selection: PASS

Step 4 makes the primitive-vs-partner split visible per benchmark row. Step 5 presents each partner as a user choice with explicit conditions, not an automatic selection. The five-point requirement at the end of Step 5 correctly mandates both the current best-performance partner and a same-contract Numba reference. The blocked wording template explicitly forbids "RTDL automatically chooses the best partner." No implicit auto-selection language was found.

### F3 — Same-contract OptiX-vs-Embree comparison discipline: PASS

The comparison rule in Step 2 is complete and strict: same app row, same primitive contract, same output surface, same partner policy, same data, clear timing protocol. Step 3 explicitly forbids cold-vs-hot cross-backend comparisons. The decision table also blocks comparisons where routes differ in contract, partner, output, or timing basis. These rules are consistent with `public_rt_vs_embree_comparison.md`'s required interpretation rules.

### F4 — No-arbitrary-OptiX-callback user API boundary: PASS

The dedicated section "Why v2.14 Does Not Expose Raw OptiX Callback APIs" is technically honest. The four reasons cover: (1) callback breaks same-contract comparison without an equivalent CPU contract, (2) ABI/memory-ownership/compilation safety, (3) pushes users back toward one-off C++/CUDA/OptiX, (4) benchmark claims become ambiguous. The preferred pattern (custom OptiX program internally implements a generic RTDL primitive → stable app-agnostic contract → apps compose explicitly) is correctly stated. The decision table guards against this at the query level.

### F5 — RTDBSCAN: backend comparison and partner comparison conflated in Step 4 (BOUNDARY GAP)

Step 4's RTDBSCAN row names primitive contribution as "Fixed-radius count threshold / core flags" and partner contribution as "Component labeling or convergence." This is accurate but does not distinguish two separate claims that the supporting evidence separates cleanly:

- Backend comparison (OptiX vs Embree): requires fixed Numba continuation as the same-contract lock. Result at 524K: 1.05x total, 1.37x threshold stage.
- Partner comparison (Numba vs CuPy): measures both on the same RT-flag base. Result at 524K: RT+Numba 8.900s vs RT+CuPy 10.662s, Numba advantage 1.20x.

An app author using Step 4 as a quick reference might think CuPy is an equally valid backend-comparison continuation. The benchmark lessons table at the bottom correctly says Numba is currently the best measured partner, but it does not say that fixed Numba continuation is the required same-contract lock for the backend row. The strategy document needs a one-sentence inline note in Step 4 or Step 5 making this separation explicit.

### F6 — RTDBSCAN narrow-engineering-row status not stated in the strategy document (BOUNDARY GAP)

`public_rt_vs_embree_comparison.md` marks the RTDBSCAN row "ready only as narrow engineering row." It also provides the phase explanation: at 524K, Numba continuation is 6.917s and the RT threshold stage is 1.181s of the 8.900s total, meaning the app is continuation-dominated and the RT-core contribution does not produce a large full-app speedup. The strategy document's benchmark lessons row only says "RT threshold helps, but component continuation can dominate." This understates the actual ratio. An app author who does not read the public comparison matrix will not understand that the backend comparison result is 1.05x total, not a large speedup. One explicit sentence is needed.

### F7 — RayJoin overlay Step 4 row lacks an inline 2/8 caveat (BOUNDARY GAP)

Step 4's table lists "RayJoin overlay | LSI, vertex/midpoint point-location, PIP traversal, and output orchestration | Topology and output assembly." This is accurate about the primitive-partner split but does not warn the user about the 2/8 exact-subset constraint. The benchmark lessons table correctly states "The available 2/8 exact Section 5.7 subset is public-review-ready, but full 8/8 reproduction remains blocked," but a user consulting Step 4's table as a quick reference will not see this warning inline. At minimum the Step 4 row should include a note field or parenthetical that points to the 2/8 boundary.

### F8 — Step 5 C++/CUDA/OptiX entry: anti-overclaim language is present but soft (MINOR)

Step 5 notes for specialized C++/CUDA/OptiX: "Valid as an external specialized baseline, but not the default RTDL language strategy." This is technically correct but "valid as external baseline" could be read as authorization to compare RTDL primitives against specialized implementations and claim a speedup. The blocked wording in the handoff requirements explicitly forbids "RTDL beats handwritten C++/CUDA/OptiX claims." The note should add: "Do not use this path to claim RTDL primitive performance exceeds a specialized implementation."

### F9 — Strengths worth preserving

- The public wording template (Allowed vs Blocked) is precise and complete. All four overclaim categories from the handoff are blocked.
- Step 3's prepared execution protocol is correctly structured and explicitly forbids hiding scene build inside a hot-query number.
- Step 6's pipeline composition model correctly keeps app policy in the app and native engine semantics app-agnostic.
- Step 7's list of bad primitive candidates explicitly names the five app-specific antipatterns.
- The status disclaimer at the top of the document ("This is not a release tag, automatic optimizer promise, whole-app speedup claim, or raw OptiX callback API proposal") correctly scopes the document before the user reads a single step.

---

## Required Fixes Before Public Release

**Fix 1 (Step 4 RTDBSCAN row):** Add an inline note distinguishing the backend comparison lock (fixed Numba continuation, result 1.05x total at 524K) from the partner comparison evidence (Numba 1.20x faster than CuPy at 524K per Goal4389). Suggested wording in a Notes column or parenthetical: "For OptiX-vs-Embree backend comparison, fix Numba as continuation; for partner comparison, Goal4389 shows Numba is current large-scale winner over same-contract CuPy. These are two separate claims."

**Fix 2 (Benchmark lessons RTDBSCAN row):** Replace the current summary "RT threshold helps, but component continuation can dominate; Numba is currently the best measured prepared-grid partner for the 524K contract" with a version that includes the continuation-dominance ratio: "RT threshold helps, but at 524K the continuation phase is ~6.9s and the RT threshold stage is ~1.2s of an 8.9s total; public wording must stay narrow (narrow engineering row, not large full-app speedup)."

**Fix 3 (Step 4 RayJoin overlay row):** Add a note field or parenthetical: "Overlay claims are limited to the available 2/8 exact Section 5.7 CDB subset; full 8/8 reproduction is blocked."

**Fix 4 (Step 5 C++/CUDA/OptiX entry):** Extend the Notes cell to explicitly say: "Do not claim RTDL primitive performance exceeds a specialized implementation; cite only as an external baseline."

---

## Suggestions

1. Consider adding a "Status scope" callout box near the benchmark lessons table that lists the three v2.14 narrow rows (RTDBSCAN as narrow engineering row, RayJoin PIP as modest-only, RayJoin overlay as 2/8-subset only) so users do not need to consult the public comparison matrix to learn the scope of each row.

2. The final checklist does not include "the backend comparison partner lock (if any)" as a required item. Given that RTDBSCAN backend comparison requires fixed Numba continuation, adding "the fixed partner used for backend comparison, if backend comparison is claimed" to the checklist would prevent a class of honest errors.

3. The decision table could add a row: "Does the OptiX-vs-Embree comparison fix the same partner for both backends? (If not, do not publish as a backend comparison.)" This is implied by the comparison rule in Step 2 but a decision-table row makes it actionable for a first-time reader.

---

## Residual Risks

1. A user who reads only Steps 1–5 and skips the benchmark lessons table will not learn the RTDBSCAN continuation-dominance ratio. The required fix (Fix 2) mitigates this but does not fully close it; linking the benchmark lessons table from the Step 4 RTDBSCAN row would also help.

2. The document does not reference Goal4389 by name in the body, only implicitly through the benchmark lessons summary. If the public release packet is consulted without access to the supporting reports, the partner comparison evidence base is not traceable from the strategy document alone. Suggest adding a citation row to the See Also section: `Goal4389 RTDBSCAN Partner Dual Implementation Supplement`.

3. The public wording template's Allowed example uses RTDBSCAN as the positive case. If this template is used verbatim without reading Fix 2's narrow-row clarification, a user might apply it to make a broader RTDBSCAN speedup claim. Fix 1 and Fix 2 together reduce this risk to acceptable levels but do not eliminate it entirely without a more explicit "narrow engineering row" label adjacent to the template.
