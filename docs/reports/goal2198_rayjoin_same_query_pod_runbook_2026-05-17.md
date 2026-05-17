# Goal2198 RayJoin Same-Query Pod Runbook

Date: 2026-05-17

Status: pod runner prepared; RTX execution still required.

## Purpose

Goal2188 proved that RayJoin itself can build and run on an RTX pod and that
RTDL can run bounded RayJoin-shaped PIP/LSI/overlay-seed workloads on the same
pod. Goal2192 added an RTDL same-query stream consumer. Goal2195 prepared the
external RayJoin patch that makes `query_exec` export its generated query
stream.

Goal2198 connects those pieces into one repeatable pod procedure:

1. clone RTDL from Git,
2. clone RayJoin at commit `02bf6220d6d20b04af77ee20364eced75cc029c9`,
3. install host dependencies without assuming Ubuntu provides `libnvtx3-dev`
   and use CUDA's `cuda-nvtx-<major>-<minor>` package when available,
4. apply the known RayJoin build-compatibility patches for current CUDA/OptiX
   pods,
5. apply the Goal2195 `-query_stream_output` export patch,
6. build RayJoin and RTDL Embree/OptiX,
7. run RayJoin `grid`, `lbvh`, and `rt` modes for generated PIP and LSI
   workloads,
8. feed the RayJoin-exported query streams to RTDL `cpu`, `embree`, and
   `optix` backends,
9. write a bounded summary artifact.

This is the next pod step toward a fair RayJoin comparison because RTDL no
longer consumes a different query protocol.

## Runner

Prepared script:

- `scripts/goal2198_rayjoin_same_query_pod_runner.sh`

Default command on an RTX pod:

```bash
bash scripts/goal2198_rayjoin_same_query_pod_runner.sh
```

Important environment knobs:

| Variable | Default | Meaning |
| --- | --- | --- |
| `WORK_DIR` | `/root/goal2198_rayjoin_same_query_pod` | Disposable clone/build workspace. |
| `OUT_DIR` | `$WORK_DIR/artifacts` | Progress logs, raw logs, streams, RTDL artifacts, and summary. |
| `RTDL_REPO` | `https://github.com/rubaolee/rtdl.git` | Source of the RTDL checkout to validate. |
| `RTDL_REF` | `main` | RTDL ref to fetch/reset in the disposable checkout. |
| `RAYJOIN_REPO` | `https://github.com/rubaolee/RayJoin.git` | External RayJoin repository. |
| `RAYJOIN_COMMIT` | `02bf6220d6d20b04af77ee20364eced75cc029c9` | RayJoin paper-code commit used by Goal2188/2195. |
| `OPTIX_PREFIX` | `/root/vendor/optix-sdk` | OptiX SDK header location. |
| `OPTIX_TAG` | `v8.0.0` | SDK tag cloned if headers are missing. |
| `CUDA_PREFIX` | auto-detected | Prefer `/usr/local/cuda-12.8`, then CUDA 12, then `/usr/local/cuda`. |
| `USE_PYTHON_VENV` | `1` | Create a local pod venv before pip installs, avoiding Ubuntu 24.04 PEP 668 system-Python blocking. |
| `VENV_DIR` | `$WORK_DIR/.venv` | Virtual environment path when `USE_PYTHON_VENV=1`. |
| `ALLOW_NON_CUDA12` | `0` | Fail closed if `nvcc` is not CUDA 12.x because the runner installs `cupy-cuda12x`; set to `1` only for manual debugging. |
| `GEN_N` | `100000` | Generated query count. |
| `GEN_T` | `0.1` | RayJoin generated-query size parameter. |
| `SEED` | `2184` | Query generator seed. |
| `WARMUP` | `1` | Warmup rounds for RayJoin and RTDL. |
| `REPEAT` | `3` | Measurement repeats for RayJoin and RTDL. |
| `STEP_TIMEOUT_SECONDS` | `1800` | Per-step timeout; set to `0` only for deliberate manual debugging. |

## Output Contract

The runner writes:

- `environment.txt`
- `progress.log`
- `rayjoin_lsi_grid.log`
- `rayjoin_lsi_lbvh.log`
- `rayjoin_lsi_rt.log`
- `rayjoin_pip_grid.log`
- `rayjoin_pip_lbvh.log`
- `rayjoin_pip_rt.log`
- `rayjoin_lsi_gen<GEN_N>_stream.json`
- `rayjoin_pip_gen<GEN_N>_stream.json`
- `rtdl_lsi_same_rayjoin_stream.json`
- `rtdl_pip_same_rayjoin_stream.json`
- `summary.json`

The RTDL artifacts must report:

- `query_stream_producer: rayjoin_query_exec_export_patch`
- `claim_boundary.same_contract_with_rayjoin_query_exec: true`
- parity for every requested RTDL backend against the declared reference backend

For local smoke tests the default reference remains `cpu_python_reference`.
For the 100k RayJoin pod stream, the runner uses `--reference-backend cpu`
because CPU Python all-pairs reference construction is intentionally not a
large-scale timing dependency.

The summary intentionally keeps these claim flags false:

- `paper_scale_perf_claim_authorized`
- `rtdl_beats_rayjoin_claim_authorized`
- `broad_rt_core_speedup_claim_authorized`
- `v2_0_release_authorized`

## Boundary

Goal2198 is still a runbook, not evidence, until it is executed on an RTX pod
and the resulting artifacts are copied back into `docs/reports/`.

Even after successful execution, the result should be interpreted narrowly:

- it can prove same-query stream ingestion and same-query RTDL timing for PIP
  and LSI;
- it does not prove full RayJoin paper reproduction;
- it does not prove RTDL beats RayJoin;
- it does not prove end-to-end overlay equivalence;
- it does not authorize a v2.0 release.

Those stronger claims require larger paper-matrix datasets, overlay contract
work, external review, and a separate consensus report.

## Review Follow-Up

Gemini's Goal2199 review accepted the runbook with one concrete boundary: the
runner originally installed `cupy-cuda12x` without an explicit CUDA-major guard.
The runner now parses `nvcc --version` and fails closed unless CUDA 12.x is
detected, or `ALLOW_NON_CUDA12=1` is set for manual debugging.

The first 2026-05-17 pod attempt also showed that Ubuntu 24.04 does not expose
`libnvtx3-dev` even though CUDA's `cuda-nvtx-12-8` package and `nvtx3` headers
are present. The runner no longer requires `libnvtx3-dev`; it installs the
matching CUDA NVTX package when available and otherwise relies on the CUDA
include tree.

The second 2026-05-17 pod attempt showed Ubuntu 24.04's PEP 668
`externally-managed-environment` guard blocking system-wide `pip` installs. The
runner now creates a local venv by default and installs Python packages there.

## Next Hardware Step

When an RTX pod is available:

```bash
git clone https://github.com/rubaolee/rtdl /root/rtdl_goal2198
cd /root/rtdl_goal2198
bash scripts/goal2198_rayjoin_same_query_pod_runner.sh
```

After completion, copy the output directory back and write the evidence report
from the raw artifacts.
