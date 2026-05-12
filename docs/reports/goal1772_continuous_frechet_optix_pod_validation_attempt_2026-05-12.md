# Goal1772 Continuous Frechet OptiX Pod Validation Attempt

Date: 2026-05-12
Status: blocked by missing OptiX SDK/runtime library
Verdict: needs-more-evidence

## Scope

This report records the first hardware-side validation attempt for the v1.8
continuous Frechet Python+RTDL learner app added in Goal1771.

The claim-sensitive command under test is:

```bash
PYTHONPATH=src:. python3 examples/rtdl_continuous_frechet_distance_app.py --backend optix --candidate-mode rtdl_broadphase --require-rt-core --iterations 8 --decision-radius 0.25
```

The intended claim is narrow: NVIDIA RT cores may accelerate the RTDL
segment/expanded-shape broadphase that selects candidate free-space cells.
Python still owns the continuous Frechet free-space reachability decision and
binary-search distance estimate.

## Pod

Connection used the repo-local RTDL key:

```text
ssh root@194.68.245.162 -p 22077 -i id_ed25519_rtdl_codex
```

Observed hardware/software:

```text
hostname: 77877e3410d3
GPU: NVIDIA RTX A5000
driver: 570.195.03
Python: 3.11.10
CUDA: /usr/local/cuda-12.4/bin/nvcc present
repository HEAD: a1fc0c06
```

## Passing Portable Validation

The portable learner test passes on the pod:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1771_continuous_frechet_python_rtdl_learner_app_test

Ran 4 tests in 1.009s
OK
```

This validates the learner app, Python free-space logic, claim-boundary checks,
and non-OptiX compatibility on the pod.

## OptiX Runtime Blocker

The claim-sensitive OptiX command fails before hardware execution because the
RTDL OptiX native library is absent:

```text
FileNotFoundError: librtdl_optix not found. Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.
```

No `librtdl_optix.so` was found under `/root`, `/usr`, or `/opt`.

The canonical project build target also fails because the separate NVIDIA OptiX
SDK headers are not installed:

```text
make build-optix

mkdir -p build
RTDL OptiX SDK header not found at /opt/optix/include/optix.h
Set OPTIX_PREFIX to the OptiX SDK root, for example:
  make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev
make: *** [Makefile:193: build-optix] Error 1
```

Searches under `/root`, `/usr`, `/opt`, and `/usr/local` did not find
`optix.h`, `optix_stubs.h`, or `librtdl_optix.so`. `apt-cache search optix`
did not show an installable package in the pod's current package sources.

## Verdict

This pod is suitable for CUDA/NVIDIA hardware work, but it is not yet suitable
for RTDL OptiX validation because it lacks both:

- the RTDL-built `librtdl_optix.so`,
- the NVIDIA OptiX SDK header tree required to build that library.

The continuous Frechet app remains accepted as a Python+RTDL learner program.
The NVIDIA RT-core validation for this app remains blocked until a pod provides
either:

- a valid `RTDL_OPTIX_LIB=/path/to/librtdl_optix.so`, or
- the NVIDIA OptiX SDK at a known `OPTIX_PREFIX`, after which
  `make build-optix` can be run and the claim-sensitive command retried.
