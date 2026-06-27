# Goal4255 Claude Review: Goal4254 v2.10 Public Claim Wording Candidate

Date: 2026-06-09
Reviewer: Claude (Sonnet 4.6)
Verdict: **accept-with-boundary**

## Scope

Read-only review of:

- `docs/reports/goal4254_v2_10_public_claim_wording_candidate_2026-06-09.md`
- `docs/reports/goal4251_v2_10_internal_release_prep_packet_2026-06-09.md`
- `docs/reports/goal4248_current_public_docs_claim_boundary_scan_2026-06-09.md`
- `docs/reports/goal4249_major_performance_target_map_after_public_docs_scan_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`
- `tests/goal4254_v2_10_public_claim_wording_candidate_test.py`
- `tests/goal4251_v2_10_internal_release_prep_packet_test.py`
- `tests/goal4248_current_public_docs_claim_boundary_scan_test.py`
- `tests/goal4219_major_performance_target_map_test.py`

This is a wording review only. It does not authorize release.

---

## Q1: Is the candidate short description accurate for current v2.10 RTDL?

Largely yes. The description correctly identifies RTDL as a Python-hosted RT
DSL/runtime for non-graphical workloads, describes generic primitives, explicit
backend selection, and explicit partner composition. The native-engine
app-agnosticism statement is accurate and important.

**One wording concern:** The phrase "where a benchmark needs custom continuation
logic" implicitly restricts partners to benchmark contexts. Partners are a general
user-facing composition mechanism, not a benchmark-only feature. The short
description should not create the impression that partner use is benchmark-scoped.

Suggested fix (short description, last sentence of first paragraph):

> Current: "...compose the result with user-chosen Python partners such as Numba or
> CuPy where a benchmark needs custom continuation logic."
>
> Suggested: "...compose the result with user-chosen Python partners such as Numba or
> CuPy where custom continuation logic is needed."

All other aspects of the short description are accurate.

---

## Q2: Are all allowed claims scoped tightly enough to reviewed internal evidence?

Claims 1–5 and 7–10 are tightly scoped. Each either states an architectural
property verifiable in the source tree or cites a specific hardware pod and
evidence chain. The contract-split framing of claim 7 (RayJoin) and the
profile-aware framing of claim 8 (RT-DBSCAN) are well-calibrated and consistent
with Goal4218, Goal4239, and Goal4222.

**Claim 6 wording concern:** Claim 6 reads:

> "For selected RT-heavy contracts, reviewed artifacts show strong OptiX benefits
> over same-contract CPU or partner baselines."

The word "strong" is a quality superlative that is not anchored to a specific
magnitude, artifact reference, or comparison point. In the context of a release
wording candidate, an unanchored quality adjective creates the same overclaim
risk as unscoped speedup language. The claim is adequately scoped spatially
("selected RT-heavy contracts") but not in degree.

Suggested fix:

> "For selected RT-heavy contracts, reviewed artifacts show measured OptiX
> speedups over same-contract CPU or partner baselines."

The replacement drops "strong" and substitutes "measured" (which is verifiable
from the artifacts) for the quality assertion.

---

## Q3: Are all blocked claims explicit enough?

Yes. The ten blocked claims in the "Claims That Must Not Be Made" section
explicitly cover every category specified in the reviewer questions:

| Reviewer question category | Blocked claim present |
| --- | --- |
| Package install | #1: "released as a package-install product" |
| Universal speedup | #2: "every user program faster" |
| Broad RT-core speedup | #3: "broad RT-core speedup guarantee" |
| Whole-app acceleration | #4: "whole-application acceleration for every benchmark" |
| RayJoin superiority | #5: "RTDL beats RayJoin as a full paper system" |
| Paper reproduction | #6: "reproduces the full authors-code results of RayJoin, X-HD, RTNN, RT-DBSCAN, or other papers" |
| True zero-copy | #7: "general true-zero-copy product guarantee" |
| Automatic partner selection | #8: "automatically chooses the best backend or partner" |
| AMD/HIPRT | #9: "AMD/HIPRT performance evidence without an actual AMD hardware run" |
| App-specific native-engine logic | #10: "app-specific native-engine logic for benchmark apps" |

The blocked claim list is complete and phrased precisely. No omissions were found.

---

## Q4: Does the candidate front-page paragraph read clearly to learners without inviting overclaim?

The paragraph is direct and the negative boundary list at the end is
comprehensive. It does not invite overclaim.

Two wording observations for a learner audience:

**4a. Platform-specific shell invocation.** The paragraph opens with:

> "RTDL v2.10 is used from the source tree with `PYTHONPATH=src:.`."

The colon as `PATH` separator is a POSIX convention. On Windows the separator is
a semicolon. A learner on Windows who copies this verbatim will get a broken
environment. Since this is the first sentence of a learner-facing paragraph,
it either needs a platform note or should defer the invocation detail to the
README. Suggested alternatives:

> "RTDL v2.10 is used from the source tree (see README for platform setup)."

or, if the incantation must stay:

> "RTDL v2.10 is used from the source tree with `PYTHONPATH=src:.` (Linux/macOS)
> or `PYTHONPATH=src;.` (Windows)."

**4b. "Scoped by contract and artifact."** The sentence "keeps public claims
scoped by contract and artifact" uses the term "contract" without definition.
Learners who are new to RTDL may not know what a "contract" means in this
context. The term is well-defined internally but is jargon in a learner-facing
paragraph. Suggested softening:

> "keeps public performance claims scoped to specific workload contracts and
> reviewed timing artifacts."

This observation is lower priority than 4a; the existing sentence is not
incorrect, only slightly opaque.

---

## Q5: What exact wording must change before this can become part of a formal release packet?

Three changes are required; one is recommended but not required.

**Required (R1) — Claim 6, drop "strong":**

Current:
> "For selected RT-heavy contracts, reviewed artifacts show **strong** OptiX
> benefits over same-contract CPU or partner baselines."

Change to:
> "For selected RT-heavy contracts, reviewed artifacts show **measured** OptiX
> speedups over same-contract CPU or partner baselines."

Rationale: "strong" is an unanchored quality assertion. "Measured" points back
to the reviewed artifacts and does not assert degree.

**Required (R2) — Short description, partner scope:**

Current:
> "...user-chosen Python partners such as Numba or CuPy **where a benchmark
> needs** custom continuation logic."

Change to:
> "...user-chosen Python partners such as Numba or CuPy **where** custom
> continuation logic is needed."

Rationale: partners are a general user mechanism, not benchmark-scoped. The
current phrasing could mislead learners about when partner use is appropriate.

**Required (R3) — Front-page paragraph, platform-specific invocation:**

Current:
> "RTDL v2.10 is used from the source tree with `PYTHONPATH=src:.`."

Change to one of:
> "RTDL v2.10 is used from the source tree (see README for platform-specific
> setup)."

or:
> "RTDL v2.10 is used from the source tree with `PYTHONPATH=src:.` (Linux/macOS)
> or `PYTHONPATH=src;.` (Windows)."

Rationale: the colon-separator form will silently break on Windows. A
learner-facing paragraph must not ship a platform-specific incantation without
a platform qualifier.

**Recommended (not required) — Front-page paragraph, "contract" jargon:**

Replace "scoped by contract and artifact" with "scoped to specific workload
contracts and reviewed timing artifacts" for learner clarity. This is a
polish-level change; the current phrasing is not a hard blocker.

---

## Summary Assessment

The overall structure of Goal4254 is sound:

- All authorization flags remain false throughout the evidence chain.
- The blocked-claims list is complete and precisely phrased.
- The evidence base (Goal4235, Goal4239, Goal4243, Goal4248, Goal4249, Goal4250)
  is coherent and consistently referenced.
- The target-map dataclass enforces authorization flags at the Python level,
  providing a structural check independent of document wording.

The three required wording fixes (R1, R2, R3) are all surface-level changes.
None of them represent evidence gaps or structural claim failures. After those
three fixes are applied and pass re-review, this document is suitable to be
included in a formal release packet.

**Verdict: accept-with-boundary**

This document may become part of a formal release packet after the three
required wording fixes (R1, R2, R3) above are applied and reviewed. This review
does not authorize release.

---

## Boundary

This review does not authorize release, public speedup wording, whole-app
acceleration wording, broad RT-core wording, RTDL-beats-RayJoin wording,
paper-reproduction wording, package-install wording, true-zero-copy wording,
automatic partner/backend selection, AMD/HIPRT performance wording, or
app-specific native-engine logic.
