# Claude Review: Phoenix V3 Secondary RT Hardware Scope Waiver

Reviewer: Claude Sonnet 4.6 (external, local Windows Claude Code)
Date: 2026-06-21
Files read:
- `docs/reviews/call_for_review_phoenix_v3_secondary_rt_hardware_scope_waiver_2026-06-21.md`
- `docs/rebuild/v3/v3_secondary_rt_hardware_scope_waiver_candidate_2026-06-21.md`
- `docs/rebuild/v3/v3_secondary_platform_strategy_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_eleven_row_release_readiness_review_2026-06-21.md`
- `scripts/v3_phoenix_secondary_platform_gate.py`
- `scripts/v3_phoenix_release_readiness_gate.py`

Verdict: `accept-with-amendments-not-release`

---

## Bottom Line

The waiver candidate is logically sound, scope-honest, and avoids every named
overclaim. It can close exactly one blocker — `secondary_rt_performance_confirmation_not_closed`
— under the explicit scope `single_rtx_4000_ada_driver_550_127_05_pod`, by
waiver rather than by second-machine confirmation. This mechanism was already
explicitly endorsed in the prior eleven-row Claude review: "either a second
RTX-class run or an explicit 2-AI-reviewed hardware-scoped waiver."

However, the two gate scripts are not currently wired to accept a waiver.
Before any fields flip in the gate output, three concrete P0 amendments must be
implemented and verified. Until those amendments exist and the gate scripts
produce the correct waiver-state output, this review is a conditional acceptance
only — no gate field changes, no release authorization.

`release_authorized` remains `false`. This review does not authorize V3 release.
This review does not supersede the current eleven-row consensus.

---

## Answers To The Five Review Questions

**Q1. Can this waiver close `secondary_rt_performance_confirmation_not_closed`
under the explicit scope `single_rtx_4000_ada_driver_550_127_05_pod`?**

Yes. The blocker name is `secondary_rt_performance_confirmation_not_closed`,
which is the absence of second-machine RT performance evidence. The waiver
candidate proposes to close it not by providing that evidence but by explicitly
narrowing the hardware claim so the blocker no longer applies: "V3 performance
evidence is scoped to one NVIDIA RTX 4000 Ada Generation pod; second-machine RT
core confirmation is not available and is not claimed." When the scope
explicitly excludes the missing evidence type, the blocker can close under that
scope. The mechanism is sound.

The pod identity is specific: `host 2bcb58b259e4`, `NVIDIA RTX 4000 Ada
Generation`, `driver 550.127.05`, `memory 20475 MiB`, `pci_bus_id
00000000:C1:00.0`, `ssh root@213.173.108.14 -p 11592`. This is enough
specificity to make the waiver machine-readable. The candidate correctly does
NOT claim this pod is a second hardware platform; it is the same hardware class
as the existing M7 evidence.

**Q2. Should `secondary_rt_performance_confirmation_authorized` remain `false`
while `secondary_platform_closes_release_blocker` becomes `true`?**

Yes. These two fields serve different semantic purposes and must be held apart:

- `secondary_rt_performance_confirmation_authorized: false` is a permanent
  factual statement: we have not confirmed RT performance on a second machine.
  This fact does not change when the waiver is accepted; it is the reason the
  waiver exists.
- `secondary_platform_closes_release_blocker: true` is a process statement: the
  named release blocker is considered closed by an accepted hardware-scoped
  waiver, not by actual second-machine confirmation.

The candidate correctly holds both simultaneously. Flipping `closes_release_blocker`
to `true` while keeping `confirmed_authorized` at `false` is not a
contradiction; it is the precise semantics of a hardware-scoped waiver. Any
implementation that conflates these two fields is incorrect.

**Q3. Are the proposed machine-readable fields complete enough for the gate
scripts?**

No — not yet. The proposed fields are semantically correct and complete as a
specification, but neither gate script currently has logic to produce or consume
them in the waiver state. Concrete gaps:

In `v3_phoenix_secondary_platform_gate.py`:
- `build_payload()` hardcodes `"secondary_platform_closes_release_blocker": False`
  at line 150 with no conditional path for waiver acceptance.
- The output does not include `secondary_rt_hardware_scope_waiver_reviewed`,
  `secondary_platform_closes_release_blocker_method`, or
  `secondary_platform_closes_release_blocker_scope`.

In `v3_phoenix_release_readiness_gate.py`:
- `REQUIRED_SECONDARY_PLATFORM_PHRASES` at lines 170–176 requires the literal
  string `"secondary_platform_closes_release_blocker: false"` from the strategy
  document. After the waiver, this will conflict with the updated strategy
  document.
- The check `secondary_platform_does_not_close_release_blocker` at lines 351–353
  asserts `secondary_platform_closes_release_blocker is False`. After waiver
  acceptance this assertion inverts and the structural pass will fail.
- `blocking_reasons` at lines 494–500 unconditionally includes
  `"secondary_rt_performance_confirmation_not_closed"`. After waiver acceptance,
  this must be removed or conditioned on the waiver flag.

These are implementation gaps, not conceptual ones. The required P0 amendments
below specify exactly how to close them.

**Q4. What exact P0 amendments are required before gate implementation?**

See the Required P0 Amendments section below.

**Q5. Does the candidate avoid V3 release authorization, broad V3-over-V2
speedup, package-install, second-hardware, and multi-GPU portability overclaims?**

Yes, without exception:

- `release_authorized: false` — explicitly present in proposed fields.
- `broad_v3_faster_than_v2_claim_authorized: false` — explicitly present.
- `multi_gpu_performance_portability_claim_authorized: false` — explicitly present.
- `secondary_rt_performance_confirmation_authorized: false` — explicitly present.
- Package-install: the Allowed Wording section contains no install claim; the
  Forbidden Wording section explicitly prohibits "V3 has a general package
  installer."
- Second-hardware: the candidate's own prose states "no second RT-core
  performance platform is claimed." The waiver explicitly acknowledges the RTX
  4000 Ada pod is the same class as the M7 evidence, not a second class.
- Multi-GPU portability: no wording implying RTX portability beyond the stated
  single pod appears anywhere in the candidate.

The Allowed Wording template is factually supportable as written. The Forbidden
Wording list covers all five major overclaim routes named in the call for review.
No overclaim is present in the candidate.

---

## Fields Allowed To Flip

The following fields may change from their current values when the P0 amendments
below are implemented and verified:

| Field | Current value | Allowed new value | Condition |
| --- | --- | --- | --- |
| `secondary_rt_hardware_scope_waiver_reviewed` | `false` / absent | `true` | P0 amendment 1 implemented and this review file passes gate phrase check |
| `secondary_platform_closes_release_blocker` | `false` | `true` | P0 amendment 1 implemented |
| `secondary_platform_closes_release_blocker_method` | absent | `reviewed_hardware_scoped_waiver` | P0 amendment 1 implemented |
| `secondary_platform_closes_release_blocker_scope` | absent | `single_rtx_4000_ada_driver_550_127_05_pod` | P0 amendment 1 implemented |

No other field may flip as a result of this waiver. The four fields above are
the complete and exclusive set of permitted changes.

## Fields That Must Remain False

The following fields must remain at their current false values regardless of
waiver acceptance. Any implementation that flips any of these is incorrect and
must be rejected:

| Field | Required value | Why it cannot change |
| --- | --- | --- |
| `secondary_rt_performance_confirmation_authorized` | `false` | The waiver exists precisely because second-machine RT confirmation was not obtained; the absence of the evidence is the semantic content of the waiver |
| `multi_gpu_performance_portability_claim_authorized` | `false` | One pod is not portability evidence; portability requires multiple distinct hardware configurations |
| `broad_v3_faster_than_v2_claim_authorized` | `false` | Same-row geomean is 1.012x with four V3 losses; this waiver does not affect the paired run evidence |
| `release_authorized` | `false` | Closing one blocker does not resolve the remaining four: `release_authorization_false`, `eleven_row_surface_still_too_narrow_for_major_release`, `broad_v3_faster_than_v2_claim_not_authorized`, `current_eleven_row_release_readiness_consensus_blocks_release` |
| `package_install_claim_authorized` | `false` | Installer is closed under `source_tree_pod_gated_eleven_row` scope only; general package-install remains unauthorized |

---

## Required P0 Amendments Before Implementation

### Amendment 1 — `v3_phoenix_secondary_platform_gate.py`

The gate script must be amended to detect and record waiver acceptance. When
this review file (`docs/reviews/claude_phoenix_v3_secondary_rt_hardware_scope_waiver_review_2026-06-21.md`)
exists and passes a required-phrase check, `build_payload()` must produce:

```python
"secondary_rt_hardware_scope_waiver_reviewed": True,
"secondary_platform_closes_release_blocker": True,
"secondary_platform_closes_release_blocker_method": "reviewed_hardware_scoped_waiver",
"secondary_platform_closes_release_blocker_scope": "single_rtx_4000_ada_driver_550_127_05_pod",
"secondary_rt_performance_confirmation_authorized": False,  # unchanged
"release_authorized": False,  # unchanged
```

Required phrases the gate must check in this review file before accepting the
waiver (the gate should require ALL of the following strings to be present):

```text
accept-with-amendments-not-release
secondary_rt_hardware_scope_waiver_reviewed
secondary_platform_closes_release_blocker: true
secondary_rt_performance_confirmation_authorized: false
release_authorized: false
single_rtx_4000_ada_driver_550_127_05_pod
This review does not authorize V3 release.
```

If this review file is absent or any required phrase is missing, the gate must
continue to return `secondary_platform_closes_release_blocker: False` and must
NOT produce the waiver-state output.

### Amendment 2 — `v3_phoenix_release_readiness_gate.py`

Three changes are required:

**2a. Update `REQUIRED_SECONDARY_PLATFORM_PHRASES`.**
Remove the literal string `"secondary_platform_closes_release_blocker: false"`
from this tuple and replace it with the waiver-state phrases:

```python
"secondary_rt_hardware_scope_waiver_reviewed: true",
"secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver",
"secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod",
```

Add a required-phrase check for this review file (the waiver review document)
to the gate's document phrase checks, using a subset of the required phrases
listed under Amendment 1.

**2b. Replace the `secondary_platform_does_not_close_release_blocker` check.**
The current check asserts `secondary_platform_closes_release_blocker is False`.
After waiver acceptance this check inverts and breaks the structural pass.
Replace it with two checks:

```python
"secondary_platform_closes_release_blocker_by_waiver": (
    secondary_platform_payload.get("secondary_platform_closes_release_blocker") is True
    and secondary_platform_payload.get("secondary_platform_closes_release_blocker_method")
        == "reviewed_hardware_scoped_waiver"
),
"secondary_rt_performance_confirmation_still_false_after_waiver": (
    secondary_platform_payload.get("secondary_rt_performance_confirmation_authorized") is False
),
```

Both checks must be `True` for a structural pass after the waiver.

**2c. Remove `secondary_rt_performance_confirmation_not_closed` from
`blocking_reasons`.**
After waiver acceptance the secondary RT blocker is closed by waiver. Remove
this string from the `blocking_reasons` list in `build_payload()`. The
remaining four blocking reasons are correct and must be preserved:

```python
"release_authorization_false",
"eleven_row_surface_still_too_narrow_for_major_release",
"broad_v3_faster_than_v2_claim_not_authorized",
"current_eleven_row_release_readiness_consensus_blocks_release",
```

### Amendment 3 — `docs/rebuild/v3/v3_secondary_platform_strategy_2026-06-21.md`

The current strategy document contains the literal string
`secondary_platform_closes_release_blocker: false`, which is currently a
required phrase in `REQUIRED_SECONDARY_PLATFORM_PHRASES`. After the waiver, the
gate will require waiver-state phrases instead. The strategy document must be
updated to reflect the waiver-accepted state. The update must:

1. Add a new section (e.g., "Waiver State") recording that the secondary RT
   hardware blocker is closed by the reviewed hardware-scoped waiver, not by
   second-machine confirmation.
2. Preserve the existing compatibility-only classification of `lx1` / GTX 1070.
3. Include the new machine-readable phrases that Amendment 2a will require,
   specifically:
   ```text
   secondary_rt_hardware_scope_waiver_reviewed: true
   secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver
   secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod
   ```
4. Remove or condition the phrase `secondary_platform_closes_release_blocker: false`
   so the current gate phrase check does not false-fail on the updated document.

---

## What This Waiver Does Not Close

Accepting this waiver closes exactly one of the five active blocking reasons.
The following four blocking reasons remain fully open and are not affected by
this waiver:

1. `release_authorization_false` — no explicit release decision exists.
2. `eleven_row_surface_still_too_narrow_for_major_release` — eleven row-scoped
   results on one hardware point do not constitute a major-release surface.
3. `broad_v3_faster_than_v2_claim_not_authorized` — 1.012x same-row geomean
   with four V3 losses; this evidence state is unchanged by the waiver.
4. `current_eleven_row_release_readiness_consensus_blocks_release` — the
   current eleven-row Claude+Codex consensus says `not-release-ready-fix-p0`
   and has not been superseded.

Additionally, this waiver does not close or affect any of the following:

```text
release_authorization_false
eleven_row_surface_still_too_narrow_for_major_release
broad_v3_faster_than_v2_claim_not_authorized
current_eleven_row_release_readiness_consensus_blocks_release
general_release_installer_not_ready (already closed by scope; unrelated to this waiver)
```

The aggregate release-readiness gate must continue to return `blocked_not_release`
after the amendments are implemented. The `--strict-release` flag must continue
to exit nonzero. No public release wording, no release tagging, and no
superseding of the current eleven-row consensus follows from this waiver.

---

## Scope Boundary Check

| Claim | Authorized by this waiver | Notes |
| --- | --- | --- |
| Single-RTX-4000-Ada-pod performance evidence, eleven exact M7 rows | Yes, with disclosure | Must cite pod identity exactly: `NVIDIA RTX 4000 Ada Generation`, `driver 550.127.05`, `host 2bcb58b259e4` |
| Second-machine RT-core performance confirmation | No | Explicitly absent; waiver acknowledges this |
| Multi-GPU or multi-RTX portability | No | One pod, one driver, one host |
| Broad V3-over-V2 speedup | No | Unchanged by waiver; remains unauthorized |
| V3 release authorization | No | Four remaining blockers are unaffected |
| Package-install claim | No | Unchanged by waiver; remains unauthorized |
| `lx1` / GTX 1070 as RT performance evidence | No | Compatibility-only classification unchanged |

---

## Implementation Sequence

1. Implement Amendment 1 in `v3_phoenix_secondary_platform_gate.py`.
2. Implement Amendment 3 in `v3_secondary_platform_strategy_2026-06-21.md`.
3. Implement Amendment 2 (a, b, c) in `v3_phoenix_release_readiness_gate.py`.
4. Run `v3_phoenix_secondary_platform_gate.py --pretty` and verify output
   contains `secondary_platform_closes_release_blocker: true`,
   `secondary_rt_hardware_scope_waiver_reviewed: true`, and
   `secondary_rt_performance_confirmation_authorized: false`.
5. Run `v3_phoenix_release_readiness_gate.py --pretty` and verify:
   - `status: blocked_not_release`
   - `release_authorized: false`
   - `blocking_reasons` contains the four remaining blockers and does NOT
     contain `secondary_rt_performance_confirmation_not_closed`.
   - `failed_checks` is empty (structural pass).
6. Run `v3_phoenix_release_readiness_gate.py --strict-release` and verify exit
   code is 1 (blocked, not structural fail).

Do not proceed to any form of release tagging, release consensus update, or
public release wording until a new aggregate release-readiness consensus
explicitly supersedes the current eleven-row `not-release-ready-fix-p0`
consensus.

---

This review does not authorize V3 release.
This review does not supersede the prior six-row Claude+Codex consensus.
This review does not supersede the current eleven-row Claude+Codex consensus.
The aggregate release-readiness gate must remain `blocked_not_release` until the
four remaining P0 blockers above are closed by concrete work and a new 2-AI
consensus.
