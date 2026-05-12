# Goal1772 Continuous Frechet OptiX Pod Validation Attempt

Date: 2026-05-12
Status: completed after installing compatible OptiX headers
Verdict: accept-with-boundary

## Scope

This report records the first hardware-side validation pass for the v1.8
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
repository HEAD for learner test: a1fc0c06
repository HEAD after OptiX identifier fix: 5a587f48
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

## Initial OptiX Runtime Blocker

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

## Remediation

The pod has full root access, so normal OS/package installation was possible.
OptiX itself was not available from the configured apt repositories, but NVIDIA
publishes a public header-only `optix-dev` repository. The headers were
installed on the pod at:

```text
/root/vendor/optix-dev
```

Using the default `optix-dev` `main`/`v9.1.0` headers built the RTDL OptiX
library, but runtime initialization failed with:

```text
RuntimeError: OptiX error: Unsupported ABI version
```

The cause was an ABI mismatch: `v9.1.0` reports `OPTIX_ABI_VERSION 118`, which
the pod's installed `570.195.03` driver rejected. Fetching the full
`optix-dev` tag set and pinning to `v9.0.0` produced
`OPTIX_ABI_VERSION 105`, which the driver accepted.

During the first compile attempt, `nvcc` also exposed a source-level OptiX
identifier regression from an earlier mechanical rename:

```text
struct shape-pair relationPipeline
struct shape-pair relationLaunchParams
```

Those invalid C++ identifiers were fixed in commit `5a587f48` by restoring
legal internal identifier names (`ShapePairRelationPipeline` and
`ShapePairRelationLaunchParams`) while leaving the native ABI app-agnostic.

## Build Evidence

Command:

```bash
cd /root/vendor/optix-dev
git fetch --unshallow --tags
git checkout -q v9.0.0

cd /root/rtdl
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev
```

Result:

```text
build/librtdl_optix.so
```

Export check:

```text
000000000004cc40 T rtdl_optix_run_segment_shape_anyhit_rows_native_bounded
```

## Passing RT-Core Path

Command:

```bash
RTDL_OPTIX_LIB=/root/rtdl/build/librtdl_optix.so \
PYTHONPATH=src:. \
python3 examples/rtdl_continuous_frechet_distance_app.py \
  --backend optix \
  --candidate-mode rtdl_broadphase \
  --require-rt-core \
  --iterations 8 \
  --decision-radius 0.25
```

Key output:

```json
{
  "app": "continuous_frechet_distance",
  "backend": "optix",
  "candidate_mode": "rtdl_broadphase",
  "decision": {
    "broadphase_row_count": 7,
    "candidate_cell_count": 7,
    "radius": 0.25,
    "within_radius": true
  },
  "distance_estimate": 0.20614200080478015,
  "free_space_cell_count": 9,
  "matches_oracle": true,
  "oracle_distance_estimate": 0.20614200080478015,
  "rt_core_accelerated": true
}
```

## Verdict

The continuous Frechet learner app now has pod-side OptiX execution evidence on
an RTX A5000. The claim remains deliberately bounded:

- RTDL/OptiX accelerates the segment/expanded-shape broadphase over candidate
  free-space cells.
- Python still owns the continuous Frechet free-space reachability algorithm,
  binary-search distance estimate, and JSON app assembly.
- This is not a whole-algorithm or universal speedup claim.

The infrastructure lesson is also clear: future pod runs should install
`NVIDIA/optix-dev` and pin it to `v9.0.0` for this driver family unless the
driver is upgraded to support newer OptiX ABI versions.
