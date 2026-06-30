# Goal2584 Continuous Frechet GPU/CPU Baseline Results

Date: 2026-05-24
Status: pod-tested
Verdict: correct; demote Continuous Frechet to learner/demo app

## Purpose

Compare the attempted Continuous Frechet benchmark candidate against
same-contract CPU and GPU baselines on an NVIDIA pod before deciding whether it
deserves active benchmark status.

The user request was:

> compare our to gpu-version cft, if you cannot find one base, write one; also
> cpu one, find a tool for that, otherwise, write one; make sure correctness.

## Baselines Used

| Path | Implementation | Contract |
| --- | --- | --- |
| CPU C++ all-cells | Existing learner-owned C++ helper embedded in `rtdl_continuous_frechet_distance_app.py` | exact continuous Frechet binary-search estimate over all free-space cells |
| GPU CFT baseline | New Torch CUDA wavefront implementation in `scripts/goal2584_continuous_frechet_gpu_cpu_baselines.py` | same all-cells continuous Frechet decision/search contract |
| RTDL OptiX | Existing RTDL segment/expanded-shape broadphase plus learner-owned C++ continuation | RT-core broadphase and exact C++ continuation with pruning fallback |

I did not use a discrete Frechet GPU implementation as the GPU baseline because
that is a different contract. No usable same-contract external continuous
Frechet GPU implementation was available in the pod environment, so the GPU
baseline was written locally.

## Pod Environment

SSH command supplied:

```text
ssh root@69.30.85.177 -p 22184 -i ~/.ssh/id_ed25519
```

Actual working key on this Mac:

```text
~/.ssh/id_ed25519_rtdl_codex
```

Environment:

| Item | Value |
| --- | --- |
| GPU | NVIDIA RTX A5000 |
| Driver | 570.211.01 |
| Python | 3.12.3 |
| Torch | 2.8.0+cu128 |
| Torch CUDA | 12.8 |
| CUDA toolkit | `/usr/local/cuda-12.8` |
| OptiX SDK | `/root/vendor/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64` |
| RTDL OptiX library | `/root/rtdl_python_only/build/librtdl_optix.so` |

Build command:

```text
make build-optix OPTIX_PREFIX=/root/vendor/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64 CUDA_PREFIX=/usr/local/cuda-12.8 NVCC=/usr/local/cuda-12.8/bin/nvcc
```

Result:

```text
build/librtdl_optix.so
```

## Commands

Warmed repeated matrix:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_python_only/build/librtdl_optix.so \
python3 scripts/goal2584_continuous_frechet_gpu_cpu_baselines.py \
  --copies-list 8,16,32,64 \
  --iterations 8 \
  --repeats 3 \
  --warmups 1 \
  --output-json docs/reports/goal2584_continuous_frechet_pod_results_2026-05-24.json
```

Large probe:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_python_only/build/librtdl_optix.so \
python3 scripts/goal2584_continuous_frechet_gpu_cpu_baselines.py \
  --copies-list 128,256 \
  --iterations 8 \
  --repeats 1 \
  --warmups 0 \
  --output-json docs/reports/goal2584_continuous_frechet_pod_large_probe_2026-05-24.json
```

## Correctness

All rows matched the CPU C++ all-cells reference within `1e-5` relative/absolute
tolerance:

| Points per curve | Torch CUDA matches CPU C++ | RTDL OptiX matches CPU C++ |
| ---: | --- | --- |
| 32 | true | true |
| 64 | true | true |
| 128 | true | true |
| 256 | true | true |
| 512 | true | true |
| 1024 | true | true |

## Performance

Times are median seconds except the 512/1024 rows, which are single-run large
probes.

| Points per curve | Cells | CPU C++ all-cells | Torch CUDA all-cells | RTDL OptiX broadphase + C++ | RTDL / CPU speed | RTDL / Torch speed | Last RTDL prune |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | 961 | 0.003954 | 1.018416 | 0.055487 | 0.071x | 18.35x | 81.58% |
| 64 | 3,969 | 0.003312 | 2.018817 | 0.064186 | 0.052x | 31.45x | 89.19% |
| 128 | 16,129 | 0.008445 | 4.093519 | 0.146129 | 0.058x | 28.01x | 94.56% |
| 256 | 65,025 | 0.028264 | 8.281458 | 0.571836 | 0.049x | 14.48x | 96.79% |
| 512 | 261,121 | 0.107647 | 17.154918 | 3.160941 | 0.034x | 5.43x | 97.96% |
| 1024 | 1,046,529 | 0.418241 | 33.703798 | 12.268292 | 0.034x | 2.75x | 98.54% |

## Interpretation

The current RTDL OptiX path is correct and the broadphase is highly selective
on these authored fixtures, pruning `81.6%` to `98.5%` of cells after candidate
expansion. It also beats the locally written Torch CUDA all-cells wavefront
baseline by `2.75x` to `31.45x`.

However, it does not beat the optimized CPU C++ all-cells baseline. The CPU C++
path remains `14x` to `29x` faster than RTDL OptiX in these rows. The reason is
not correctness or candidate quality; it is execution structure:

- RTDL runs a separate OptiX broadphase per binary-search radius.
- The C++ continuation is invoked separately and uses file/process-style
  helper plumbing.
- Even with strong pruning, launch/orchestration cost dominates for these
  sizes.
- The Torch CUDA wavefront baseline is intentionally simple and same-contract,
  but it has high Python/diagonal-launch overhead, so it is not a strong GPU
  implementation.

## Conclusion

Continuous Frechet remains a valuable learner/demo app because it exposes a real
runtime/language gap:

- RTDL needs a compact mask or device-resident candidate output contract.
- The benchmark needs a batched many-trajectory-pair mode to amortize RT setup.
- A stronger GPU CFT path should fuse the wavefront continuation rather than
  launching per diagonal from Python.
- The current RTDL OptiX broadphase plus C++ continuation should not be used for
  public speedup wording.
- The app should not be listed as an active research benchmark.

Claim allowed:

```text
RTDL can correctly express a generic RT-core broadphase for continuous Frechet
free-space cells and can outperform a simple same-contract Torch CUDA all-cells
wavefront baseline, but the current implementation is still slower than the
optimized CPU C++ all-cells reference.
```

Claim not allowed:

```text
RTDL accelerates continuous Frechet distance over optimized CPU code.
```

Benchmark-app decision:

```text
Demote Continuous Frechet from benchmark-app consideration. Keep it as a
learner/demo app and lesson artifact.
```

## Local Validation

After copying pod JSON evidence back to the Mac:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal2584_continuous_frechet_gpu_cpu_baseline_results_test

Ran 3 tests in 0.000s
OK
```

Current post-demotion compatibility checks:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal2584_continuous_frechet_gpu_cpu_baseline_results_test tests.goal1771_continuous_frechet_python_rtdl_learner_app_test

Ran 5 tests
OK
```
