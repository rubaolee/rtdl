# Goal1478 v1.5.4 Device Memory Measurement Envelope

## Verdict

Added a design-time measurement envelope for v1.5.4 device-memory descriptors.

## What It Records

- Host-to-device transfer count
- Device-to-host transfer count
- Device residency observation
- Measurement backend
- Measurement scope
- Whether the observation came from real NVIDIA hardware

## Candidate Boundary

A device descriptor with observed residency, zero host/device transfer counts,
and real NVIDIA measurement can become a true-zero-copy evidence candidate.
That still does not authorize true zero-copy wording, public speedup wording,
whole-app claims, stable primitive promotion, partner tensor handoff, or release
action.

Host staging descriptors never become true-zero-copy candidates.

## Pod Boundary

No pod is required for this measurement envelope contract. A pod becomes
necessary when a real device path exists and the transfer/residency fields must
be populated from actual NVIDIA execution.

## Validation

Run:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1478_v1_5_4_device_memory_measurement_envelope_test
```
