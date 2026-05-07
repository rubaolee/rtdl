# Goal1477 v1.5.4 Device Memory Descriptor Contract

## Verdict

Added a design-time device memory descriptor contract for the v1.5.4
Python+RTDL device zero-copy lane.

## Descriptor Kinds

- `host_staging`: CPU host staging descriptor. This is reduced-copy or
  transfer-reuse plumbing, not true zero-copy.
- `device_resident`: Device pointer descriptor. This is an unmeasured zero-copy
  candidate only.
- `external_shareable_device`: Device pointer plus external handle descriptor.
  This is also an unmeasured zero-copy candidate only.

## Required Boundary

Device-resident descriptors require a non-null pointer and a non-CPU device.
External-shareable descriptors additionally require an external handle. Host
staging descriptors must use `device="cpu"` and remain `host_staging_reduced_copy`.

## Still Blocked

- True zero-copy claim
- Public speedup wording
- Whole-app speedup claim
- Stable public primitive promotion
- Partner tensor handoff claim
- Release action

## Pod Boundary

No pod is required for this descriptor contract. A pod becomes necessary only
after an implementation can measure device residency, transfer counts, or real
NVIDIA behavior.

## Validation

Run:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1477_v1_5_4_device_memory_descriptor_contract_test
```
