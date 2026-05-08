# Goal 1492: COLLECT_K_BOUNDED Device-Buffer Execution Packet

## Verdict

Prepared as a replayable packet. It is blocked on the current pod until Goal 1489 preflight is green.

## Fixture

- Candidate rows: `((2, 20), (1, 10), (2, 20), (3, 30))`
- Row width: `2`
- Capacity: `3`

## Expected Reference

- Valid count: `3`
- Overflowed: `False`
- Candidate rows: `((1, 10), (2, 20), (3, 30))`

## Required Device-Buffer Execution

- Backend: `optix`
- Symbol: `rtdl_optix_collect_k_bounded_i64`
- Must run on real NVIDIA hardware after Goal 1489 preflight is green.

## Claim Boundary

Goal1492 prepares a replayable COLLECT_K_BOUNDED device-buffer execution packet only. It does not run OptiX, does not prove true zero-copy, and does not authorize public speedup wording, whole-app claims, partner tensor handoff, or release action.
