# Claude Recorded Review: Phoenix V3 M66 Topology-Stream POD Authorization Non-Go

Date: 2026-06-23
Reviewer: Claude (claude-sonnet-4-6)
Status: recorded external review; non-authorizing

## Verdict

`accept_m66_topology_stream_pod_authorization_rejected_continue_barnes_hut_pre_audit_no_pod_no_release`

The M66 packet is internally consistent. The local runner safety hardening is valid and
fail-closed. The non-go decision on a new RayJoin topology-stream POD run is correct and
well-supported by prior evidence. The redirect to Barnes-Hut phase-structure pre-audit is
the right next step. No blocking fixes are required before M66 completion.

---

## Q1: Is the local runner safety hardening valid and fail-closed?

**Yes.**

The runner enforces three independent gates before any workload call reaches hardware:

1. **Default dry-run.** `--execute` is not the default. Without it, `run_rayjoin_prepared_optix_workload`
   is never called. Verified by `test_main_defaults_to_dry_run_without_calling_workload`.

2. **Token gate.** When `--execute` is given, the code immediately checks
   `str(args.authorization_token) not in AUTHORIZED_EXECUTION_TOKENS` (runner.py:99-103)
   and raises `SystemExit` with a descriptive message before any preflight runs.
   The check is a string membership test, not a truthy check — an empty string or wrong token
   both fail. Verified by `test_main_execute_requires_authorization_token`.

3. **Preflight gate.** When `--execute` is given with the correct token, `execute_preflight`
   runs before `run_packet` is called (runner.py:104-113). If any required preflight step
   returns a non-zero exit code, errors dict is non-empty, and the runner writes
   `STATUS_FAILED` without calling the workload. Verified by
   `test_execute_aborts_before_samples_when_preflight_fails`.

Additionally, `validate_sample` (runner.py:418-440) raises `RuntimeError` at runtime if any
sample payload reports `release_authorized`, `public_speedup_claim_authorized`,
`row_scoped_public_speedup_claim_authorized`, `m7_promotion_authorized`, or
`true_zero_copy_claim_authorized` as True. This is an in-execution boundary, not just a
label. Verified by `test_validate_sample_rejects_authorized_claims`.

`require_full_m3` defaults to `True` (argparse line 149), so a partial M3 phase table aborts
the sample. The `--run-preflight` standalone mode also correctly does not call the workload.

One observation noted but not blocking: `_command_output` (runner.py:513-522) silently swallows
exceptions. This function is used only for non-required environment metadata
(`git_commit`, `nvidia_smi` in `run_packet`), not for any preflight gate. No safety gap.

**Safety hardening verdict: valid and fail-closed.**

---

## Q2: Does the M66 source-signature/preflight path prevent accidental POD samples before current code checks pass?

**Yes.**

The `current_topology_stream_source_signature` preflight step (runner.py:241-255) is marked
`required: True`. It runs the inline `CURRENT_SOURCE_SIGNATURE_SCRIPT` as a subprocess,
which checks 8 specific code invariants:

| Check | What it guards |
| --- | --- |
| `point_topology_runner_present` | Core runner function in prepared_execution.py |
| `segment_topology_runner_present` | Segment runner in prepared_execution.py |
| `m3_bridge_helper_present` | M3 bridge helper in prepared_execution.py |
| `step3_audit_bridge_gate_present` | M65 audit bridge gate in prepared_execution.py |
| `rayjoin_app_emits_m3_table` | App emits required phase table |
| `rayjoin_app_emits_prepared_handle` | App emits required handle |
| `runner_uses_m66_token` | Runner carries M66 token (prevents silent token rollback) |
| `runner_runs_preflight` | Runner calls `execute_preflight` (prevents silent bypass) |

The last two checks are self-referential: if the runner's own token or preflight call were
removed, the source-signature script would fail with `exit_code=1`, which flows into the
errors dict, which blocks execution and emits `STATUS_FAILED`. The M66 report records this
check passing: `failed: []`.

The `current_preflight_tests` step (runner.py:251-255) is also `required: True` and runs
four test modules including the negative hardening gate from M65. Both steps must pass before
any sample is collected.

**Preflight path verdict: prevents accidental POD samples.**

---

## Q3: Is the non-go decision correct given the prior serious RayJoin focused POD result?

**Yes, and the self-correction is the right process.**

The 2026-06-22 Step-2 RayJoin POD result established:

| Metric | Ratio |
| --- | ---: |
| Runner vs legacy hot query | `0.9735x` |
| Runner vs legacy total repeat | `0.9738x` |
| Runner vs legacy process wall | `0.7942x` |

The performance regression is not measurement noise. Claude's 2026-06-22 review diagnosed
the structural reason: both the productized runner and the legacy route call the same native
relation-status scalar-count executor; the legacy path already has `candidate_download: 0.0`,
so the runner's device-residency advantage has no elimination target. The runner adds
session-management overhead without compressing any dominant phase.

A new topology-stream RayJoin POD run would probe the same PIP scalar-count wrapper against
the same already-optimized executor on the same hardware. No new physical cost has been
introduced or identified that the runner could remove. The M66 report's goal-level audit
correctly identifies the foolish action: extrapolating from M65 local hardening to a new POD
authorization without rereading the prior focused evidence.

**Non-go decision verdict: correct. Prior evidence is controlling.**

---

## Q4: Should the next local runtime work redirect to Barnes-Hut phase-structure pre-audit rather than another RayJoin PIP wrapper run?

**Yes.**

The 2026-06-22 Claude review stated explicitly:

> Precondition before pod spend: audit the Barnes-Hut incumbent path's phase timing and
> confirm a non-zero download, host roundtrip, materialization phase, or repeated-planning
> phase exists for the runner to eliminate.

Two consecutive Set-A probes (RTDBSCAN and RayJoin PIP) have both returned structural-only
results. The common failure pattern is that the incumbent has already optimized the dominant
phase before the runner gets involved. The pre-audit protocol exists precisely to filter out
this failure before POD spend.

Barnes-Hut frontier/vector-accumulation is the candidate family because it is more likely
to have multi-phase physical cost: repeated host-device transfer between phases, repeated
planning overhead, or a continuation layer with enough accumulated work that fusing it
produces measurable savings. None of this is assumed — the pre-audit must confirm it first.

The M66 report's redirect path is correctly scoped: local pre-audit first, no focused A/B
until the pre-audit confirms a non-zero dominant phase the runner can compress.

**Redirect verdict: correct.**

---

## Q5: Are non-authorization boundaries preserved?

**Yes.**

All authorization flags in both `build_dry_run_packet` and `run_packet` are hardcoded
`False` at the source level. The flags covered are:

- `release_authorized`
- `public_speedup_claim_authorized`
- `row_scoped_public_speedup_claim_authorized`
- `broad_v3_faster_than_v2_claim_authorized`
- `whole_app_speedup_claim_authorized`
- `paper_reproduction_claim_authorized`
- `rtdl_beats_rayjoin_claim_authorized`
- `true_zero_copy_claim_authorized`
- `v4_embedding_claim_authorized`
- `m7_promotion_authorized`
- `m7_qualified_release_rows_added: 0`

In the summary dict, `all_app_pod_spend_authorized`, `focused_pod_spend_authorized_now`,
and `release_authorized` are also False. `validate_sample` enforces these at execution time.
The status labels (`STATUS_NOT_M7`, `STATUS_DRY_RUN`, `STATUS_PREFLIGHT_ONLY`,
`STATUS_FAILED`) contain no release language.

The M66 report's non-authorization section matches the call-for-review's required list
exactly. No softening, no silent omission.

**Non-authorization boundaries verdict: preserved.**

---

## Q6: What smallest fixes, if any, are required before M66 completion?

**No blocking fixes required.**

The packet is complete as written. The safety hardening is correct, the tests pass, the
source signature check passes, and the non-go decision is well-supported.

**P2 carry-forwards (not blocking M66, from prior reviews):**

- P2-A: `steady_state_stream` / `topology_continuation_sec` phase accounting is still
  measured at `0.001s` in test fixtures but was `0.0` with `no_separate_stream_phase_recorded`
  in actual execution (2026-06-22 review). Phase accounting must go from asserted to measured
  before any future Set-A candidate can be promoted. This is a pre-existing gap, not introduced
  in M66.
- P2-B: Process-wall overhead (`2.12s` runner vs `1.68s` legacy in Step-2) is real deployment
  cost. Cold-prepare overhead needs characterization before any release claim that the runner
  is deployment-equivalent to the legacy route.

These items belong in the Barnes-Hut pre-audit checklist, not in M66.

---

## Explicit Non-Authorization

This review does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- focused POD spend
- public speedup wording
- broad V3-over-V2 claim
- whole-app speedup claim
- paper reproduction claim
- RTDL-beats-RayJoin claim
- true-zero-copy claim
- future-version host integration work
- external device-buffer interop claim
- low-level host interface work
- watch-row closure

---

## Summary

M66 is correctly scoped. The hardening is real, the non-go is correct, and the redirect to
Barnes-Hut pre-audit follows the exact protocol established by the prior Claude review. Accept
M66 as a local hardening and non-authorization packet. No POD spend. No release. Proceed to
Barnes-Hut phase-structure pre-audit.
