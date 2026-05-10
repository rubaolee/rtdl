# Goal1647 v1.6.x OptiX Collect-K Cooperative Capability Probe

## Verdict

`cooperative_launch_capability_recorded`

## Scope

- Git commit: `8403a85d06cfbef10d9e249159bac749b42b24e0`
- Library: `build/librtdl_optix.so`
- Host: `9744d9e86539`
- GPU summary: `NVIDIA RTX A4500, 570.195.03, 20470 MiB`

## Capability

- CUDA device index: `0`
- Cooperative launch supported: `True`
- Cooperative multi-device launch supported: `True`
- Multiprocessor count: `56`
- Max threads per block: `1024`
- Max shared memory per block opt-in: `101376`
- Next cooperative merge-chain probe allowed: `True`

## Claim Boundary

Goal1647 records cooperative-launch readiness for a future opt-in collect-k merge-chain diagnostic. It is not performance evidence, does not change fastest-candidate behavior, and does not authorize public speedup wording, stable COLLECT_K_BOUNDED promotion, broad RTX/GPU wording, release tags, or release action.
