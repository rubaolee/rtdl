# Goal2596 GPU-RMQ Expensive Pod Negative Result

Date: 2026-05-24

## Purpose

Qualify the expensive pod for the missing GPU-RMQ author-code RT/OptiX
comparison. The previous RTX A5000 pod could build CUDA-only author paths but
could not run the authors' OptiX hit-object paths because OptiX 8.1 failed at
runtime with an unsupported ABI error.

## Pod

- User-provided command: `ssh root@213.173.103.218 -p 48630 -i ~/.ssh/id_ed25519`
- Actual working key on this Mac: `~/.ssh/id_ed25519_rtdl_codex`
- Hostname: `0abb82543b1c`
- GPU: NVIDIA GeForce RTX 5090
- Driver: `580.159.03`
- GPU memory: `32607 MiB`
- Initial CUDA: `13.0`
- Installed for author build: CUDA 12.9 compiler/runtime headers, cuRAND dev
- OptiX SDK: local `NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64-35015278.sh`
- Author repo: `https://github.com/lakreis/GPU-RMQ`
- Author commit: `86fed1c170b7e41e8ec44e461f7220f87f492893`
- HRMQ commit: `e2a54bd193faf98e4325a494ae9315373d86b23c`

## Build Outcome

The authors' code built only after switching from CUDA 13.0 to CUDA 12.9.

- CUDA 13.0 build failed during PTX assembly with unresolved OptiX hit-object
  symbols such as `_optix_hitobject_traverse`.
- CUDA 12.9 build succeeded after installing `libcurand-dev-12-9`.

This confirms the authors' CUDA 12.9 requirement is material for this code.

## Checked Runtime Outcome

Smoke workload:

```text
n=1,048,576
q=65,536
lr=-1 and lr=-3
algorithms=2,5,16,18,19,20,21,24
check mode=--randTrivialCheck
```

Usable CUDA-only author rows passed:

- `alg=2` GPU base
- `alg=16` GPU-RMQ XXX
- `alg=19` interleaved CUDA
- `alg=20` basic vector load
- `alg=24` XXX multi load

RT/OptiX rows were not usable:

- `alg=5` RTX_blocks returned exit code 0 but emitted OptiX `Invalid value`
  errors, returned zero-valued RMQ outputs, and failed random trivial checking
  with `checkResult=4`.
- `alg=18` segfaulted for both `lr=-1` and `lr=-3`.
- `alg=21` segfaulted for both `lr=-1` and `lr=-3`.

Artifacts:

- `docs/reports/goal2596_gpu_rmq_expensive_pod_artifacts/goal2596_expensive_author_smoke_checked.csv`
- `docs/reports/goal2596_gpu_rmq_expensive_pod_artifacts/goal2596_expensive_author_smoke_checked.log`

## Conclusion

This pod should not be used for further GPU-RMQ author RT/OptiX benchmarking.
It is powerful enough, but the author RT paths are not producing valid checked
results on RTX 5090 with OptiX 8.1/CUDA 12.9.

The likely practical reason is a compatibility boundary between the authors'
OptiX 8 hit-object code, OptiX SDK 8.1, and RTX 5090/Blackwell behavior. Since
we do not have an OptiX SDK newer than 8.1 locally, continuing on this pod would
mainly burn budget without producing publishable author RT evidence.

## Next Pod Requirement

For author RT comparison, prefer a pod with:

- RTX 4090, RTX 6000 Ada, A6000 Ada, L40S, or another pre-Blackwell RTX GPU.
- New enough driver to avoid the previous `Unsupported ABI version` failure.
- CUDA 12.9 available or installable.
- OptiX SDK 8.1 supplied from local Downloads.

If only RTX 5090 pods are available, we should skip author RT rows unless the
user can provide an OptiX SDK version that explicitly supports RTX 50-series
hit-object paths.
