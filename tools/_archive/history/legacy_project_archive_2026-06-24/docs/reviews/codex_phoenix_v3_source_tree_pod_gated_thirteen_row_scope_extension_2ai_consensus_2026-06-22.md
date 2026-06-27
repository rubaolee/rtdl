# Codex Consensus: Phoenix V3 Source-Tree / Pod-Gated Thirteen-Row Scope Extension

Date: 2026-06-22

Status:
`claude_codex_consensus_source_tree_pod_gated_thirteen_row_scope_extension_reviewed_not_release`

External review:
`docs/reviews/claude_phoenix_v3_source_tree_pod_gated_thirteen_row_scope_extension_review_2026-06-22.md`

Claude verdict: `accept-with-amendments-not-release`

Codex verdict: accept Claude's scoped thirteen-row installer/reproducibility
extension after applying the required P0 amendment, the P1 gate-field fix, and
the recommended provenance scoping note.

## Decision

Phoenix V3 may extend the reviewed source-tree/pod-gated
installer/reproducibility closure from:

```text
source_tree_pod_gated_twelve_row
```

to:

```text
source_tree_pod_gated_thirteen_row
```

This is only a scoped installer/reproducibility label update. It does not
authorize V3 release.

## Amendments Applied

Claude's blocking P0 amendment is applied in:

```text
docs/rebuild/v3/v3_source_tree_pod_gated_thirteen_row_scope_extension_candidate_2026-06-22.md
```

The candidate now explicitly states:

```text
v3_install_gpu_pod_env.sh covers the Spatial point_location_topology_stream
default-path configuration without modification.
```

The accepted basis is Option A: no install-script delta is required. The Spatial
row uses source-tree imports, the existing native OptiX runtime, the existing
runbook native build and runtime variables, and the already-pinned CuPy /
Numba / CUDA-wheel package set from the staged pod gate.

The P1 gate-field fix is also applied in the candidate:

```text
aggregate_13_row_installer_scope_review_required: false
```

The provenance note is carried forward: the Spatial POD evidence has
`git_commit: null`, which is acceptable for this source-tree/pod-gated scope
because the packet records local native source SHA and pod-built OptiX library
SHA. It is not sufficient for a future versioned public release artifact.

## Allowed Machine-Field Changes

After this consensus, the install and release-readiness gates may record:

```text
release_scope: source_tree_pod_gated_thirteen_row
installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row
source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true
aggregate_13_row_installer_scope_review_required: false
```

The install gate status remains:

```text
staged_pod_gate_present_general_release_installer_not_ready
```

## Fields That Must Remain False

This consensus does not authorize release. These fields must remain false:

```text
release_authorized: false
general_release_installer_ready: false
package_install_claim_authorized: false
secondary_rt_performance_confirmation_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
public_speedup_claim_authorized: false
multi_gpu_performance_portability_claim_authorized: false
```

## Forbidden Claims

This consensus does not authorize:

- V3 release-ready wording.
- Package-install wording or `pip install rtdl` readiness.
- Broad RT-core hardware portability.
- Public Spatial speedup.
- `RTDL beats RayJoin` wording.
- True zero-copy wording.
- Broad V3-over-V2 speedup.
- Whole-app speedup from thirteen rows.
- V4, C ABI, embedding, or multi-language host wording.

## Remaining Release Blocker

After the gate update, the installer-scope mismatch may close, but the aggregate
release-readiness blocker remains:

```text
updated_thirteen_row_release_readiness_consensus_required
```

Phoenix V3 must still receive a separate aggregate 13-row release-readiness
review before any release authorization can change.

## Goal-Level Decision Audit

Decision: accept the Claude-reviewed thirteen-row source-tree/pod-gated
installer/reproducibility scope extension and keep release authorization false.

1. Was I foolish?
   No. I waited for Claude review, applied its P0/P1 amendments, and limited the
   change to a machine-readable scope label rather than turning it into release
   authorization.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to broaden the twelve-row
   installer scope silently, or to treat a scoped pod-gated path as a general
   package installer.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Re-run a fresh full install packet for all thirteen rows or build a
   general package installer first. Those are larger paths than the reviewed
   source-tree/pod-gated scope extension.
4. Can I now try a different path that actually solves the problem?
   Yes. Update the gates to record the reviewed thirteen-row scope, rerun the
   V3 matrix, then request the separate aggregate 13-row release-readiness
   review.
