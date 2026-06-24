# Claude Review: Phoenix V3 Source-Tree / Pod-Gated Scoped Release Wording

Reviewer: Claude Sonnet 4.6 (external, local Windows Claude Code)
Date: 2026-06-21
Files read: all twelve listed in the call-for-review.

Verdict: `accept-with-amendments-not-release`

---

## Bottom Line

The `source_tree_pod_gated_eleven_row` scope is precise enough to close the
installer/reproducibility blocker without claiming a general installer, and the
candidate correctly preserves every blocked field. Two P0 amendments are
required before `installer_closes_release_blocker: true` can be recorded: the
candidate must specify the exact gate script delta and must add a
`release_scope: source_tree_pod_gated_eleven_row` machine-readable field to the
gate payload so the scoped acceptance is verifiable, not only
prose-documented.

This review does not authorize release. It does not close any blocker by
itself. Every field not explicitly named below must remain at its current value.
Codex consensus is still required before any gate field is updated.

---

## Findings

### What is solid

**Scope precision.** The label `source_tree_pod_gated_eleven_row` encodes
three orthogonal constraints: delivery mechanism (source tree), reproducibility
gating (pod-gated), and evidence count (eleven row). Each axis is independently
verifiable. The scope is not synonymous with any broader concept — it cannot
be confused with "package release," "general installer," or "broad V3-over-V2
speedup" without a deliberate wording violation.

**Forbidden wording list.** The candidate explicitly lists eight forbidden
phrases covering `V3 is release-ready`, `V3 has a general installer`,
`pip install rtdl`, `V3 performance is confirmed across RT-core hardware`,
`V3 broadly beats V2.x`, `All benchmark apps are release-ready`,
`The eleven M7 rows imply full-app acceleration`, and `V3 is finished`. These
are the exact overclaims a user might attempt. The gate script enforces a
subset of this list machine-readably via `REQUIRED_CANDIDATE_PHRASES`.

**Active pip-install confusion protection.** The experimental flag
`--accept-experimental-pod-gate` is load-bearing: the install script refuses
invocation without it, the gate verifies this refusal logic, the runbook quotes
the flag with the label "Staged installer for the tested pod-style environment,"
and the reproducibility candidate quotes it in the install command. A user
cannot accidentally use this path as a general installer; they must explicitly
invoke the flag.

**Field discipline.** The candidate asks to change exactly one field
(`installer_closes_release_blocker: false → true`). It explicitly keeps
`release_authorized`, `general_release_installer_ready`,
`package_install_claim_authorized`,
`secondary_rt_performance_confirmation_authorized`, and
`broad_v3_faster_than_v2_claim_authorized` all false. The gate script
currently hardcodes `installer_closes_release_blocker: False` and
`release_authorized: False` independently, so changing the installer blocker
field does not cascade to the release field.

**Reviewed reproducibility basis.** The candidate depends on the
already-reviewed reproducibility candidate and its 2-AI consensus
(`source_tree_pod_gated_candidate_reviewed: true`). That consensus confirmed
the Numba CUDA path exports were added, the package pins are exact, the native
build commands are correct, and the gate sequence produces confirming output.
The reproducibility basis is solid.

**Gate machinery alignment.** The gate script's `required_next_action` field
explicitly names this wording path: "Close installer/reproducibility with 2-AI
source-tree/pod-gated release-scope wording or replace the staged pod gate with
a reviewed general release installer." The candidate is operationalizing the
path that the gate itself already describes as the intended next step.

**Exact row enumeration.** The candidate lists all eleven M7-qualified row IDs
exactly. This prevents scope creep: a future wording claim using this scope
must reference these exact rows, and any attempt to extend it to new rows
requires a new scoped wording review.

**Prior review chain.** The eleven-row release-readiness review (Claude +
Codex consensus, also 2026-06-21) explicitly names this as a valid path at Q3
and Step 2 of the suggested next sequence. The current candidate operationalizes
that recommendation. The prior review's P0 blockers 4–6 are the intended targets
of this candidate; this candidate addresses only P0 blocker 4
(`general_release_installer_not_ready`), correctly leaving 5 and 6 open.

---

### What requires amendment

**P0 Amendment 1 — Gate script delta not specified.** The candidate describes
the expected gate output after acceptance but does not specify which fields in
`scripts/v3_phoenix_install_reproducibility_gate.py` must change and what they
must become. The gate currently hardcodes `"installer_closes_release_blocker":
False` at line 183. Without an explicit delta, a Codex gate update could
introduce ambiguity: for example, Codex could set the field to `True` without
adding scope context, or could inadvertently alter adjacent fields. The
candidate must add a section specifying the exact gate script changes:

```text
Required gate script changes (scripts/v3_phoenix_install_reproducibility_gate.py):
  - Line 183: "installer_closes_release_blocker": False → True
  - Add new field: "installer_closes_release_blocker_scope": "source_tree_pod_gated_eleven_row"
  - Add new field: "release_scope": "source_tree_pod_gated_eleven_row"
  - "release_authorized": False — no change
  - "general_release_installer_ready": False — no change
  - "package_install_claim_authorized": False — no change
  - Update required_next_action to reflect that installer blocker is now closed
    and next open P0 is secondary_rt_performance_confirmation_not_closed
```

Without this explicit delta, the field update is underdetermined.

**P0 Amendment 2 — No machine-readable `release_scope` field.** The gate
script's current payload has no `release_scope` field. After acceptance, the
gate will report `installer_closes_release_blocker: true`, but a user running
the gate will not know from the machine-readable output under what scope that
True value was granted. The scope must be machine-readable alongside the field
value so that a future reviewer can verify the scope was correctly applied and
was not silently expanded. The candidate must specify that a
`release_scope: source_tree_pod_gated_eleven_row` field is added to the gate
payload simultaneously with the blocker-field change.

**Recommended (non-blocking) Amendment 3 — Single-hardware disclosure.** The
allowed wording section does not explicitly require hardware disclosure. The
reproducibility candidate and runbook both mention "RTX 4000 Ada pod" in
context, but the wording scope line should include a disclosure requirement:

```text
This is source-tree/pod-gated evidence on a single RTX 4000 Ada pod.
This does not confirm performance across RT-core hardware classes.
```

This prevents a user from citing the `installer_closes_release_blocker: true`
status as evidence that V3 is hardware-validated broadly. The secondary-hardware
blocker is still open; the wording scope must not obscure that.

**Recommended (non-blocking) Amendment 4 — `required_next_action` update
specification.** After `installer_closes_release_blocker` is set to `True`, the
gate's current `required_next_action` value ("Close installer/reproducibility
with 2-AI source-tree/pod-gated release-scope wording...") becomes stale. The
candidate should specify the replacement `required_next_action` text so Codex
applies a consistent, accurate next-action string:

```text
required_next_action (post-acceptance):
  "Close secondary RT performance blocker with a second RTX/RT-core run or an
   explicit 2-AI-reviewed hardware-scoped waiver. Then request a new aggregate
   release-readiness external review."
```

---

## Answers To The Six Questions

**Q1: Is `source_tree_pod_gated_eleven_row` a precise enough product scope to
close the installer/reproducibility blocker without claiming a general
installer?**

Yes, with the P0 amendments applied. The label is not ambiguous. It does not
overlap with `pip install`, general release, or broad speedup concepts. Its
three axes (source tree, pod-gated, eleven row) each independently constrain the
scope. The forbidden wording list covers every adjacent overclaim. The
experimental flag provides runtime enforcement. The scope is precise enough to
close this specific blocker — provided the gate update records the scope as a
machine-readable field alongside the changed value, so the scope cannot drift
silently.

**Q2: If accepted, what exact machine fields may change, and which must remain
false?**

May change (after P0 amendments applied and Codex consensus recorded):

| Field | From | To |
| --- | --- | --- |
| `installer_closes_release_blocker` | `false` | `true` |
| `source_tree_pod_gated_scoped_release_wording_reviewed` | `false` | `true` |
| `release_scope` | (absent) | `source_tree_pod_gated_eleven_row` (new field) |
| `installer_closes_release_blocker_scope` | (absent) | `source_tree_pod_gated_eleven_row` (new field) |

Must remain false and must not change:

| Field | Required value |
| --- | --- |
| `release_authorized` | `false` |
| `general_release_installer_ready` | `false` |
| `package_install_claim_authorized` | `false` |
| `secondary_rt_performance_confirmation_authorized` | `false` |
| `broad_v3_faster_than_v2_claim_authorized` | `false` |
| Gate status | `staged_pod_gate_present_general_release_installer_not_ready` |

The overall gate status string must not change. The gate status is a composite
that reflects that a general release installer is still not ready; closing the
installer blocker under a scoped path does not make the general-installer status
true. These two properties are independent and the candidate correctly treats
them as such.

**Q3: If rejected, is the required next step a general installer, stronger
scoped wording, more hardware evidence, or more M7 rows?**

This review does not reject. But for completeness: if the scope were rejected
as insufficiently precise, the correct next step would be stronger scoped
wording (not more M7 rows, more hardware evidence, or a general installer).
The M7 surface and hardware evidence are independent P0 blockers on separate
tracks; adding rows or hardware evidence would not address the installer
blocker. A general installer is the longer fallback path the candidate itself
names. The shorter path is to strengthen the scoped wording language until it
is precise enough — which the P0 amendments accomplish.

**Q4: Does the candidate protect users from confusing a source-tree/pod-gated
evidence path with `pip install` release readiness?**

Yes, with three independent layers of protection:

1. **Runtime enforcement.** The install script refuses without
   `--accept-experimental-pod-gate`. A user cannot accidentally run it as a
   general installer.
2. **Prose enforcement.** The candidate's forbidden wording list includes
   `pip install rtdl gives a finished V3 GPU release` and `V3 has a general
   installer`. Any document built on this scope that contains these phrases
   violates the scope contract explicitly.
3. **Gate enforcement.** The gate verifies that forbidden-phrase absence is
   preserved via `REQUIRED_CANDIDATE_PHRASES`. A scope-violating document would
   fail the gate's phrase checks.

The Recommended Amendment 3 (single-hardware disclosure in allowed wording)
adds a fourth layer that prevents hardware scope confusion alongside install
scope confusion.

**Q5: Does the candidate preserve broad V3-over-V2 speedup, secondary RT-core
confirmation, whole-app speedup, paper reproduction, and release authorization
as blocked?**

Yes, fully.

| Claim | Preserved as blocked? | How enforced? |
| --- | --- | --- |
| Broad V3-over-V2 speedup | Yes | `broad_v3_faster_than_v2_claim_authorized: false` unchanged; forbidden wording list; gate |
| Secondary RT-core confirmation | Yes | `secondary_rt_performance_confirmation_authorized: false` unchanged; secondary platform gate separate |
| Whole-app speedup | Yes | Forbidden wording: "The eleven M7 rows imply full-app acceleration" |
| Paper reproduction | Yes | Forbidden wording covers this class; no paper claim appears in allowed wording |
| Release authorization | Yes | `release_authorized: false` unchanged; gate status `staged_pod_gate_present_general_release_installer_not_ready` unchanged; prior eleven-row consensus blocks release independently |

The current eleven-row release-readiness consensus
(`claude_codex_consensus_current_eleven_row_not_release_ready_fix_p0`) remains
active regardless of this scoped wording acceptance. Closing the installer
blocker is a necessary condition for release, not a sufficient condition.
Secondary hardware and external release consensus remain open P0 blockers on
independent tracks.

**Q6: What exact amendments, if any, must Codex apply before updating any
gate?**

See Required Amendments section below. Summary:

- P0 Amendment 1: add explicit gate script delta to the wording candidate.
- P0 Amendment 2: specify `release_scope` and `installer_closes_release_blocker_scope`
  as new machine-readable gate fields.
- These two must be applied and confirmed by Codex consensus before any gate
  field changes.
- Recommended Amendments 3–4 are non-blocking but should be applied in the
  same pass.

---

## Required Amendments

### P0 Amendment 1 — Explicit gate script delta

Add the following section to
`docs/rebuild/v3/v3_source_tree_pod_gated_scoped_release_wording_candidate_2026-06-21.md`
before or within the "Candidate Status Fields" section:

```text
## Required Gate Script Changes

If this scoped wording is accepted by 2-AI consensus, Codex must apply exactly
these changes to `scripts/v3_phoenix_install_reproducibility_gate.py`:

In `build_payload()`:
  - Change `"installer_closes_release_blocker": False` to `True`
  - Add `"installer_closes_release_blocker_scope": "source_tree_pod_gated_eleven_row"`
    immediately after that line
  - Add `"release_scope": "source_tree_pod_gated_eleven_row"` to the top-level
    payload dict
  - Keep `"release_authorized": False` — no change
  - Keep `"general_release_installer_ready": False` — no change
  - Keep `"package_install_claim_authorized": False` — no change
  - Keep gate status `staged_pod_gate_present_general_release_installer_not_ready` —
    no change (composite status not affected by scoped installer closure)
  - Update `required_next_action` to:
    "Close secondary RT performance blocker with a second RTX/RT-core run or an
     explicit 2-AI-reviewed hardware-scoped waiver. Then obtain a new aggregate
     release-readiness external review."

No other gate script fields may change in this update pass.
```

### P0 Amendment 2 — Machine-readable scope field in candidate wording

In the "Candidate Status Fields" block of the wording candidate, add:

```text
release_scope: source_tree_pod_gated_eleven_row
installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row
```

These must appear in the candidate document so the gate's phrase-check can
verify the scope is explicitly named in the wording record.

### Recommended Amendment 3 — Single-hardware disclosure in allowed wording

Add to the "Allowed Wording If Accepted" section, after the last allowed
statement and before the required boundaries block:

```text
It must also disclose:
This is source-tree/pod-gated evidence from a single RTX 4000 Ada pod.
This does not confirm performance across RT-core hardware classes.
```

### Recommended Amendment 4 — Post-acceptance `required_next_action` specification

Add to the candidate, after the "Required Gate Script Changes" section (from
Amendment 1):

```text
After this scoped wording is accepted, the next open P0 blockers are:
1. secondary_rt_performance_confirmation_not_closed
2. external_release_readiness_consensus_blocks_major_release_wording
These remain unaffected by this acceptance.
```

---

## Gate Recommendation

| Field | Current value | After P0 amendments applied + Codex consensus |
| --- | --- | --- |
| `installer_closes_release_blocker` | `false` | `true` — only after P0 amendments confirmed |
| `release_scope` | (absent) | `source_tree_pod_gated_eleven_row` — new field |
| `installer_closes_release_blocker_scope` | (absent) | `source_tree_pod_gated_eleven_row` — new field |
| `source_tree_pod_gated_scoped_release_wording_reviewed` | `false` | `true` |
| `release_authorized` | `false` | `false` — no change |
| `general_release_installer_ready` | `false` | `false` — no change |
| `package_install_claim_authorized` | `false` | `false` — no change |
| `secondary_rt_performance_confirmation_authorized` | `false` | `false` — no change |
| `broad_v3_faster_than_v2_claim_authorized` | `false` | `false` — no change |
| Gate status | `staged_pod_gate_present_general_release_installer_not_ready` | `staged_pod_gate_present_general_release_installer_not_ready` — no change |

The gate status string must not change. Closing the installer blocker under a
scoped path means the blocker is addressed under that scope; it does not mean
a general release installer is ready. These are independent properties and must
remain independently represented.

No gate field changes until:

1. P0 Amendment 1 is added to the wording candidate.
2. P0 Amendment 2 is added to the wording candidate.
3. Codex records consensus accepting this review.
4. The gate script is updated exactly as specified in Amendment 1.
5. The gate is run and confirms expected output.

---

## Claim Boundary Check

| Claim | Authorized under `source_tree_pod_gated_eleven_row` scope? | Notes |
| --- | --- | --- |
| Reviewed source-tree/pod-gated reproducibility path exists for eleven M7 rows | Yes | Narrow disclosure required; must name RTX 4000 Ada pod and experimental flag |
| Evidence can be rerun from source tree using documented commands | Yes | Only on RTX pod with documented package set; placeholder paths must be substituted |
| General package installer available | No | `general_release_installer_ready: false` enforced; unchanged |
| `pip install rtdl` gives V3 GPU | No | `package_install_claim_authorized: false` enforced; unchanged |
| V3 release authorized | No | `release_authorized: false` enforced; eleven-row consensus still blocks |
| Broad V3-over-V2 speedup | No | 1.012x geomean; explicitly blocked; unchanged |
| V3 performance confirmed across RT-core hardware | No | Single RTX 4000 Ada pod; secondary platform gate separate; unchanged |
| Paper reproduction | No | No paper-reproduction allowed wording; unchanged |
| Whole-app speedup from eleven rows | No | Forbidden wording; unchanged |
| `installer_closes_release_blocker: true` | Yes, under scope — after amendments + Codex consensus | Must be accompanied by `installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row` |

---

## Evidence Gaps Or Weak Sources

**Single-hardware scope.** All eleven M7 rows come from one RTX 4000 Ada pod
(driver 550.127.05). The scoped wording correctly limits performance claims to
this pod class, but any external user encountering `installer_closes_release_blocker:
true` in the gate output may not immediately understand this hardware constraint.
P0 Amendment 2 and Recommended Amendment 3 together address this by making the
scope machine-readable and requiring hardware disclosure in allowed wording.

**Installer blocker ≠ release readiness.** After this acceptance, the gate will
report `installer_closes_release_blocker: true`. A casual reader might interpret
this as "V3 is release-ready." The gate's simultaneous `release_authorized: false`
and unchanged `staged_pod_gate_present_general_release_installer_not_ready`
status string should prevent this, but the `installer_closes_release_blocker_scope`
field specified in the P0 amendments provides an additional machine-readable
guard that the True value is scope-qualified, not absolute.

**Secondary hardware blocker remains open.** After this acceptance, two P0
blockers remain from the eleven-row consensus: secondary RT-core performance
confirmation and the external release-readiness consensus. Neither is affected
by this review. Both must remain machine-readable as open blockers in the
aggregate gate.

**Wording scanner is first-pass only.** The current `v3_release_wording_gate.py`
is described in all documents as a first-pass scanner, not a final
release-authorization scanner. Accepting the scoped installer closure does not
upgrade the wording scanner. Any release attempt must still upgrade the scanner
before public release.

**No git head in the candidate.** Consistent with other Phoenix artifacts, the
wording candidate records no git commit hash. Provenance depends on
`source_manifest.sha256` cross-referencing from the reproducibility candidate.
This is a pre-existing limitation of the Phoenix artifact chain, not a flaw
specific to this candidate.

---

## Suggested Next Sequence

**Step 1 — Apply P0 and Recommended Amendments (Codex).**
Add the gate script delta section, the `release_scope` and
`installer_closes_release_blocker_scope` fields, the single-hardware disclosure,
and the post-acceptance next-action pointer to the wording candidate. No gate
fields change in this step.

**Step 2 — Codex records consensus.**
Codex records its consensus with this review. The consensus document must:
state the verdict (`accept-with-amendments-not-release`); confirm that P0
Amendments 1 and 2 were applied; and confirm that the two-field gate update
(`installer_closes_release_blocker: true` and `release_scope:
source_tree_pod_gated_eleven_row`) is the correct next gate state.

**Step 3 — Update the gate script (Codex).**
Apply exactly the changes specified in P0 Amendment 1:
- Set `installer_closes_release_blocker` to `True`.
- Add `installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row`.
- Add `release_scope: source_tree_pod_gated_eleven_row`.
- Update `required_next_action`.
Run the gate and confirm it returns `staged_pod_gate_present_general_release_installer_not_ready`
with `release_authorized: false` and `general_release_installer_ready: false`
unchanged.

**Step 4 — Close secondary hardware blocker (independent track).**
Begin work on the secondary RT-core performance blocker: either a second
RTX/RT-core machine run of the eleven M7 rows (or a validated subset), or an
explicit 2-AI-reviewed hardware-scoped waiver. This track is independent and can
be started now.

**Step 5 — Obtain a new aggregate release-readiness external review.**
After the installer blocker and secondary hardware blocker are both closed,
request a new external release-readiness review. That review must explicitly
supersede `claude_codex_consensus_current_eleven_row_not_release_ready_fix_p0`.
The new consensus must confirm that all P0 blockers from the current eleven-row
consensus are closed or waived by 2-AI review before `release_authorized: true`
can be recorded.

**Step 6 — Upgrade wording scanner (prerequisite for release candidate).**
Extend `v3_release_wording_gate.py` from first-pass to full release-authorization
scanner before any public release candidate is tagged.

---

This review does not authorize release. It does not change any gate field. The
aggregate release-readiness gate must continue to return `blocked_not_release`
until secondary hardware and external consensus P0 blockers are independently
closed. The only fields that may change after P0 amendments and Codex consensus
are `installer_closes_release_blocker` (to `true`),
`installer_closes_release_blocker_scope` (new field), and `release_scope` (new
field), all in `scripts/v3_phoenix_install_reproducibility_gate.py`, under the
exact `source_tree_pod_gated_eleven_row` scope.
