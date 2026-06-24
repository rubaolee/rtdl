# Codex Consensus: Phoenix V3 Source-Tree / Pod-Gated Reproducibility Candidate

Date: 2026-06-21

Status:
`claude_codex_consensus_source_tree_pod_gated_candidate_reviewed_not_release`

External review:
`docs/reviews/claude_phoenix_v3_source_tree_pod_gated_reproducibility_candidate_review_2026-06-21.md`

Claude verdict: `approve-with-amendments-not-release`

Codex verdict: accept Claude's candidate-level approval after applying the P0
amendment. This consensus does not authorize release.

## Decision

The Phoenix V3 source-tree / pod-gated reproducibility candidate may be marked:

```text
source_tree_pod_gated_candidate_reviewed: true
```

The following fields must remain unchanged:

```text
general_release_installer_ready: false
package_install_claim_authorized: false
installer_closes_release_blocker: false
release_authorized: false
```

The install gate status must remain:

```text
staged_pod_gate_present_general_release_installer_not_ready
```

## Amendments Applied

Claude required one P0 amendment before the candidate could be marked reviewed:
the candidate had to include the Numba CUDA compiler-path exports needed for
`numba_cuda_jit: pass` in the GPU environment gate.

That amendment is now present in:

```text
docs/rebuild/v3/v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md
```

The candidate now documents:

```bash
export NUMBA_CUDA_PREFIX=/path/to/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc
export CUDA_HOME=$NUMBA_CUDA_PREFIX
export CUDA_PATH=$NUMBA_CUDA_PREFIX
export PATH=$NUMBA_CUDA_PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$NUMBA_CUDA_PREFIX/nvvm/lib64:/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:${LD_LIBRARY_PATH:-}
```

The candidate also notes that `/path/to/.venv/` must be replaced with the pod
virtualenv path and that these exports are required for `numba_cuda_jit: pass`.

Claude's non-blocking recommendations were also applied:

- the native library path placeholders are explicitly described as build-output
  paths that must be substituted;
- the CUDA 12.4 nvcc plus CUDA 12.9 NVRTC/runtime package mix is explained as a
  tested-pod requirement, with gate results taking precedence over resolver
  silence.

## Claim Boundary

This consensus authorizes only this narrow statement:

```text
Phoenix V3 evidence has a reviewed source-tree/pod-gated reproducibility
candidate for the documented RTX pod environment.
```

This consensus does not authorize:

```text
V3 is released.
V3 has a general installer.
pip install rtdl gives a finished V3 GPU release.
V3 performance is confirmed across RT-core hardware.
V3 broadly beats V2.
The installer blocker is closed.
```

## Why The Installer Blocker Remains Open

Claude explicitly recommended that `installer_closes_release_blocker` remain
`false`. Codex agrees.

The candidate is reviewed as a reproducibility path, not as a release-scope
decision. To close the installer/reproducibility blocker, Phoenix still needs
one of these:

1. a 2-AI reviewed source-tree/pod-gated release-scope decision with final
   scoped wording and a machine-readable gate update; or
2. a reviewed general package installer and install documentation.

## Gate Update

The install reproducibility gate should now report:

```text
source_tree_pod_gated_candidate_present: true
source_tree_pod_gated_candidate_reviewed: true
general_release_installer_ready: false
package_install_claim_authorized: false
installer_closes_release_blocker: false
release_authorized: false
```

The aggregate release readiness gate should remain:

```text
status: blocked_not_release
```

with `general_release_installer_not_ready` still active.

## Goal-Level Decision Audit

Decision: accept Claude's amended approval and mark the candidate reviewed
without closing the installer blocker.

1. Was I foolish?
   No. This changes only the evidence-review field Claude said could change,
   while preserving all release-blocking fields.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to treat candidate-level review
   as release authorization or as a general installer.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Build a general package installer now. That may still be required, but
   it is a different and larger release-scope path.
4. Can I now try a different path that actually solves the problem?
   Yes. Use this reviewed candidate as the basis for either a scoped release
   wording review, or build the general installer if scoped release is rejected.
