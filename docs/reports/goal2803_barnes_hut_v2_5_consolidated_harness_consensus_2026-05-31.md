# Goal2803 Barnes-Hut v2.5 Consolidated Harness Consensus

Date: 2026-05-31

Verdict: accept-with-boundary.

## Consensus Basis

Goal2803 adds one canonical Barnes-Hut v2.5 consolidated harness for the current runtime. It covers:

- Embree versus OptiX expanded-membership aggregate-frontier lowering;
- Torch versus Triton grouped vector-sum partner continuation;
- same-contract membership parity;
- explicit OptiX RT-core evidence for the generic membership subpath;
- explicit blocking of Triton vector-sum auto-selection while Triton remains slower than the same-contract Torch/CuPy opponent.

## Distinct-AI Reviews

| Reviewer | File | Verdict | Boundary |
| --- | --- | --- | --- |
| Codex | `docs/reports/goal2803_barnes_hut_v2_5_consolidated_harness_2026-05-31.md` | accept-with-boundary | First evidence is live but the clean-from-Git pod rerun remains pending. |
| Claude | `docs/reviews/goal2803_claude_review_barnes_hut_consolidated_harness_2026-05-31.md` | accept-with-boundary | Requests clean-from-Git rerun with all default cases, three repeats, and at least two vector warmups. |
| Gemini | `docs/reviews/goal2803_gemini_review_barnes_hut_consolidated_harness_2026-05-31.md` | accept-with-boundary | Confirms live harness coverage, boundary wording, and pending clean-from-Git status. |

## Boundary

This consensus does not authorize:

- a public speedup claim;
- a whole-app speedup claim;
- a paper-reproduction claim;
- an authors-code comparison;
- a paper-level speedup claim;
- Triton vector-sum auto-selection;
- app-specific native engine logic.

The clean-from-Git rerun must preserve these boundaries and record source commit, source dirty status, GPU, cases, repeats, vector warmups, and the membership validation policy.
