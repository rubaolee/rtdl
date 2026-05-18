# v2.0 Pre-Release Candidate After Goal2086

Date: 2026-05-15

Status: `archived-pre-release-candidate`

This report is preserved as a historical checkpoint. It was superseded by the
Goal2319 cleanup packet, the Goal2320 Claude review, the Goal2321 Gemini
review, the Goal2322 final 3-AI consensus, and the
[v2.0 Release Package](v2_0/README.md).

## What Is Ready

The v2.0 engineering packet is ready for final consensus review:

- the RTDL native engine remains app-agnostic;
- the Python+partner path is protocol-first and keeps PyTorch/CuPy as partners,
  not engine ABI owners;
- all current OptiX/RT v1.8-vs-v2.0 evidence rows are filled;
- all 16 current OptiX/RT rows have measured v2/v1.8 ratios below `1.0` under
  their documented contracts;
- the old `segment_polygon_anyhit_rows` weak spot is superseded by the
  streaming exact witness-column contract;
- Embree remains bounded CPU same-contract evidence, not the headline GPU
  partner-speedup surface.

Primary packet:

- `docs/reports/goal2088_v2_0_release_prep_after_streaming_witness_2026-05-15.md`
- `docs/reports/goal2092_v2_0_release_consensus_gap_after_gemini_pro_2026-05-15.md`

## What Was Still Blocked At This Checkpoint

The final v2.0 release is blocked by governance, not by the current engineering
evidence:

- fresh Claude-family final review was missing;
- final post-Goal2086 3-AI consensus has not been written;
- no final v2.0 tag, publish step, or announcement should happen before that
  consensus exists.

Copilot review is useful supplemental signal, but it does not replace Claude
under the standing release rule unless the user explicitly changes that rule.

## Public Wording

Historical allowed wording:

- "v2.0 is a Python+partner+RTDL pre-release candidate."
- "The current OptiX/RT evidence table has 16/16 measured v2 rows faster than
  v1.8 under documented contracts."
- "The streaming exact witness-column contract replaces the old full Python
  witness-row output contract for the v2 segment/polygon any-hit row."

Still not allowed in the v2.0 release:

- "RTDL accelerates arbitrary PyTorch or CuPy programs."
- "RTDL provides broad RT-core acceleration."
- "RTDL supports package installation."
- "Every possible user program is faster."
- "Arbitrary polygon overlay is solved."

## Superseded Next Step

The required Claude/Gemini reviews and final consensus now exist in the
Goal2319-Goal2322 packet.
