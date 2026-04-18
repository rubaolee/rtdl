# Goal 517: Claude Review

Date: 2026-04-17

Reviewer: Claude Sonnet 4.6 (external AI review)

Verdict: **APPROVED**

## The Bounded Claim

The handoff asks whether Goal517 correctly documents the bounded claim that ITRE is sufficient for the RTDL-owned kernel parts of the v0.8 apps while Python remains the application layer.

It does. The documentation is precise, internally consistent, and does not overreach.

## What Is Done Well

**The boundary is explicit and honest.** `itre_app_model.md` states in bold: "RTDL does **not** claim that ITRE alone is a complete application language." The RTDL-owns / Python-owns split is itemized concretely, not left implicit. The intended app shape (`Python prepares → RTDL emits rows → Python reduces`) is stated as a design position, not a limitation to apologize for.

**The three app mappings are correct in structure.** Each app is decomposed into Input/Traverse/Refine/Emit/Python columns. The Hausdorff and collision-screening cases are clean fits. The Barnes-Hut case is correctly identified as the strongest language-pressure example, and the doc honestly says ITRE covers "only the first bounded candidate-generation part" — not the full app. That is the right call.

**Future pressure is recorded without being laundered into current claims.** Tree-node input types, opening predicates, grouped vector reductions, and iterative multi-stage orchestration are listed as future growth areas, not as v0.8 capabilities.

**The "What This Does Not Prove" section is appropriately conservative.** It explicitly disclaims that RTDL is a full app language, that it replaces Python, or that every workload is covered. The final summary sentence is tightly scoped to "the current v0.8 target apps."

## Test Coverage Assessment

The test file (`goal517_itre_app_model_doc_test.py`) checks:
- All four ITRE phases are named.
- The explicit non-claim about being a complete app language is present.
- All three apps are documented.
- Key future-pressure terms are present.
- The doc is linked from all four public entry points.

These are structural content tests, appropriate for documentation goals. They are sufficient to prevent silent regression of the key assertions.

## Minor Observations (non-blocking)

- The test checks for `"Python owns the app"` as a substring, which is present. No concern.
- The Barnes-Hut section says "ITRE is only enough for the first bounded candidate-generation part" — this phrasing is honest but slightly asymmetric with the summary table, which says "body and node inputs become candidate interaction rows." Both are accurate; they describe the same thing at different levels of detail.
- The doc does not include a timestamp or version tag, which is fine given the tutorial and architecture docs link to it by filename.

## Conclusion

Goal517 correctly documents the bounded claim. The primary assertion — ITRE is sufficient for the RTDL-owned kernel parts of the v0.8 target apps, with Python owning the application layer — is supported by the three app mappings, the explicit ownership split, the honest Barnes-Hut caveat, and the "What This Does Not Prove" section. The claim is defensible and the documentation does not overstate it.

Goal517 is ready to close.
