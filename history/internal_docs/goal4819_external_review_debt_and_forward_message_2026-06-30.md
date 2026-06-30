# Goal4819 External Review Debt And Forward Message

Date: 2026-06-30

Status: `external_review_pending_manual_forward`

Update after user-forwarded Antigravity review:

- Goal4818 correctness-gap diagnosis is now reviewed and approved by
  Antigravity with verdict
  `approve_goal4818_gap_diagnosis_authorize_closure_packet`.
- Recorded review:
  `history/internal_docs/antigravity_goal4818_rayjoin_correctness_gap_review_2026-06-30.md`
- Remaining external review debt: Goal4819 closure decision.

## Why This Exists

Goal4819 is the closure packet for the current RayJoin user-mode reproduction
attempt. It recommends closing the current line as:

`blocked_by_released_rtdl_pip_sos_contract_gap`

This is a significant decision, so it needs independent review before the thread
goal can be considered closed.

## Local Reviewer CLI Status

Available local reviewer CLIs checked:

- `claude`: not found
- `claude-code`: not found
- `agy`: found at `C:\Users\Lestat\AppData\Local\agy\bin\agy.exe`

Antigravity `agy --print` was tested with a minimal prompt:

```text
Reply with exactly: AGY_OK
```

Result:

- process exit code: `0`
- stdout: empty
- requested log file: not created

Therefore the local Antigravity CLI is not currently a reliable review channel
from this Codex session. No external verdict has been obtained for Goal4819.

## Files For Reviewer

Primary file:

`history/internal_docs/goal4819_rayjoin_user_mode_reproduction_closure_packet_2026-06-30.md`

Supporting files:

- `history/internal_docs/goal4816_A_rayjoin_section57_paper_source_contract_extraction_2026-06-30.md`
- `history/internal_docs/goal4816_B_rayjoin_v2_14_asset_capability_map_2026-06-30.md`
- `history/internal_docs/goal4816_C_rayjoin_app_only_reproduction_design_2026-06-30.md`
- `history/internal_docs/goal4816_D_rayjoin_correctness_preflight_smoke_plan_2026-06-30.md`
- `history/internal_docs/goal4817_rayjoin_user_mode_correctness_smoke_execution_2026-06-30.md`
- `history/internal_docs/goal4818_rayjoin_public_sample_correctness_gap_diagnosis_2026-06-30.md`
- `history/internal_docs/goal4818_numba_partner_support_audit_2026-06-30.md`
- `history/internal_docs/antigravity_goal4818_rayjoin_correctness_gap_review_2026-06-30.md`
- `history/internal_docs/goal4817_artifacts_2026-06-30/`
- `history/internal_docs/goal4818_artifacts_2026-06-30/`

## Message To Forward To Claude Or Antigravity

Please review Goal4819:

`history/internal_docs/goal4819_rayjoin_user_mode_reproduction_closure_packet_2026-06-30.md`

This packet asks whether the current RayJoin user-mode paper-reproduction line
should close as:

`blocked_by_released_rtdl_pip_sos_contract_gap`

Goal4818's correctness-gap diagnosis has already received Antigravity approval:

`history/internal_docs/antigravity_goal4818_rayjoin_correctness_gap_review_2026-06-30.md`

Context:

- The executor is constrained to behave as an RTDL user/application author.
- Runtime/native/release-surface edits are forbidden.
- Performance runs are forbidden until correctness passes.
- Bundled RayJoin helper evidence must not be presented as generic RTDL+Numba
  language evidence.

Key evidence:

1. Author public sample inputs and answer are present.
2. Author `polyover_exec -mode=rt -output ...` reproduces the public sample answer
   byte-for-byte on the POD.
3. Released RTDL v2.14 bundled helper runs on the same public sample but does not
   byte-match the author answer.
4. RTDL and author agree on LSI count: 20,860 intersections.
5. RTDL output is missing six 2-point output chains; these omissions cascade
   into broader chain/face-id differences.
6. Author source/reply require map0 larger-slope and map1 smaller-slope PIP tie
   handling via slope-dependent `t_reported`.
7. Released RTDL native code uses the opposite equal-height slope preference and
   its `RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES=1` knob only applies
   `nextafterf(report_t, +inf)`, which did not change the output hash.
8. v2.14 supports Numba as a first-class explicit partner for selected
   continuation contracts, but not as a complete RayJoin Section 5.7 overlay
   reproduction route.

Please answer with one verdict label:

- `approve_goal4819_close_user_mode_reproduction_as_released_rtdl_pip_sos_gap`
- `approve_with_required_amendments`
- `fail_redo_closure_packet`
- `block_due_to_overclaim_or_missing_evidence`

Specific questions:

1. Does the packet correctly preserve the user-mode boundary?
2. Does the author public sample byte-equality failure justify blocking exact
   reproduction?
3. Does the Goal4818 diagnosis support the `released_rtdl_pip_sos_contract_gap`
   label?
4. Is the Numba partner status described accurately?
5. Does the packet avoid presenting bundled-helper evidence as generic RTDL
   language evidence?
6. Should performance runs remain blocked until correctness is fixed?
7. Is more user-mode evidence required before closing, or is this enough to close
   the current line as a released capability gap?

Non-authorization:

Do not authorize runtime/native edits, performance benchmarks, public
reproduction claims, generic RTDL+Numba reproduction claims, full 8/8 Section
5.7 claims, or v3/v4 work.
