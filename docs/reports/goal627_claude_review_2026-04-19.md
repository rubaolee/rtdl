# Goal 627 Claude Review

Date: 2026-04-19

Reviewer: Claude Sonnet 4.6

## Verdict: ACCEPT

No required fixes.

## Basis

**Honesty check: pass.**

The response correctly handles the external large-scale numbers (OptiX 46.2s / Vulkan 46.5s / HIPRT 51.9s on DB scan; HIPRT `std::bad_alloc` on large BFS) as external input to document and bound, not as a new canonical benchmark artifact. It does not misrepresent what those numbers prove or disprove.

**Sufficiency check: pass.**

Both updated documents now carry the required boundary language:

- `backend_maturity.md` "Linux GPU Performance Notes" section accurately records the large-scale result, draws the correct Vulkan-as-serious-GPU-path conclusion, retains HIPRT as correctness/API coverage only, and explicitly prohibits HIPRT AMD GPU claims.
- `support_matrix.md` "Performance Boundary" section closes with the same signal as a critical scaling note, blocking any future HIPRT memory-scalable or performance-leading claim for graph workloads.

The external blocker cross-check (20 tests, OK) is correctly handled: not reproduced locally, flagged as external-machine findings, not dismissed.

**Non-overclaiming check: pass.**

The response does not:
- promote the external numbers to canonical benchmark status
- drop any backend based on this data alone
- present HIPRT-on-CUDA/NVIDIA as AMD GPU evidence
- claim Vulkan beats OptiX (reports near-parity, correct)
- weaken the existing v0.9.4 correctness or release status

The engineering conclusions (prioritize Vulkan for performance, retain OptiX as NVIDIA-specific RT backend, keep HIPRT correctness-only until AMD hardware and large-graph memory are validated, require chunked/prepared execution before broad DB/graph throughput claims) are the correct conservative response to the evidence presented.

## No Fixes Required
