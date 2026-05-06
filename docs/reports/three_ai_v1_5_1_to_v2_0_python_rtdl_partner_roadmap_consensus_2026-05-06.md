# 3-AI Consensus: RTDL v1.5.1-v2.0 Python+RTDL and Partner Roadmap - 2026-05-06

## Verdict

Consensus is reached.

RTDL should adopt the two-track roadmap:

```text
v1.5.1-v1.5.10: finish the first architecture track, Python + RTDL
v1.6: close and publish Python + RTDL as the first architecture milestone
v1.7-v2.0: build the second architecture track, Python + partner + RTDL
v2.0: close and publish Python + partner + RTDL if release gates pass
```

The core rule for all versions is unchanged: stable Embree and NVIDIA RT engine
paths should be app-generic. The native engine may know RTDL primitives, buffer
contracts, traversal contracts, and backend capabilities. It should not know app
names or app-specific business logic in stable primitive paths.

## Reviewed Artifacts

- Proposal:
  `docs/reports/v1_5_1_to_v2_0_python_rtdl_partner_roadmap_proposal_2026-05-06.md`
- Claude second-pass review:
  `docs/reports/claude_v1_5_1_to_v2_0_python_rtdl_partner_roadmap_rereview_2026-05-06.md`
- Claude final rereview:
  `docs/reports/claude_v1_5_1_to_v2_0_python_rtdl_partner_roadmap_final_rereview_2026-05-06.md`
- Gemini initial review:
  `docs/reports/gemini_v1_5_1_to_v2_0_python_rtdl_partner_roadmap_review_2026-05-06.md`
- Gemini second-pass review:
  `docs/reports/gemini_v1_5_1_to_v2_0_python_rtdl_partner_roadmap_rereview_2026-05-06.md`

## Consensus Positions

Codex accepts the revised roadmap because it creates a disciplined closure path
for Python+RTDL before opening the broader partner track. It also prevents
`COLLECT_K_BOUNDED`, zero-copy, partner integration, and app-generic engine
cleanup from being conflated into one unbounded milestone.

Claude accepts the final revised proposal as consensus-ready. Claude confirmed
that the prior required changes are satisfied: the Codex review anchor is
defined, v1.6 closure is explicitly classified as a key decision, v1.8 now has a
conformance baseline requirement, and the CUDA managed-memory caveat is
adequate.

Gemini accepts the revised proposal as a 3-AI consensus roadmap basis. Gemini
confirmed that the proposal adequately addresses external review definition,
partner baseline, v2.0 measurement, backend support policy, zero-copy claim
boundaries, semantic-version checkpointing, and `COLLECT_K_BOUNDED` bounds
testing.

## Execution Rules

- v1.5.1 should start with `COLLECT_K_BOUNDED` promotion as an app-generic
  primitive, not as a Jaccard-specific, polygon-specific, or app-specific engine
  path.
- v1.5.1 promotion requires fail-closed overflow semantics, exact bounds tests,
  Embree/OptiX parity where both are claimed, bounded result buffers, and
  benchmark evidence for exact claimed subpaths only.
- v1.5.2-v1.5.4 may develop result-buffer ABI, copy-reduction, and persistent
  buffer lifecycle work, but true zero-copy wording is allowed only for measured
  GPU-resident or externally shareable device-memory paths.
- v1.6 public closure is a key decision and requires Codex plus two independent
  external AI reviews, normally Claude and Gemini.
- v1.7 should begin the partner track with a DLPack-compatible tensor handoff
  and PyTorch or CuPy as the first practical consumer, rather than an open-ended
  partner menu.
- v2.0 public closure is a key decision and requires documented partner
  contracts, conformance evidence, exact measurement, and 3-AI consensus.

## Decision

Proceed to v1.5.1 under this consensus. The first implementation focus should
be a stable, app-generic `COLLECT_K_BOUNDED` contract and buffer shape for
Embree and OptiX, with Python remaining the app/control layer and native engines
remaining primitive-oriented rather than app-aware.
