# Iteration 2 Final Consensus

Date: `2026-03-31`
Author: `Codex`

## Outcome

The Goal 14 estimation has been refined with concrete one-hour profiles, and Gemini accepted the update by consensus.

## Accepted One-Hour Profiles

- `lsi`
  - fixed `R = 1,000,000`
  - varying `S = 1,000,000, 2,000,000, 3,000,000, 4,000,000, 5,000,000`
  - estimated total query-only time: about `0.91 h`

- `pip`
  - fixed `R = 1,000,000`
  - varying `S = 20,000, 40,000, 60,000, 80,000, 100,000`
  - estimated total query-only time: about `1.00 h`

## Interpretation

These are still estimation-phase recommendations, not completion claims for a full exact-scale paper reproduction.

The key point is:

- `pip` must be scaled down substantially on the current Mac to fit a one-hour budget,
- while `lsi` can stay much closer to the paper's original probe scale if the build side is reduced,
- and both recommendations remain bounded by the same current RTDL limitation: Python-side materialization before Embree execution.
