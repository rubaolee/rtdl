# Goal 1487: CUDA Driver Copy Boundary Probe

## Verdict

Probe status: `ok`.

This artifact records explicit content-copy evidence. It is not true-zero-copy evidence.

## Environment

- Commit: `20d8553db865885fad75c6737fe221125b137d1c`
- Device: `NVIDIA RTX 4000 Ada Generation`
- CUDA driver version: `12040`

## Evidence

- Device allocation performed: `True`
- Device free performed: `True`
- Device pointer nonzero: `True`
- Host-to-device transfers: `1`
- Device-to-host transfers: `1`
- Device residency observed: `True`
- Measured on real NVIDIA: `True`
- Content roundtrip verified: `True`
- True zero-copy evidence candidate: `False`

## Claim Boundary

Goal1487 records a CUDA Driver API host-to-device and device-to-host copy-boundary probe for RTDL-shaped int64 rows. Because content movement performs explicit copies, this is not a true zero-copy evidence candidate. It does not authorize public speedup wording, whole-app claims, stable primitive promotion, partner tensor handoff, or release action.
