I have what I need. Let me now deliver the review.

---

# Review: Phoenix V3 Source-Tree / Pod-Gated Thirteen-Row Scope Extension

**Reviewer:** Claude Sonnet 4.6  
**Date:** 2026-06-22  
**Files read:** candidate packet, `phoenix_v3_release_readiness_gate_2026-06-21.json`, `claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md`, `claude_phoenix_v3_source_tree_pod_gated_scoped_release_wording_review_2026-06-21.md`

---

## Verdict

**`accept-with-amendments-not-release`**

One P0 amendment is required before any gate field changes. This review does not authorize release. The only permitted outcome is a scoped installer/reproducibility scope label update from twelve-row to thirteen-row, conditional on the amendment below.

---

## Findings, Ordered by Severity

### P0 — Install-script coverage of the Spatial row is asserted, not documented

**Finding:** The candidate lists `scripts/v3_install_gpu_pod_env.sh` as a "required existing basis" artifact (implying it does not change) and proposes no delta to that script. However, the candidate does not explicitly state that the Spatial benchmark (`point_location_topology_stream` default-path configuration) is already covered by the existing install script without modification, and does not enumerate whether any new package pins or build steps are required.

The twelve-row installer closure was reviewed as a verified unit: install scripts + package pins + native build commands + gate sequence, all together. The 13th row's POD evidence was reviewed separately for M7 eligibility under the Spatial promotion review. That review also carries a documented `git_commit: null` provenance gap ("remote source is a non-git checkout"), which was explicitly accepted for M7 eligibility but not explicitly resolved in the installer-path context.

The install-path coverage must be stated explicitly, not implied by omission of a script delta. The pattern established by the eleven-row review's P0 Amendment 1 (explicit gate script delta required) generalizes here: if the install script does not change, say so explicitly and state why the Spatial benchmark is already covered.

**Required fix:** Add a section to the candidate stating one of:

```
v3_install_gpu_pod_env.sh coverage confirmation:
  The Spatial benchmark `point_location_topology_stream` default-path configuration
  requires no changes to v3_install_gpu_pod_env.sh. All required packages are
  already pinned in the existing twelve-row install path. The Spatial POD evidence
  was captured in the same install-script-configured pod environment. The git_commit:null
  provenance gap from the promotion review does not affect install-path coverage
  because [specific reason: e.g., the source SHA records the correct built library].
```

OR, if any install-script changes are needed:

```
v3_install_gpu_pod_env.sh delta (required):
  [Enumerate exact changes]
```

Until one of these is present, the scope of the installer path covering the Spatial row is underdetermined.

---

### P1 — `aggregate_13_row_installer_scope_review_required` flag not addressed

**Finding:** The gate JSON records `aggregate_13_row_installer_scope_review_required: true`. If this review accepts the scope extension, that field should be noted as resolved. The candidate does not mention this flag or specify that it should be set to `false` (or removed) after acceptance.

**Required fix:** The gate script delta section should include:
```
- set `aggregate_13_row_installer_scope_review_required` to false
  (or remove field; it is satisfied by this review)
```

This is a P1 because the gate script delta is otherwise specified; this is an omission, not a structural gap.

---

### P2 — Source provenance gap handling in installer context not bound

**Finding:** The Spatial promotion review explicitly noted: "This is acceptable for M7 row eligibility because the packet records source SHA and built library SHA. It is not acceptable for a future public release artifact, which must come from a versioned git-tagged build." The thirteen-row scope extension is not a public release artifact, but this statement should be explicitly carried into the installer-scope context so a future reviewer does not mistake the scope extension for full release provenance closure.

**Recommended fix (non-blocking):** Add to the candidate's "Increment Since Twelve-Row Scope" section:

```
The Spatial POD evidence carries a git_commit: null provenance gap (non-git
checkout) as recorded in the promotion review. This gap is acceptable for the
source-tree/pod-gated installer scope because the packet records source SHA and
built library SHA. It does not establish full release-artifact provenance;
that requires a versioned git-tagged build, which remains a future requirement.
```

---

## Answers to the Six Required Review Questions

**Q1 — Is `source_tree_pod_gated_thirteen_row` precise enough?**

Yes, by the same three-axis standard applied to the eleven- and twelve-row scopes:
- Delivery mechanism: source tree
- Reproducibility gating: pod-gated
- Evidence count: thirteen rows

Each axis is independently verifiable. The scope cannot be confused with a general package release, broad V3-over-V2 speedup, or hardware portability claim without a deliberate wording violation. The candidate enumerates all thirteen row IDs exactly, preventing silent scope creep.

The label is precise enough — provided the P0 amendment documents install-script coverage explicitly.

**Q2 — Does the prior source-tree/pod-gated reproducibility basis cover the new Spatial row, or is a fresh pod rerun/install packet required?**

The prior basis is *likely* sufficient — the gate JSON already lists the Spatial row in `expected_m7_rows`, `m7_qualified_release_rows` is already 13, and the gate checks `release_surface_breadth_gate_thirteen_rows: true` already pass. The aggregate review chain explicitly flagged the installer scope mismatch (`aggregate_13_row_review_flags_installer_scope_mismatch: true`) and proposed resolving it via this exact scope extension review.

However, "likely sufficient" is not "documented sufficient." The P0 amendment converts the implication into an explicit statement. If the install script was already verified to include the Spatial benchmark, no fresh pod rerun or install packet is required — only the explicit confirmation. If the install script was not verified to include the Spatial benchmark, a fresh install-path verification is required before this extension can be accepted.

**Q3 — If accepted, what exact machine fields may change?**

After P0 amendment applied and Codex consensus recorded — and only then:

| Field | From | To |
|---|---|---|
| `release_scope` | `source_tree_pod_gated_twelve_row` | `source_tree_pod_gated_thirteen_row` |
| `installer_closes_release_blocker_scope` | `source_tree_pod_gated_twelve_row` | `source_tree_pod_gated_thirteen_row` |
| `source_tree_pod_gated_thirteen_row_scope_extension_reviewed` | `false` | `true` |
| `aggregate_13_row_installer_scope_review_required` | `true` | `false` (P1 fix) |

No other fields may change in this update pass.

**Q4 — Which fields must remain false?**

These fields must remain at their current values and must not change:

| Field | Required value |
|---|---|
| `release_authorized` | `false` |
| `general_release_installer_ready` | `false` |
| `package_install_claim_authorized` | `false` |
| `secondary_rt_performance_confirmation_authorized` | `false` |
| `broad_v3_faster_than_v2_claim_authorized` | `false` |
| `public_speedup_claim_authorized` | `false` |
| `multi_gpu_performance_portability_claim_authorized` | `false` |
| Gate status | `staged_pod_gate_present_general_release_installer_not_ready` unchanged |
| Overall status | `blocked_not_release` unchanged |
| `installer_closes_release_blocker` | `true` — keep, no re-change needed |

**Q5 — Does this extension authorize release, package-install wording, broad hardware portability, public Spatial speedup, RTDL-beats-RayJoin, true zero-copy, broad V3-over-V2 speedup, or whole-app claims?**

No. None of these.

| Claim | Authorized by this extension? |
|---|---|
| Release authorization | No — `release_authorized: false` unchanged; independent consensus required |
| Package-install wording / `pip install rtdl` | No — `package_install_claim_authorized: false` unchanged |
| Broad hardware portability | No — single RTX 4000 Ada pod; secondary hardware waiver is a separate track |
| Public Spatial speedup | No — `public_speedup_claim_authorized: false` unchanged; promotion review boundary explicitly prohibits this |
| RTDL-beats-RayJoin | No — forbidden by the promotion review boundary |
| True zero-copy | No — forbidden by the promotion review boundary |
| Broad V3-over-V2 speedup | No — `broad_v3_faster_than_v2_claim_authorized: false` unchanged |
| Whole-app speedup from thirteen rows | No — forbidden wording in candidate |
| Multi-GPU portability | No — `multi_gpu_performance_portability_claim_authorized: false` unchanged |

The only thing authorized by this extension (after P0 amendment + Codex consensus) is a scope label update on the installer/reproducibility closure, from twelve-row to thirteen-row.

**Q6 — If rejected, what fix is required?**

This review does not reject. But the P0 amendment is a blocking condition. If the install-script coverage statement cannot be made (because the Spatial benchmark requires new dependencies or was captured in a different environment), the fix is:

1. Verify whether `v3_install_gpu_pod_env.sh` handles the Spatial benchmark.
2. If yes: add the explicit statement to the candidate; no fresh pod rerun needed.
3. If no: enumerate the install-script delta, run the gate under the updated script, confirm the gate returns expected output for all 13 rows including the Spatial row, and then re-submit the candidate with the verified script delta.

---

## What Is Solid in the Candidate

- **Scope precision**: three-axis label, exact row enumeration, no ambiguity.
- **Gate script delta**: explicitly enumerated (learning from the eleven-row P0 Amendment 1 pattern). The prior review required this as a P0 amendment; this candidate provides it proactively.
- **Forbidden wording list**: all required forbidden phrases are present and correct.
- **Field discipline**: every false field is explicitly kept false; no cascading changes.
- **Incremental change**: one row added, with a specific reviewed ID and documented boundary conditions from the promotion review.
- **Prior review chain**: Spatial promotion review + 2-AI Codex consensus are listed as required existing basis; the promotion review accepted the Spatial row for M7 eligibility with clear boundaries.
- **No release implication**: the candidate correctly characterizes every claim boundary and does not attempt to use the scope extension to unlock any blocked field.

---

## Required Amendments Before Gate Changes

### P0 — Install-script coverage confirmation (blocking)

Add to the candidate (suggested placement: between "Increment Since Twelve-Row Scope" and "Required Existing Basis"):

```
## Install-Script Coverage Confirmation

v3_install_gpu_pod_env.sh covers the Spatial benchmark without modification.
[One of the following must be true and stated:]

Option A (no changes):
  All packages required by the Spatial benchmark's default-path configuration
  are already pinned in the existing twelve-row install path. No new package pins,
  build steps, or environment variables are required. The Spatial POD evidence
  was captured in an environment consistent with the install-script-configured pod.

Option B (install script delta required):
  [Enumerate exact changes to v3_install_gpu_pod_env.sh]
  These changes must be verified to produce a passing gate run before this
  extension is accepted.
```

No gate field changes until this section is present and Codex consensus is recorded.

### P1 — Add `aggregate_13_row_installer_scope_review_required` to gate delta (non-blocking for acceptance, required in gate update pass)

In the "Required Gate Script Delta If Accepted" section, add:

```
- set `aggregate_13_row_installer_scope_review_required` to false
```

### P2 (Recommended) — Provenance gap scoping statement

Add to "Increment Since Twelve-Row Scope":

```
The Spatial POD evidence carries a git_commit: null provenance gap as recorded
in the promotion review. This is acceptable for this installer scope extension
because the packet records source SHA and built library SHA. It does not close
the future requirement for a versioned git-tagged build artifact.
```

---

## Gate Recommendation

No gate fields change until:

1. P0 Amendment applied to the candidate document.
2. Codex records consensus accepting this review.
3. Gate script updated to exactly: `SCOPED_RELEASE_SCOPE` → `source_tree_pod_gated_thirteen_row`, new field `source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true`, and `aggregate_13_row_installer_scope_review_required: false`.
4. Gate run confirmed to return `staged_pod_gate_present_general_release_installer_not_ready` with `release_authorized: false` and `general_release_installer_ready: false` unchanged.

After those four steps, and only those steps, the scope label fields may update to `source_tree_pod_gated_thirteen_row`.

---

This review does not authorize release. `release_authorized` must remain `false`. The aggregate 13-row release-readiness review (`updated_thirteen_row_release_readiness_consensus_required`) remains a separate open blocker that is not addressed by this extension.
