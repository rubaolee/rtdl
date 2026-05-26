# Goal2621 3-AI Consensus: Bounded Contact-Witness COLLECT_K_BOUNDED Candidate

Date: 2026-05-25

Scope: review the bounded contact-witness/contact-manifold app candidate and
decide whether it preserves the generic `COLLECT_K_BOUNDED` primitive boundary.

## Reviewed Artifacts

- `examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
- `examples/v2_0/research_benchmarks/contact_manifold/README.md`
- `tests/goal2621_contact_manifold_collect_k_bounded_benchmark_candidate_test.py`
- `docs/reports/goal2621_bounded_contact_witness_collect_k_candidate_2026-05-25.md`
- `docs/rtdl_primitive_catalog.md`
- `docs/application_catalog.md`

## AI Inputs

- Codex implementation and local validation: accepted as benchmark candidate.
- Claude review:
  `docs/reports/goal2621_claude_bounded_contact_witness_review_2026-05-25.md`.
- Gemini review:
  `docs/reports/goal2621_gemini_bounded_contact_witness_review_2026-05-25.md`.

## Consensus

Accepted as a benchmark candidate only.

All three reviewers agree:

- The app exercises `COLLECT_K_BOUNDED` as a generic bounded `int64` witness-row
  collector.
- Collision/contact/manifold semantics remain in Python app code and
  documentation, not in native engine logic.
- Overflow behavior is exact fail-closed: no silent truncation and no partial
  row return on overflow.
- The current docs correctly avoid promoted benchmark wording and speedup
  wording.

## Promotion Decision

Promoted benchmark wording is not authorized yet.

Blocking gates:

- Local Mac Embree generic-collector parity is done for the same row schema and
  overflow contract; repeat on Linux if release evidence requires
  cross-platform coverage.
- OptiX parity on an NVIDIA RTX A5000 pod for the same row schema and overflow
  contract was added after this consensus:
  `docs/reports/goal2621_contact_manifold_optix_pod_evidence_2026-05-25.md`.
- Standalone C++ CPU baseline evidence was added after the first external
  reviews. A CUDA/BVH or physics-library baseline remains optional if feasible.
- A follow-up promotion consensus after the backend/baseline evidence exists.

## Post-Review Local Evidence

After the Claude and Gemini candidate reviews, Codex added a standalone non-RTDL
C++ exact triangle-pair baseline, local Mac Embree generic-collector parity, and
RTX A5000 OptiX generic-collector parity. These additions do not change the
candidate-only decision. A final promotion review should include the C++
baseline, Embree evidence, and pod OptiX evidence together.

## Required Fixes From Review

Claude noted that `--dataset overflow` could be surprising because overflow is
a capacity condition over the tiny fixture, not a separate scene. The app source
and README now state this explicitly.

No other required fixes were identified.

## Final Boundary

This consensus accepts the Goal2621 local candidate implementation and
documentation. It does not authorize stable `COLLECT_K_BOUNDED` promotion,
promoted benchmark wording, public performance claims, native collision/contact
engine logic, or release wording changes.

## Promotion Addendum

Date: 2026-05-25

After the candidate-only consensus, Codex added and recorded the missing
evidence:

- Pod OptiX evidence:
  `docs/reports/goal2621_contact_manifold_optix_pod_evidence_2026-05-25.md`
  and `.json`.
- Follow-up Claude review:
  `docs/reports/goal2621_claude_followup_promotion_review_2026-05-25.md`.
- Follow-up Gemini review:
  `docs/reports/goal2621_gemini_followup_promotion_review_2026-05-25.md`.

All three reviewers now accept the promotion.

Decision:

- `examples/v2_0/research_benchmarks/contact_manifold/` is promoted from
  benchmark candidate to promoted internal benchmark app.
- `COLLECT_K_BOUNDED` is promoted to stable primitive status.
- The promotion is limited to generic bounded `int64` row collection with exact
  fail-closed overflow semantics.
- Collision/contact/manifold semantics remain app-owned Python or external
  baseline code; no native collision/contact engine ABI is authorized.
- Linux Embree parity has not been separately recorded. This is documented as
  a qualification, not a blocker, because local Mac Embree parity and Linux
  RTX A5000 OptiX parity both validate the app-independent primitive contract.
- Public speedup claims remain unauthorized.

This addendum supersedes the candidate-only decision above for app/primitive
status only. It does not alter the no-speedup and no-domain-native-engine
boundaries.
