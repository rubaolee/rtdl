# Goal1647 v1.6.x OptiX Collect-K Cooperative Capability Probe

## Verdict

`cooperative_launch_capability_recorded`

## Scope

- Git commit: `1bbf095293a180ccee0687858ae2c306be3b0b63`
- Library: `build/librtdl_optix.so`
- Host: `lx1`
- GPU summary: `NVIDIA GeForce GTX 1070, 580.126.09, 8192 MiB`

## Capability

- CUDA device index: `0`
- Cooperative launch supported: `True`
- Cooperative multi-device launch supported: `True`
- Multiprocessor count: `16`
- Max threads per block: `1024`
- Max shared memory per block opt-in: `49152`
- Next cooperative merge-chain probe allowed: `True`

## Claim Boundary

Goal1647 records cooperative-launch readiness for a future opt-in collect-k merge-chain diagnostic. It is not performance evidence, does not change fastest-candidate behavior, and does not authorize public speedup wording, stable COLLECT_K_BOUNDED promotion, broad RTX/GPU wording, release tags, or release action.
