# Goal 1486: CUDA Driver Allocation Probe

## Verdict

Probe status: `ok`.

This artifact records allocation evidence only. It does not authorize public zero-copy or speedup claims.

## Environment

- Commit: `92c601c3a58eb95decddadc2faecc56bc1b88bcd`
- Device: `NVIDIA RTX 4000 Ada Generation`
- CUDA driver version: `12040`

## Evidence

- Device allocation performed: `True`
- Device free performed: `True`
- Device pointer nonzero: `True`
- Host-to-device transfers: `0`
- Device-to-host transfers: `0`
- Device residency observed: `True`
- Measured on real NVIDIA: `True`
- True zero-copy evidence candidate: `True`

## Claim Boundary

Goal1486 records a CUDA Driver API cuMemAlloc/cuMemFree allocation probe for an RTDL-owned managed-buffer evidence envelope. A candidate result is not a public zero-copy claim and does not authorize public speedup wording, whole-app claims, stable primitive promotion, partner tensor handoff, or release action.
