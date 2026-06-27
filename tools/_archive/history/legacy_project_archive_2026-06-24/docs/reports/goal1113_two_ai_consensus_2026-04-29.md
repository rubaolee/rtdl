# Goal1113 Two-AI Consensus

Date: 2026-04-29

Verdict: ACCEPT

## Scope

Goal1113 formalizes split Robot Embree validation/timing baseline collection.

## Consensus

Codex verdict: ACCEPT.

Second-AI reviewer verdict: ACCEPT.

Consensus conclusion: the split runner/intake contract is ready for Linux execution.

## Contract

- Validated chunks: `chunk_<index>.json`
- Split validation chunks: `validation_chunk_<index>.json`
- Timing-only chunks: `timing_chunk_<index>.json`
- Timing-only runner mode: `RTDL_GOAL1085_TIMING_ONLY=1`
- Timing-only artifacts must use `status: timing_only` and `correctness_parity: null`
- Intake accepts either legacy all-validated chunks or split validation/timing chunks
- Split mode allows smaller validation chunks; it does not require one full 200k-pose CPU-oracle validation chunk

## Boundary

This goal does not authorize public RTX speedup claims. A complete Robot baseline still requires actual chunk execution, intake, and another 2+ AI review.
