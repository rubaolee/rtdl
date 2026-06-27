# V3 Install Reproducibility Strategy

Status: staged pod gate present; source-tree/pod-gated candidate reviewed;
installer blocker scoped-closed; general release installer not ready.

This packet classifies the Phoenix V3 GPU install path. It does not authorize a
V3 release, package-install wording, or a claim that a normal user can install
V3 from a polished release package.

## Decision

`scripts/v3_install_gpu_pod_env.sh` is accepted only as a staged pod-environment
gate for reproducing the 2026-06-20 Phoenix V3 GPU evidence package set.

It is not a general release installer.

The script intentionally requires:

```text
--accept-experimental-pod-gate
```

That flag is load-bearing. It prevents the script from being mistaken for a
normal install path.

## Package Set

The staged GPU pod gate installs the package set required by the repaired
Phoenix V3 pod runs:

```text
torch==2.6.0+cu124
cupy-cuda12x==14.1.1
numba==0.65.1
nvidia-cuda-nvcc-cu12==12.4.131
nvidia-cuda-nvrtc-cu12==12.9.86
nvidia-cuda-runtime-cu12==12.9.79
```

After installation it runs:

```text
python3 scripts/v3_gpu_python_env_gate.py --pretty
```

## Machine Gate

Run:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_install_reproducibility_gate.py --pretty
```

Expected current status:

```text
status: staged_pod_gate_present_general_release_installer_not_ready
staged_gpu_pod_gate_available: true
release_scope: source_tree_pod_gated_thirteen_row
general_release_installer_ready: false
package_install_claim_authorized: false
source_tree_pod_gated_scoped_release_wording_reviewed: true
source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true
aggregate_13_row_installer_scope_review_required: false
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row
release_authorized: false
```

## Release Consequence

The installer blocker is closed only under the machine-readable
`source_tree_pod_gated_thirteen_row` scope. The general release installer
remains not ready.

There is now an externally reviewed source-tree/pod-gated reproducibility
candidate:

```text
docs/rebuild/v3/v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md
```

Its current machine-readable status is:

```text
source_tree_pod_gated_candidate_present: true
source_tree_pod_gated_candidate_reviewed: true
source_tree_pod_gated_scoped_release_wording_reviewed: true
source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true
aggregate_13_row_installer_scope_review_required: false
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row
```

The candidate is reviewed reproducibility material only. It is not a general
release installer, not package-install wording, and not release authorization.

The remaining release work is:

1. obtain a new aggregate release-readiness review that covers the thirteen-row
   surface, scoped installer closure, and reviewed
   `single_rtx_4000_ada_driver_550_127_05_pod` hardware waiver;
3. build a reviewed general release installer later if package-install wording
   is desired.

Until a general installer exists, Phoenix V3 may cite the script only as a
staged pod reproducibility gate under `source_tree_pod_gated_thirteen_row`
scope.

## Goal-Level Decision Audit

Decision: classify the Phoenix V3 installer as a staged pod gate, not a general
release installer, while recording that the source-tree/pod-gated
reproducibility candidate, scoped release wording, and thirteen-row scope
extension are reviewed.

1. Was I foolish?
   No. This closes only the scoped thirteen-row installer blocker while
   preventing a dependency-gated pod script from being promoted into a
   user-facing install promise.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be claiming package-install
   readiness or release authorization because a scoped installer blocker is
   closed.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: build a general package installer first. That remains necessary for
   package-install wording.
4. Can I now try a different path that actually solves the problem?
   Yes. Request a new aggregate release-readiness review that covers the scoped
   thirteen-row installer closure and the reviewed single-RTX hardware waiver.
