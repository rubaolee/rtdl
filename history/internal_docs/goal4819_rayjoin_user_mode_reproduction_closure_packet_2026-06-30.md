# Goal4819 — RayJoin User-Mode Reproduction Closure Packet

Date: 2026-06-30

Status: `goal4819_closure_packet_complete_pending_external_review`

This packet closes the current user-mode RayJoin paper-reproduction attempt for
external review. It does **not** close the thread goal by itself and does not
authorize RTDL runtime development.

## Scope Being Judged

Question:

Can a user, using released RTDL v2.14 + Python + Numba partner where available,
reproduce the RayJoin Section 5.7 polygon overlay workload without modifying
RTDL runtime/native code?

Constraints:

- treat the executor as a user/application author, not an RTDL developer;
- do not edit `src/rtdsl/**`, `src/native/**`, or release surface;
- separate bundled-helper evidence from generic RTDL+Numba evidence;
- do not run performance until correctness passes;
- do not treat scalar LSI/PIP counts as full polygon overlay reproduction.

## Evidence Chain

### Goal4816-A — Paper/source contract

File:

`history/internal_docs/goal4816_A_rayjoin_section57_paper_source_contract_extraction_2026-06-30.md`

Outcome:

- Section 5.7 is full polygon overlay: LSI, vertex PIP, midpoint PIP,
  output-chain assembly, and author output semantics.
- The author reply establishes a deterministic PIP tie-break requirement:
  slope-dependent `t_reported`, not just equal-tie acceptance.

### Goal4816-B — v2.14 capability map

File:

`history/internal_docs/goal4816_B_rayjoin_v2_14_asset_capability_map_2026-06-30.md`

Outcome:

- v2.14 contains useful RayJoin assets.
- The complete overlay route relies on bundled RayJoin helper/application logic.
- Generic primitive + Numba route is not proven complete for Section 5.7.

### Goal4816-C/D — user-mode design and smoke plan

Files:

- `history/internal_docs/goal4816_C_rayjoin_app_only_reproduction_design_2026-06-30.md`
- `history/internal_docs/goal4816_D_rayjoin_correctness_preflight_smoke_plan_2026-06-30.md`

Outcome:

- execution must stay in user mode;
- first smoke should test bundled helper correctness;
- generic+Numba should be treated as a capability probe;
- performance is not authorized until correctness passes.

### Goal4817 — user-mode correctness smoke

File:

`history/internal_docs/goal4817_rayjoin_user_mode_correctness_smoke_execution_2026-06-30.md`

Outcome:

- clean v2.14 checkout could build/load OptiX.
- RTDL bundled helper ran on tiny fixture and author public sample.
- author binary reproduced the author public sample answer byte-for-byte.
- RTDL bundled helper did **not** byte-match the author public sample answer.
- existing `RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES=1` did not change RTDL output.
- generic+Numba was blocked/unproven in the clean environment:
  - Numba was not installed;
  - no complete public overlay assembly route was identified without bundled
    RayJoin helper code.

### Goal4818 — correctness-gap diagnosis

File:

`history/internal_docs/goal4818_rayjoin_public_sample_correctness_gap_diagnosis_2026-06-30.md`

Outcome:

- RTDL and author agree on LSI count for the public sample: 20,860
  intersections.
- RTDL output is missing six 2-point output chains versus author answer.
- RTDL has no extra coordinate records; the six omissions cascade into many
  chain/face-id differences.
- released RTDL's PIP equal-height tie policy differs from author
  source/reply:
  - author says map0 prefers larger slope and map1 prefers smaller slope;
  - RTDL native code currently chooses the opposite direction in its internal
    equal-height comparison;
  - RTDL's equal-ties env knob uses `nextafterf(report_t, +inf)` and does not
    implement slope-dependent `t_reported`.

### Goal4818 side audit — Numba partner support

File:

`history/internal_docs/goal4818_numba_partner_support_audit_2026-06-30.md`

Outcome:

- v2.14 does support Numba as an explicit partner for selected continuation
  contracts.
- For RayJoin Section 5.7, Numba evidence is route-specific
  (`compact_mask`, topology/reference continuation), not a complete overlay
  reproduction engine.

## Decision

Recommended closure label:

`blocked_by_released_rtdl_pip_sos_contract_gap`

Supporting labels:

- `bundled_helper_runs_but_not_exact_author_reproduction`
- `generic_primitive_numba_reproduction_not_proven`
- `performance_runs_blocked_by_correctness_failure`

## Why This Is The Correct Closure

The reproduction line failed at correctness before performance.

The author public sample is the smallest decisive test:

- it has author input and author answer;
- author binary reproduces the answer byte-for-byte on this POD;
- released RTDL bundled helper does not.

Because byte-equality fails on this public sample, running larger Section 5.7
data would only produce larger unverifiable outputs. It would be foolish to
spend POD time on performance or full-input runs before resolving this
correctness gap.

Because the current role is RTDL user/application author, not RTDL developer,
the correct action is not to patch RTDL. The correct action is to record that
released RTDL v2.14 lacks the exact author-compatible PIP/SoS behavior required
for byte-equivalent RayJoin overlay reproduction.

## What Would Be Needed In A Separate Future Product Goal

This is outside the current user-mode reproduction goal, but the required
product work is now clear:

1. expose or implement an author-compatible RayJoin CDB PIP/SoS contract;
2. implement slope-dependent `t_reported` or an equivalent deterministic
   OptiX-safe tie-break;
3. make the slope preference match the author contract:
   - map0 larger slope;
   - map1 smaller slope;
4. expose a clean, public, non-private overlay row/assembly contract if the
   project wants generic RTDL+Numba reproduction rather than bundled helper
   reproduction;
5. rerun author public sample correctness before any Section 5.7 performance.

## Non-Authorization

This packet does not authorize:

- runtime/native edits;
- performance benchmarks;
- public reproduction claims;
- generic RTDL+Numba reproduction claims;
- full 8/8 Section 5.7 claims;
- v3/v4 work.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   No. The closure follows a falsifiable correctness failure and avoids both
   performance theater and runtime patching.

2. **What would make this foolish?**
   Continuing to performance, calling the near-match a success, or changing RTDL
   while pretending to be a user.

3. **Is there another path that avoids being stuck?**
   Yes. Close this user-mode reproduction as a released RTDL capability gap,
   then create a separate product-development goal if the user wants RTDL fixed.

4. **Can I start a different path that truly solves the problem?**
   Yes, but only as future RTDL development, not inside this user-mode paper
   reproduction. The future path is to implement/expose the author-compatible
   PIP/SoS contract and then rerun correctness.

