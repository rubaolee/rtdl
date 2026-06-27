# Phoenix V3 Barnes-Hut Runner Parity Focused POD A/B

Status: `barnes_hut_runner_parity_pod_ab_collected_not_release`.

- body counts: `[32768, 65536, 131072]`
- repeat/warmup/samples: `11` / `3` / `5`
- runner vs existing fused-control geomean: `0.999328063165968`
- historical OptiX over runner geomean: `12.730691398985789`
- runner parity with existing fused partner: `True`
- step-1 replacement candidate: `True`

The primary control is the existing app-front-door fused Numba CUDA route.
The prepared OptiX frontier route is included only as a historical no-go reference.
This packet authorizes no release, broad V3-over-V2 wording, true-zero-copy wording,
wrapper-is-faster wording, or all-app rerun.
