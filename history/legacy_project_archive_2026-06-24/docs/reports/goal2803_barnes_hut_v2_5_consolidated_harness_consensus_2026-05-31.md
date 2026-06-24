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
| Codex | `docs/reports/goal2803_barnes_hut_v2_5_consolidated_harness_2026-05-31.md` | accept-with-boundary | Clean-from-Git pod evidence is recorded at `60237c66`; public/paper/whole-app claims remain blocked. |
| Claude | `docs/reviews/goal2803_claude_review_barnes_hut_consolidated_harness_2026-05-31.md` | accept-with-boundary | Requested clean-from-Git rerun with all default cases, three repeats, and at least two vector warmups; this has now been satisfied by the clean artifact. |
| Gemini | `docs/reviews/goal2803_gemini_review_barnes_hut_consolidated_harness_2026-05-31.md` | accept-with-boundary | Confirms live harness coverage and boundary wording; clean validation was pending at review time and is now supplied by Codex evidence. |

## Clean Pod Evidence

| Field | Value |
| --- | --- |
| Commit | `60237c663c64b3322310817f0e0ece28e15e0f30` |
| Artifact | `docs/reports/goal2803_pod_artifacts/barnes_hut_v25_consolidated_harness_clean_from_git.json` |
| Status | `pass` |
| Source dirty | `[]` |
| GPU | `NVIDIA RTX A5000, 570.211.01` |
| Cases | `512:16`, `2048:32`, `8192:32` |
| Repeats | `3` |
| Vector warmups | `2` |
| Membership validation policy | `first_case_reference_validation_plus_all_case_embree_optix_shape_parity` |
| Max OptiX membership-wrapper speedup vs Embree | `154.324x` |
| Triton vector-sum status | Correct but `4.345x` slower than Torch; auto-selection remains blocked |

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
