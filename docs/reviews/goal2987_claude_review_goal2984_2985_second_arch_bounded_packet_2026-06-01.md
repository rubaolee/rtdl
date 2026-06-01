# Goal2987 Claude Review: Goals 2984–2985 Second-Architecture Bounded Packet

Date: 2026-06-01

Verdict: `accept-with-boundary`

Reviewer: Claude (Sonnet 4.6)

## Scope

Independent review of Goal2984 (Barnes-Hut second-architecture profile policy) and
Goal2985 (RTX 4000 Ada seven-harness bounded packet) as requested by the
Goal2987 external review handoff.

Files reviewed:
- `docs/reports/goal2984_barnes_hut_second_arch_profile_policy_2026-06-01.md`
- `docs/reports/goal2985_rtx4000ada_second_arch_bounded_packet_2026-06-01.md`
- `docs/reports/goal2985_second_arch_bounded_packet_pod/goal2855_summary.json`
- `docs/reports/goal2985_second_arch_bounded_packet_pod/goal2803_barnes_hut.json`
- `scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2984_barnes_hut_second_arch_profile_policy_test.py`
- `tests/goal2985_rtx4000ada_second_arch_bounded_packet_test.py`

This review does not authorize release.

---

## Q1: Does Goal2984 make the bounded profile explicit without silently weakening the default?

**Yes.**

The runner defines two named profiles in `BARNES_HUT_CASE_PROFILES`:

```python
"default":            ((512, 16), (2048, 32), (8192, 32))
"second_arch_bounded": ((512, 16), (2048, 32))
```

The CLI argument `--barnes-hut-case-profile` uses `choices=sorted(BARNES_HUT_CASE_PROFILES)`
and defaults to `"default"`. Any unrecognized profile name raises `ValueError` in
`_barnes_hut_cases_for_profile`, so the gate is fail-closed.

Crucially, the profile only rewrites the Goal2803 command. The `packet_plan` function
records `barnes_hut_case_profile: None` on every non-Goal2803 row, making the
scope of the profile change machine-readable in the plan output. The `summarize_packet`
function embeds `barnes_hut_case_profile` and `barnes_hut_case_profile_boundary` in the
top-level summary JSON, so any consumer of the artifact can see the active profile
without parsing the plan separately.

The Goal2984 test suite verifies all three concerns:
1. `test_runner_declares_default_and_second_arch_profiles` — both profiles declared correctly.
2. `test_second_arch_profile_rewrites_only_goal2803_command` — no other harness is affected.
3. `test_default_profile_remains_full_profile` — the 8192:32 case is still present in the default.

**Finding:** Goal2984 is a clean, auditable, backward-compatible change. The default canonical
runner is unchanged. The bounded profile is an opt-in, named, and documented deviation.

---

## Q2: Does Goal2985 provide a valid clean 7/7 RTX 4000 Ada packet for the bounded scope?

**Yes.**

The `goal2855_summary.json` records:

| Field | Observed | Expected |
| --- | --- | --- |
| `status` | `pass` | `pass` |
| `all_pass` | `true` | `true` |
| `artifact_count` | `7` | `7` |
| `expected_artifact_count` | `7` | `7` |
| `dirty_artifacts` | `{}` | `{}` |
| `claim_boundary_violations` | `{}` | `{}` |
| `source_commit_consistent` | `true` | `true` |
| `source_commit` | `20b62a3eb21607a4e313b58fd8804de91e681f4e` | consistent |
| `v2_5_release_authorized` | `false` | `false` |
| `barnes_hut_case_profile` | `second_arch_bounded` | `second_arch_bounded` |

All seven artifact entries in `artifacts` have `status: "pass"`. All seven
execution entries have `returncode: 0` and `timed_out: false`.

The Goal2803 execution command is:

```text
--case 512:16 --case 2048:32
```

No `--case 8192:32` appears. This is consistent with the `second_arch_bounded` profile
and confirms that the 8192-body Embree baseline was not run on this second-architecture
machine.

### Barnes-Hut evidence quality

From `goal2803_barnes_hut.json`:

| Bodies | Embree total (s) | OptiX total (s) | Total speedup | Membership speedup | RT-core accel | Rows match |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 512 | 2.994 | 0.503 | 5.955x | 177.221x | true | true |
| 2048 | 59.169 | 3.773 | 15.681x | 696.740x | true | true |

Both rows are OptiX RT-core accelerated and pass shape parity. The OptiX membership
speedup is well above the 100x and 500x thresholds that the Goal2985 test asserts.

**Boundary note — validation policy for the 2048 case:** The artifact records
`validation_skipped: true` for the 2048-body row and reports
`membership_validation_policy: "first_case_reference_validation_plus_all_case_embree_optix_shape_parity"`.
This means the 512-body case received full reference validation (exact value
comparison between Embree and OptiX outputs), while the 2048-body case received
shape-parity validation only (row counts match, not exact values). The
`rows_match_between_backends: true` for the 2048 row reflects shape parity, not
value equality. This policy is established from prior goals and is explicitly
stated in the artifact — it is not new or hidden. However, **any future release
packet that cites the 2048-body measurement must state this validation scope
explicitly in release text**.

### Partner selection

CuPy was selected at 0.000418 s vs. torch at 0.000767 s (CuPy wins by a factor
of ~1.8x). The `selected_partner_reason: "cupy_wins_same_contract_timing"` is
consistent with the measured timings. Triton preview was not promoted
(`triton_preview_promoted: false`). The `triton_vector_sum_auto_selection_allowed: false`
field in the Barnes-Hut artifact confirms the Triton gate is enforced.

**Minor naming note:** The vector sum section records `torch_faster: true` alongside
`selected_partner: "cupy"`. Since CuPy (0.000418 s) is faster than torch (0.000767 s),
the field name is potentially confusing — it may record that torch beats Triton rather
than that torch beats CuPy. This naming ambiguity does not affect the selection logic
(which is unambiguous: `cupy_wins_same_contract_timing`) or any claim authorization,
but the field should be clarified before it is cited in release documentation.

**Finding:** Goal2985 delivers a valid 7/7 bounded packet. All artifacts pass, are clean,
and share a single consistent source commit. The profile limitation is transparent in
the summary JSON.

---

## Q3: Does this close the operational Gap from Goal2977 while keeping the policy question open?

**Yes.**

Goal2977 produced a 6/7 packet on RTX 4000 Ada because the 8192-body Embree CPU
baseline did not complete. Goal2984 and Goal2985 together close that gap at the
operational level: the second architecture now has a clean 7/7 packet at current main.

The policy question — can a future release packet state that second-architecture
Barnes-Hut evidence uses the bounded profile while the full profile is primary-architecture
evidence — remains explicitly open. The summary boundary string says "not a release
shortcut unless the release scope names this bounded tier," and `v2_5_release_authorized`
is false throughout.

The internal readiness module reflects this correctly:
- `allowed_next_actions` includes `triage_goal2985_second_arch_bounded_packet_before_release_packet`
  and `request_external_review_for_goal2985_before_release_packet`.
- `v2_5_release` remains in `blocked_actions`.
- `request_fresh_3ai_release_review_only_if_user_requests_release` is the correct
  terminal action.

**Finding:** The operational gap is closed. The policy gap is correctly kept open
pending user request and fresh 3-AI release consensus.

---

## Q4: Are any claims overbroad?

**No overbroad claims detected.**

The top-level summary `claim_boundary` has all six hazardous flags set to `false`:
`public_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`,
`paper_reproduction_claim_authorized`, `broad_rt_core_speedup_claim_authorized`,
`true_zero_copy_claim_authorized`, `v2_5_release_authorized`.

Per-artifact `claim_boundary_violations` is `{}` for all seven artifacts, meaning none
of the `FALSE_CLAIM_KEYS` in the runner are set to a non-false value in any artifact.

The toolchain metadata claim boundary is also clean:
- `compiler_fairness_claim_authorized: false`
- `multivendor_claim_authorized: false`
- `cross_compiler_fairness_claim_authorized: false`
- `public_speedup_wording_authorized: false`
- `release_authorized: false`

The Barnes-Hut membership speedup numbers (177x–697x) are striking, but they are
correctly framed as internal RT-core acceleration evidence. No public speedup wording
or broad RT-core claim is authorized anywhere in the artifact chain.

The Goal2984 report explicitly lists nine unauthorized claim categories in its
"Boundary" section, and the Goal2985 report repeats the same list. Both reports
contain the phrase "does not authorize" and are verified by the Goal2984 and Goal2985
tests respectively.

**Finding:** The claim boundary system is working correctly for both goals.

---

## Q5: What remains before a user-requested v2.5 release packet?

In order of operational priority:

1. **External review closure for Goals 2984–2985.** This review (Goal2987) provides
   the Claude side. A Gemini-equivalent review (Goal2986) is the partner. Both are
   in the handoff.

2. **Policy decision on second-arch Barnes-Hut scope.** A release packet must
   explicitly state which architectures use the full three-case Barnes-Hut profile and
   which use `second_arch_bounded`. This review finds the bounded profile is acceptable
   as a release evidence scope, subject to the conditions below.

3. **2048-body validation scope disclosure.** Any release text citing the 2048-body
   Barnes-Hut measurement must state that it uses shape-parity validation, not
   full reference validation.

4. **`torch_faster` field clarification.** The naming ambiguity in the vector sum
   output should be resolved before it appears in release documentation.

5. **Pending "triage before release packet" items.** The internal readiness module
   still lists triage obligations for Goals 2956, 2960, 2963, 2966, 2970, 2974,
   2982, 2983, and 2985 before any release packet is assembled.

6. **Compiler flag alignment and multivendor check.** `track_goal2897_compiler_flag_alignment_before_release_packet`
   and `track_goal2897_multivendor_or_second_arch_perf_check_before_release_packet`
   remain open in `allowed_next_actions`.

7. **Partner conformance release completeness.** `release_conformance_complete: false`
   in the partner conformance matrix means there are still descriptor-only cells that
   have not achieved pod runtime smoke status.

8. **User request.** The final v2.5 release packet requires an explicit user request
   followed by fresh 3-AI release consensus.

---

## Summary

| Question | Finding |
| --- | --- |
| Q1: Profile explicit without weakening default? | Yes. Named, documented, fail-closed, backward-compatible. |
| Q2: Valid clean 7/7 bounded packet? | Yes. All pass, clean commit, no violations, profile recorded. |
| Q3: Operational gap closed, policy gap open? | Yes. Correctly positioned. |
| Q4: Any overbroad claims? | No. All claim flags are false throughout the artifact chain. |
| Q5: What remains? | Policy decision, 2 minor artifact disclosures, triage obligations, user request. |

**Verdict: `accept-with-boundary`**

Goals 2984 and 2985 are technically sound and accomplish what they claim. The bounded
profile mechanism is auditable and non-silent. The second-architecture packet is a
valid clean 7/7 result. Two boundary conditions must be carried forward into any future
release packet that uses this evidence:

1. **Validation scope:** The 2048-body Barnes-Hut row uses shape-parity validation
   only. Release text must say so explicitly.
2. **Profile scope:** Any release packet citing second-architecture Barnes-Hut evidence
   must explicitly name the `second_arch_bounded` tier and state that the 8192-body
   Embree CPU baseline remains unmeasured on that architecture.

This review does not authorize v2.5 release. Final release requires a user request
and fresh 3-AI release consensus.
