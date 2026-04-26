# Goal589 Adaptive Engine Hold

Date: 2026-04-19

Status: HOLD

## Decision

Active development of the RTDL adaptive backend engine is paused. The adaptive engine remains a useful future performance path, but it is not required for the current release path because RTDL already has established RT backends:

- Embree
- OptiX
- Vulkan
- HIPRT
- CPU/Python correctness oracles

## Current State

The adaptive backend has already landed earlier bounded goals:

- Goal584: adaptive backend engine proposal and 3-AI consensus
- Goal585: adaptive runtime skeleton
- Goal586: native adaptive ray-triangle hit-count
- Goal587: native adaptive 2D segment intersection
- Goal588: native adaptive point-nearest-segment

Goal589 fixed-radius-neighbors work was started but is not closed, reviewed, or committed. It should not be treated as release evidence until resumed, tested, reviewed, and committed.

## Hold Rationale

The adaptive backend is RTDL-owned native optimization work rather than a vendor RT backend. It can be valuable during idle cycles, but the project currently has more important release-facing work around supported RT engines, public docs, tutorials, examples, and full validation.

## Resume Conditions

Resume Goal589 only when adaptive work is explicitly prioritized again. Before closure, it needs:

- correctness tests against the Python reference
- ordering parity for unsorted query IDs
- bounded performance smoke evidence
- Claude/Gemini review or equivalent 2+ AI consensus
- a clean commit that excludes unrelated Apple RT experiment files
