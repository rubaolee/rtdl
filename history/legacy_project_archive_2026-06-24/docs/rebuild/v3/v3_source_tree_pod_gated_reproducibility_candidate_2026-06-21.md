# V3 Source-Tree / Pod-Gated Reproducibility Candidate

Status: `source_tree_pod_gated_candidate_reviewed_not_release`

This candidate describes the narrow reproducibility path that could support a
scoped Phoenix V3 release if a later release-scope review accepts that scope.
It has received external Claude review plus Codex consensus as a
source-tree/pod-gated candidate.

Candidate boundary: not a general release installer, not package-install wording, and not release authorization.

## Scope

This path is source-tree and RTX-pod gated:

- user starts from a checked-out RTDL source tree;
- user builds native Embree and OptiX libraries;
- user installs the staged Python GPU package set with an explicit experimental
  flag;
- user runs the Phoenix V3 gates and rerun commands from the source tree;
- performance evidence is scoped to the documented RTX pod class unless a later
  second-RTX packet or reviewed waiver changes that.

This is the candidate path for wording like:

```text
Phoenix V3 evidence is reproducible from the source tree on a documented RTX
pod environment.
```

This path does not authorize wording like:

```text
pip install rtdl gives a finished V3 GPU release.
V3 has a general installer.
V3 performance is confirmed across RT-core hardware.
Broad V3-over-V2 speedup is authorized.
```

## Required Commands

From the source tree:

```bash
export PYTHONPATH=src:.
```

Build native backends:

```bash
make build-embree
make build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0
```

Set runtime libraries:

```bash
export RTDL_OPTIX_LIBRARY=/path/to/current/build/librtdl_optix.so
export RTDL_OPTIX_LIB=$RTDL_OPTIX_LIBRARY
export RTDL_EMBREE_LIBRARY=/path/to/current/build/librtdl_embree.so
```

Replace `/path/to/current/build/` with the actual output path from
`make build-optix` and `make build-embree`.

Set the Numba CUDA compiler path before running the GPU partner gate:

```bash
export NUMBA_CUDA_PREFIX=/path/to/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc
export CUDA_HOME=$NUMBA_CUDA_PREFIX
export CUDA_PATH=$NUMBA_CUDA_PREFIX
export PATH=$NUMBA_CUDA_PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$NUMBA_CUDA_PREFIX/nvvm/lib64:/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:${LD_LIBRARY_PATH:-}
```

Replace `/path/to/.venv/` with the virtualenv path used on the pod. These
exports are required for `numba_cuda_jit: pass` in the GPU environment gate.

Install the staged Python GPU package set:

```bash
bash scripts/v3_install_gpu_pod_env.sh --accept-experimental-pod-gate
```

The `--accept-experimental-pod-gate` flag is required. It must remain visible
until a reviewed general release installer exists.

Run the GPU environment gate:

```bash
PYTHONPATH=src:. python scripts/v3_gpu_python_env_gate.py --pretty
```

Run the current Phoenix V3 release-safety gates:

```bash
PYTHONPATH=src:. python scripts/v3_release_wording_gate.py --pretty
PYTHONPATH=src:. python scripts/v3_phoenix_install_reproducibility_gate.py --pretty
PYTHONPATH=src:. python scripts/v3_phoenix_secondary_platform_gate.py --pretty
PYTHONPATH=src:. python scripts/v3_phoenix_next_engine_work_queue.py --pretty
PYTHONPATH=src:. python scripts/v3_phoenix_release_readiness_gate.py --pretty
```

Expected current release-readiness result:

```text
status: blocked_not_release
release_authorized: false
package_install_claim_authorized: false
general_release_installer_ready: false
release_scope: source_tree_pod_gated_twelve_row
source_tree_pod_gated_scoped_release_wording_reviewed: true
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row
```

## Package Set

The staged pod gate installs the current Phoenix GPU package set:

```text
torch==2.6.0+cu124
cupy-cuda12x==14.1.1
numba==0.65.1
nvidia-cuda-nvcc-cu12==12.4.131
nvidia-cuda-nvrtc-cu12==12.9.86
nvidia-cuda-runtime-cu12==12.9.79
```

The CUDA package set intentionally mixes `nvidia-cuda-nvcc-cu12==12.4.131`
with CUDA 12.9 NVRTC/runtime wheels because the tested Phoenix pod needed the
newer CuPy-compatible NVRTC/runtime wheels while preserving the Numba NVVM
toolchain path. Resolver warnings may appear; the gate result, not resolver
silence, is the evidence.

Known warning to preserve until resolved:

```text
cuda-bindings was built for CUDA major version 13, but the NVIDIA driver only
supports up to CUDA 12.
```

## Candidate-Level Non-Closure

This candidate by itself did not close the installer blocker because:

- its review covers candidate reproducibility, not release-scope acceptance;
- it is not a general package installer;
- it still requires an experimental pod-gate flag;
- it does not solve second RT-core hardware confirmation;
- it does not authorize broad V3-over-V2 speedup wording.

A later scoped release-wording review closed the installer blocker only under
`source_tree_pod_gated_twelve_row` scope. The current install gate reports:

```text
staged_pod_gate_present_general_release_installer_not_ready
source_tree_pod_gated_candidate_present: true
source_tree_pod_gated_candidate_reviewed: true
source_tree_pod_gated_scoped_release_wording_reviewed: true
release_scope: source_tree_pod_gated_twelve_row
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row
general_release_installer_ready: false
package_install_claim_authorized: false
release_authorized: false
```

## Done When

This candidate is reviewed as a source-tree/pod-gated reproducibility path. A
later 2-AI review accepted source-tree/pod-gated release scope for installer
closure only. A separate general release installer is still required before any
package-install wording.

Required closure evidence:

- explicit release-scope external review, not only candidate review;
- Codex consensus on that release scope;
- release docs explicitly state source-tree/pod-gated scope;
- release gate records a machine-readable scope decision;
- `installer_closes_release_blocker: true` only under the reviewed scope.

## Goal-Level Decision Audit

Decision: keep the source-tree/pod-gated reproducibility candidate reviewed and
record that later scoped release wording closed the installer blocker only
under `source_tree_pod_gated_twelve_row`.

1. Was I foolish?
   No. This records the reviewed reproducibility candidate and its later
   scoped installer closure while preserving the current blocked release state.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to call this candidate a general
   installer, hide the experimental pod gate, or treat scoped installer closure
   as release authorization.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. I could build a full package installer first, but that is a larger path
   and does not prevent us from documenting the current reproducible source-tree
   route honestly.
4. Can I now try a different path that actually solves the problem?
   Yes. Next, request aggregate release review that covers the scoped
   installer closure and the reviewed single-RTX hardware waiver.
