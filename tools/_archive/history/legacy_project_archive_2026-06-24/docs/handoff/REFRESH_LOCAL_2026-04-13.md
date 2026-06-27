# RTDL Local Operating Refresh

This file is stable operating memory for RTDL work. Read it regularly after
context compaction. Keep project, machine, environment, tool, review-flow, and
claim-boundary rules here. Do not use this file as a running goal ledger or
progress report; write goal progress to `docs/reports/`.

## Project Identity

- Primary repo:
  - `/Users/rl2025/rtdl_python_only`
- Project: RTDL, a Python-facing ray-tracing DSL/runtime for expressing
  RT-accelerated app kernels with strict claim boundaries.
- Development focus: make public examples/apps useful, correct, documented,
  and honest about which RT engine/path is actually used.
- Stable repo convention:
  - source under `src/`
  - examples/apps under `examples/`
  - tests under `tests/`
  - scripts under `scripts/`
  - reports/reviews under `docs/reports/`
  - handoff prompts under `docs/handoff/`
- Current release/version facts belong in release docs and reports, not in this
  refresh file.

## Current Phoenix V3 Guardrail

- Current version marker:
  `v3-capability-branch-2026-06-24`. This is not a release tag.
- Current top status as of 2026-06-24:
  Phoenix V3 Phase A is complete and did **not** prove a broad performance
  source. The project is now on Claude A-H **Phase H capability/quality branch**,
  not the Phase B high-performance path.
- Phase A consensus record:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_phase_a_performance_source_consensus_2026-06-24.md`.
  Claude and Antigravity both returned
  `accept_phase_a_no_go_enter_phase_h_capability_quality`.
- Barnes-Hut carry-forward:
  Barnes-Hut proved runtime trunk execution/residency/parity but stayed
  backend-bound. No more Barnes-Hut tuning. Do not resume the old M72
  blocker-targeting loop.
- RTNN carry-forward:
  RTNN clustered/262144 executed through the productized prepared-session runner
  with zero failed checks and runner-vs-legacy parity, but projected the frozen
  OptiX scorecard row only to `1.03622547722238x`, below the `>=1.20x` Phase A
  bar. Do not search for a third winner.
- Current V3 work:
  finish Phase H/G: capability/quality user surface, claim-boundary cleanup,
  version-truth cleanup, tutorial/example polish, and V4/history fencing. No
  broad V3-over-V2 speed wording.
- Current front-door tests:
  `py -3 -m unittest tests.v3_release_wording_gate_test tests.v3_public_docs_rebuild_surface_test tests.v3_rebuild_tutorial_surface_test`
  passed on 2026-06-24 after the Phase H front-door update.
- Non-authorization:
  No V3 release, all-app benchmark, public speedup wording, broad V3-over-V2
  wording, V4, embedding, C ABI, or external zero-copy claim is authorized.

## Local Machine And Environment

- Local macOS machine:
  - main bounded-correctness, documentation, Apple RT/MPS RT, and release-flow
    work platform.
  - not an NVIDIA/OptiX validation platform.
- Linux / RTX cloud pods:
  - primary NVIDIA/OptiX and RT-core validation platforms.
  - use consolidated pod batches; do not start/stop cloud per app.
  - install GEOS before strict correctness gates:
    `apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libgeos-dev pkg-config`.
  - install/point OptiX headers and CUDA explicitly before benchmarks.
- Windows:
  - bounded correctness/performance platform when available.
  - coordinate via files/reports, not ad hoc verbal relay.
- Shared/network/remote machines:
  - write self-contained handoff files when another agent/machine should act.
  - do not assume another machine has the same credentials, keys, branches, or
    dependencies.

## Tool Availability

- Shell:
  - prefer `rg`/`rg --files` for search.
  - use `apply_patch` for manual edits.
  - avoid destructive git commands unless explicitly approved.
- Claude CLI:
  - HARD RULE: on this Windows host, use the verified absolute binary below
    first; do not spend time rediscovering Claude, trying PATH, npx, or GUI
    assumptions before this route.
  - Windows local verified path:
    `C:\Users\Lestat\.local\bin\claude.exe`
  - Windows local verified version on 2026-06-21:
    `2.1.170 (Claude Code)`.
  - Windows local invocation, preferred/required for real review prompts:
    `$prompt | & 'C:\Users\Lestat\.local\bin\claude.exe' --print --dangerously-skip-permissions`
  - Current Phoenix helper scripts may instead use
    `--permission-mode bypassPermissions`; this is the verified noninteractive
    form used by
    `scripts/run_claude_phoenix_v3_m70_m71_backfill_2026_06_24.ps1`.
    Treat both flag forms as permission-bypass aliases for Claude Code 2.1.170,
    and prefer existing checked-in helper scripts over hand-rolled commands.
  - Do not pass long review prompts as positional command arguments on this
    host; use stdin. Positional prompt arguments have already produced dropped
    or cut-off review prompts in this repo.
  - 2026-06-21 re-check: this binary is usable by absolute path but is not
    discoverable through the current PowerShell `PATH`; do not rely on
    `Get-Command claude.exe` before trying the verified absolute path.
  - 2026-06-21 stdin check: piping a prompt into
    `& 'C:\Users\Lestat\.local\bin\claude.exe' --print --dangerously-skip-permissions`
    returned `stdin-ok`; use stdin for long review prompts to avoid argument
    quoting loss.
  - 2026-06-21 verified: stdin invocation above completed a 126s Phoenix V3
    review successfully. Do not use `Start-Process -ArgumentList @(...,
    "<prompt>")` for Claude review prompts here; that route dropped the prompt
    and returned "message got cut off".
  - 2026-06-22 re-verified after user correction: the local Claude binary is
    exactly `C:\Users\Lestat\.local\bin\claude.exe`, version
    `2.1.170 (Claude Code)`. Treat this as known state. Do not rediscover it,
    do not try PATH first, and do not fall back to `npx` before this absolute
    binary has actually failed.
  - 2026-06-22 Phoenix gate-update review attempt: the absolute Claude route
    was correct, but Claude returned
    `You've hit your session limit · resets 12am (America/New_York)`. Record
    this as a quota failure, not as "Claude not found", and do not rediscover
    the binary.
  - 2026-06-22 Phoenix bounded-review rule: for Phoenix V3 aggregate or
    release-level review, follow
    `docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md`.
    Use one complete review packet and one bounded automated Claude attempt per
    review cycle; do not use Gemini again until the user explicitly says the
    Google policy/tooling issue is solved. Save a verdict or record
    `external_review_not_obtained_<tool>_<reason>`, then continue non-release
    V3 engineering work. Do not loop on Claude availability, quota, PATH, auth,
    or rediscovery.
  - 2026-06-23 Phoenix M30-M33 bundle helper:
    `scripts/run_claude_phoenix_v3_m30_m33_bundle_review_2026_06_23.ps1`.
    It uses the verified absolute Claude binary, stdin prompt delivery, and
    `--add-dir`; prefer this script for that bundle instead of hand-rolling
    another command.
  - 2026-06-23 Phoenix M30-M34 Claude review succeeded through that helper.
    Recorded verdict:
    `docs/reviews/claude_phoenix_v3_m30_m34_bundle_recorded_review_2026-06-23.md`.
    2-AI consensus:
    `docs/reviews/codex_claude_phoenix_v3_m30_m34_2ai_consensus_2026-06-23.md`.
    It accepts continued non-all-app trunk-first work, not release/all-app.
  - Do not waste time re-discovering Claude on Windows and do not use
    `npx --yes @anthropic-ai/claude-code` as the first route here; this repo
    has already observed an incompatible Windows binary path through `npx`.
  - 2026-06-21 Phoenix note: Claude can be callable but temporarily fail with
    Anthropic `529 Overloaded`; record that as external-AI-unavailable evidence
    and continue engineering work instead of rediscovering the binary.
  - On other machines, may work with:
    `claude --print --dangerously-skip-permissions "<prompt>"`
  - if Claude hits quota/auth/tool failure, do not stop; record it and use
    Antigravity or another explicitly provided external-AI fallback. Do not call
    Gemini until the user explicitly re-enables it.
- Gemini CLI:
  - macOS historical path: `/opt/homebrew/bin/gemini`.
  - Windows path observed 2026-06-22:
    `C:\Users\Lestat\AppData\Roaming\npm\gemini.cmd`.
  - historical headless review:
    `gemini -p "<prompt>" --yolo`
  - 2026-06-22 Windows status: Gemini CLI exists, but direct invocation returns
    `IneligibleTierError` / `UNSUPPORTED_CLIENT` for Gemini Code Assist
    individuals. Treat this as tool/account unavailability, not "Gemini not
    found"; save the stderr as blocked-review evidence and continue engineering
    or use an explicitly labeled Codex subagent fallback only when the user
    accepts that it is not Claude/Gemini.
  - 2026-06-23 user rule: Google changed policy; do not call Gemini CLI again
    until the user says they have figured out and restored a working solution.
  - 2026-06-23 Phoenix M30, M31, M32, M33, M30-M33 bundle, and final M30-M33
    bundle attempts still returned `IneligibleTierError` /
    `UNSUPPORTED_CLIENT` with empty stdout. These attempts are not consensus.
  - 2026-06-23 Phoenix M30-M34 bundle-gate matrix status: `v3_rebuild` passed
    locally after M34 with 113 modules / 590 tests. This is local contract/gate
    evidence only; it is not external consensus, POD evidence, release
    authorization, all-app authorization, or a public performance claim. See
    `docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md` for current paths.
  - 2026-06-23 Phoenix M35 status: focused evidence gap ledger added at
    `docs/reports/phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md`
    with review request
    `docs/reviews/call_for_review_phoenix_v3_m35_focused_gap_ledger_2026-06-23.md`.
    M35 freezes RTDBSCAN component-signature and RayJoin point-location as
    structurally ready but not material, and redirects M36/M37 to generic
    grouped-reduction and component-union runner-callable core nodes. This is
    not release authorization and not all-app authorization.
  - 2026-06-23 Phoenix M35 matrix status: `v3_rebuild` passed locally with
    114 modules / 593 tests after adding the M35 focused-gap-ledger gate.
    This remains local contract/gate evidence only.
  - 2026-06-23 Phoenix M35 external status: Claude accepted M35 with verdict
    `accept_m35_gap_ledger_continue_m36`; recorded review:
    `docs/reviews/claude_phoenix_v3_m35_focused_gap_ledger_recorded_review_2026-06-23.md`;
    Codex+Claude consensus:
    `docs/reviews/codex_claude_phoenix_v3_m35_focused_gap_ledger_2ai_consensus_2026-06-23.md`.
    The only P1 was traceability: acknowledge M3.4's AABB recommendation and
    the later M30-M34 bundle redirect to grouped reduction. This P1 is applied.
  - 2026-06-23 Phoenix M36 local status: generic grouped vector-sum/reduction
    prepared-session helper added at
    `run_grouped_vector_sum_2d_prepared_session`; current surface ledger:
    `docs/reports/phoenix_v3_m36_prepared_session_step4_surface_ledger_2026-06-23.md`;
    M36 report:
    `docs/reports/phoenix_v3_m36_grouped_vector_sum_prepared_session_core_node_2026-06-23.md`.
    Local `v3_rebuild` passed with 115 modules / 600 tests. Claude accepted
    M36 with verdict `accept_m36_grouped_reduction_core_node_continue`;
    consensus:
    `docs/reviews/codex_claude_phoenix_v3_m36_grouped_reduction_core_node_2ai_consensus_2026-06-23.md`.
    Before focused grouped-reduction POD evidence, verify the real adapter
    reports `row_count` and `group_count`. No release/all-app or performance
    claim is authorized.
  - 2026-06-23 Phoenix M37 local status: generic component-union
    prepared-session helper added at
    `run_radius_graph_component_union_3d_prepared_session`; current surface
    ledger:
    `docs/reports/phoenix_v3_m37_prepared_session_step4_surface_ledger_2026-06-23.md`;
    M37 report:
    `docs/reports/phoenix_v3_m37_component_union_core_node_and_adapter_metadata_gate_2026-06-23.md`.
    Local `v3_rebuild` passed with 117 modules / 608 tests. M37 splits
    component-union accounting from component-signature accounting, fixes
    top-level `rtdsl` exports for current prepared-session helpers, and gates
    the real grouped-vector adapter `row_count`/`group_count` metadata path.
    Claude accepted M37 with verdict
    `accept_m37_component_union_core_node_continue`; consensus:
    `docs/reviews/codex_claude_phoenix_v3_m37_component_union_core_node_2ai_consensus_2026-06-23.md`.
    No release/all-app or performance claim is authorized.
  - Do not combine stdin prompt and `--prompt/-p` with Gemini CLI. It errors
    with `Cannot use both a positional prompt and the --prompt (-p) flag
    together`.
  - if Gemini prints an attempted write action but no file appears, save the
    stdout verdict manually into the required `docs/reports/` file and note the
    capture.
- Antigravity:
  - 2026-06-23 local status: GUI app exists at
    `C:\Users\Lestat\AppData\Local\Programs\Antigravity\Antigravity.exe`.
    CLI path installed by user:
    `C:\Users\Lestat\AppData\Local\agy\bin\agy.exe`.
    Verified locally with `--version`: `1.0.10`. The active terminal PATH may
    not include it until restart, so use the absolute path first.
    AgentAPI wrapper exists at
    `C:\Users\Lestat\.gemini\antigravity\bin\agentapi.bat`.
  - 2026-06-23 M53 probe: AgentAPI worked after setting
    `ANTIGRAVITY_LS_ADDRESS`, `ANTIGRAVITY_CSRF_TOKEN`, and
    `ANTIGRAVITY_PROJECT_ID` from the live language-server process/project.
    Do not persist or quote the CSRF token in docs. Default review flow remains
    Claude first; Gemini is disabled until the user restores it; Antigravity is
    still a fallback, not the normal path. Prefer the installed `agy.exe` CLI
    for future Antigravity review attempts before falling back to raw AgentAPI.
  - 2026-06-23 M56 probe: `agy.exe --print` returned exit code 0 with empty
    stdout/stderr, so empty CLI output must not be counted as review evidence.
    AgentAPI fallback with live `127.0.0.1:57805` produced the saved
    Antigravity review:
    `docs/reviews/antigravity_phoenix_v3_m56_goal_completion_audit_review_2026-06-23.md`.
    Use this order for future review attempts: Claude first; do not call
    Gemini; try `agy.exe --print`; if output is empty, use AgentAPI and require
    an actual saved verdict file.
  - 2026-06-23 M57 probe: `agy.exe --print` again returned exit code 0 with
    empty raw output. AgentAPI fallback produced:
    `docs/reviews/antigravity_phoenix_v3_m57_authorization_after_fail_closed_fix_review_2026-06-23.md`.
    Continue treating empty `agy.exe --print` output as no review.
  - 2026-06-23 M58 probe: `agy.exe --print` again returned exit code 0 with
    empty raw output. AgentAPI fallback produced:
    `docs/reviews/antigravity_phoenix_v3_m58_librts_authorized_rerun_intake_review_2026-06-23.md`.
  - 2026-06-23 M59 probe: `agy.exe --help` worked and showed `--print`, but
    `agy.exe --print` again returned exit code 0 with empty output, so it was
    not counted as review evidence. Current AgentAPI env names are
    `ANTIGRAVITY_LS_ADDRESS`, `ANTIGRAVITY_CSRF_TOKEN`, and
    `ANTIGRAVITY_PROJECT_ID`; do not use `ANTIGRAVITY_LS_CSRF_TOKEN`.
    Read the CSRF token from the live `language_server.exe` command line and
    do not persist it. PowerShell `$PID`/`$pid` is reserved; use a variable
    name like `$projectId` when scripting. For long AgentAPI prompts, send a
    single-line prompt that asks Antigravity to write the review file directly.
    M59 output:
    `docs/reviews/antigravity_phoenix_v3_m59_librts_yellow_open_decision_review_2026-06-23.md`.
- Cloud SSH keys:
  - user-provided key paths may differ from local Codex availability.
  - verify key existence before assuming a pod is unreachable.
- Pod setup:
  - always log bootstrap, environment, commands, and copy-back paths.
  - preserve failed artifacts/logs; do not overwrite failure history without a
    supersession report.

## Review and closure discipline

- Every bounded goal should have `2+` AI consensus before it is called closed.
- For this project, `2-AI consensus` means Codex plus at least one external AI:
  Claude, Antigravity, Gemini if the user later restores it, or another
  explicitly identified external AI.
  An internal Codex subagent does not satisfy the external-AI side of this
  rule.
- `3-AI consensus` means Codex plus two external AIs. Prefer Claude plus a
  directly callable second external AI when available. Gemini is currently
  disabled by user instruction until the user restores it; Antigravity review or
  another explicitly identified external-AI review may supply a seat when its
  saved file is in the repo.
- External review priority is: Codex calls Claude first. Do not call Gemini
  until the user explicitly re-enables it. Antigravity is only a temporary GUI
  fallback when Claude is not usable and the user is willing to forward a prompt
  or AgentAPI is already live.
- 2026-06-23 user clarification: occasional user-forwarded GUI fallback is
  acceptable, but the normal path is still Codex directly calling Claude.
  Gemini must not be called again until the user restores it. Antigravity exists
  to cover temporary GUI situations, not to replace the normal Claude-first
  review flow.
- External-style AI review should be saved into repo files. If an external AI
  returns a verdict in stdout but cannot write the file itself, save the stdout
  verdict into a repo report and note that capture path explicitly.
- Codex consensus is still required in addition to external-style review.
- Prefer file-based handoff and response-file review trails.
- Do not rewrite historical external reviews. If later evidence changes a
  conclusion, add a supersession report and update current public docs.
- For required `2-AI consensus`, if Claude is unavailable, immediately use
  Antigravity/user-provided GUI external review or another explicitly provided
  external AI, and save the verdict under `docs/reviews/` or `docs/reports/`.
  Do not use Gemini until the user re-enables it.
- Important planning, public claim changes, release decisions, or architecture
  changes should seek `3-AI consensus` unless the user explicitly narrows scope.
- 2026-06-23 user rule for Phoenix V3: for major decisions, or at least once
  every six hours during sustained work, obtain `2+` AI consensus. Any
  goal-completion audit must have `3-AI` review/consensus before the goal is
  called complete. Do not use a temporary external-tool outage as a reason to
  skip this; record review debt and continue only bounded, non-release,
  non-paid-POD engineering while preserving claim boundaries.
- Claude review debt register:
  `docs/reviews/phoenix_v3_claude_review_debt_register_2026-06-23.md`.
- Claude review-debt batch helper:
  `scripts/run_claude_phoenix_v3_review_debt_backfill_2026_06_23.ps1`.
- A review failure from Claude or the historical Gemini attempts is evidence to
  handle, not a reason to ignore the review requirement. New Gemini attempts are
  disabled until the user restores the tool.
- For Phoenix V3 specifically, the current handoff entry point is
  `docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`; older V3/V4
  handoffs are historical unless the current handoff cites them. Release-level
  external review must obey the bounded-review protocol above, so review-tool
  failure cannot become an infinite retry loop.

## Goal-Level Decision Self-Audit

For every goal-level decision, including decisions to continue, stop, reroute,
start a pod, accept a benchmark interpretation, change release wording, or
declare a scope complete, the acting AI must explicitly answer these four
questions in the user-visible update or saved report:

1. Was I foolish?
2. If yes, what actions made the decision foolish?
3. Was there another path that would have avoided getting stuck on that idea?
4. Can I now try a different path that actually solves the problem?

This is not optional process decoration. It is a recurring guard against
stale-memory work, repeated trivial setup mistakes, overbroad claims, and
single-path fixation. After context compaction, after any user correction, and
before any paid-pod or release-level action, reread this section and apply the
four-question audit before proceeding. During long-running work, repeat the
audit whenever the plan changes or a new goal-level decision is made.

## Platform honesty

- Linux and RTX cloud runs are the primary NVIDIA/OptiX validation platforms.
- Local macOS is a bounded correctness, Apple RT/MPS RT, documentation, and
  release-flow platform.
- Windows is a bounded correctness/performance platform when available.
- Do not overclaim backend or GPU correctness if row parity is not proven.
- `--backend optix` is not by itself a public NVIDIA RT-core speedup claim.
- Distinguish:
  - backend ran
  - native RT traversal ran
  - RT-core hardware was plausibly exercised
  - same-semantics baseline comparison supports a public speedup claim
- Do not quote same-backend warm/prepared ratios as RTX-vs-baseline speedups.
- Public RTX wording must follow the repo's current public wording matrix and
  saved review reports.

## Documentation And Report Rules

- Front-page docs, tutorials, examples, feature guides, architecture docs, and
  app docs must be consistent with current code before release.
- Public docs must be useful and attractive, but never overclaim performance,
  backend support, or release authorization.
- Goal/progress information belongs in `docs/reports/` and history/release
  docs, not in this refresh file.
- If a new external report arrives, read it, summarize defects, fix or rebut
  with evidence, and save a response report.
- For cloud runs, copy artifacts back and run local intake before interpreting
  results.
- Release-level work requires total tests, total docs update, total audit, and
  review-flow evidence.
- Phoenix V3 M38 current state: M38 accepted the focused component-union POD
  protocol through Codex+Claude consensus
  (`docs/reviews/codex_claude_phoenix_v3_m38_component_union_focused_pod_protocol_2ai_consensus_2026-06-23.md`).
  Do not run all-app or claim release performance. The next allowed step is
  M39 local harness work; only after the harness gate passes is one focused
  component-union POD run authorized.
- Phoenix V3 M39 current state: M39 local harness
  `scripts/v3_phoenix_component_union_m38_pod_ab.py` passed local gates and
  Codex+Claude consensus
  (`docs/reviews/codex_claude_phoenix_v3_m39_component_union_harness_2ai_consensus_2026-06-23.md`)
  authorizes exactly one focused component-union POD run. Use `--variant all`
  and `--require-rt-hardware`; do not run all-app; do not claim V3 release or
  public speedup from the run.
- Phoenix V3 M40 current state: the single M39-authorized focused
  component-union POD run has been executed on RTX 4000 Ada hardware and copied
  back to
  `docs/rebuild/v3/evidence/phoenix_v3_component_union_m39_focused_pod_ab_20260623_142706/`.
  Intake:
  `docs/reports/phoenix_v3_m40_component_union_focused_pod_intake_2026-06-23.md`.
  Preliminary result: exit code `0`, failed checks `0`, signatures match,
  productized runner records `runtime_trunk_executes_end_to_end=true`,
  runner-vs-Embree hot `1.221027x`, runner-vs-Embree wall `2.421405x`,
  runner-vs-legacy wall `1.254316x`, and runner-vs-legacy hot only
  parity/slightly slower at about `0.994x`. This is one positive Step-1 probe,
  not release evidence and not an all-app or public speedup authorization.
  Harness caveat fixed after the run: future real runs now emit a real-run
  status instead of the dry-run `not_pod_run` label and expose
  `runner_vs_legacy_hot_speedup`. Focused local validation after the fix ran
  9 tests OK; full `v3_rebuild` ran 119 modules / 620 tests OK. Claude M40
  review verdict:
  `accept_with_caveats_fix_harness_before_step2`. Codex+Claude consensus:
  `docs/reviews/codex_claude_phoenix_v3_m40_component_union_focused_pod_intake_2ai_consensus_2026-06-23.md`
  with verdict `accept_with_caveats_fixed_locally_continue_step2`. Step 2
  local implementation may proceed; no additional POD spend is authorized
  until Step-2 local work is reviewed.
- Phoenix V3 M41 current state: grouped reduction
  (`grouped_vector_sum_2d`) is selected as the second Step-2 local family after
  M40 component-union. Local harness:
  `scripts/v3_phoenix_grouped_reduction_m41_local_harness.py`; report:
  `docs/reports/phoenix_v3_m41_grouped_reduction_second_family_local_harness_2026-06-23.md`;
  review request:
  `docs/reviews/call_for_review_phoenix_v3_m41_grouped_reduction_second_family_local_harness_2026-06-23.md`.
  Focused tests ran 14 OK and full `v3_rebuild` ran 120 modules / 625 tests
  OK. Claude review is pending at
  `docs/reviews/claude_phoenix_v3_m41_grouped_reduction_second_family_local_harness_review_2026-06-23.raw.md`.
  No M41 paid POD, release, all-app, or public speedup action is authorized
  until recorded external review and Codex+external consensus are saved.
  M41 final state: Claude accepted the small local CUDA smoke only as a contract
  gate and required a serious free local run before paid POD. Serious free
  local run at 262144 rows / 1024 groups passed contract gates but runner-vs-CPU
  hot was `0.4979998501868343x`. Claude serious-result review verdict:
  `accept_contract_positive_paid_pod_blocked`; Codex+Claude consensus:
  `docs/reviews/codex_claude_phoenix_v3_m41_grouped_reduction_2ai_consensus_2026-06-23.md`.
  M41 is closed as contract-positive/performance-blocked. Do not request paid
  POD for grouped reduction. Next step is either grid-size/occupancy root-cause
  diagnosis before one bounded free-local shape experiment, or move Step-2
  performance evidence to another family.
- Phoenix V3 M42 current state: grouped-reduction low occupancy root cause has
  been diagnosed. The Numba offsets kernel parallelizes over `group_count`; at
  `262144` rows / `1024` groups it launches only
  `ceil(1024 / 256) = 4` blocks. Increasing row count at fixed `1024` groups
  does not improve occupancy, and reducing groups worsens it. M42 added generic
  launch-shape metadata to the prepared runner path
  (`v2_5_numba_offset_program_count`,
  `v2_5_numba_threads_per_block`,
  `v2_5_numba_launch_parallelism_axis`,
  `v2_5_numba_rows_per_group_mean`,
  `grouped_reduction_launch_shape`). One bounded free local lx1 shape run at
  `262144` rows / `65536` groups passed failed checks `0`, correctness
  `allclose=true`, runtime trunk executes end-to-end `true`, internal residency
  `true`, hot-path host materialization `false`, and runner-vs-CPU hot
  `6.443935850755532x`. Evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m42_lx1_shape_262144x65536_20260623_151852/`.
  Report:
  `docs/reports/phoenix_v3_m42_grouped_reduction_grid_occupancy_root_cause_2026-06-23.md`.
  Claude verdict and Codex+Claude consensus:
  `accept_m42_shape_positive_require_tiled_kernel` at
  `docs/reviews/codex_claude_phoenix_v3_m42_grouped_reduction_grid_occupancy_2ai_consensus_2026-06-23.md`.
  M42 proves shape-positive grouped-reduction trunk evidence, but does not close
  the family. The next authorized step is M43 local-only tiled/row-parallel
  grouped-reduction kernel work on the original blocked `262144 x 1024` shape.
  No paid POD, all-app run, release, public speedup claim, broad V3-over-V2
  claim, V4, embedding, C ABI, or true-zero-copy work is authorized.
- Phoenix V3 M43 current state: local-only grouped-reduction work added Numba
  tiled strategies and a productized CuPy prepared-session route. Numba tiled
  attempts improved but did not clear the original `262144 x 1024` CPU-hot
  inversion (`0.6216966017370773x` block-per-group, `0.6777200472439239x`
  warp-per-group). The CuPy RawKernel warp prepared runner did clear the
  original CPU-hot gate on free local lx1: failed checks `0`,
  runtime trunk executes end-to-end `true`, internal residency `true`,
  hot-path host materialization `false`, partner `cupy`, kernel strategy
  `warp_per_group_tiled`, program count `128`, runner-vs-CPU hot
  `3.454249350723889x`, runner-vs-legacy hot `6.670789510185146x`.
  A local trusted-offset follow-up fixed the inclusive-wall caveat for
  prevalidated/generated offsets: evidence
  `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_trust_offsets_262144x1024_20260623_154342/`,
  failed checks `0`, runner-vs-CPU hot `3.634392783864349x`,
  runner-vs-legacy hot `3.3163301846618403x`, runner-vs-legacy wall
  `15.409127696720203x`.
  Evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_original_262144x1024_20260623_153707/`.
  Full local `v3_rebuild` passed with `120` modules / `627` tests; JSON:
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m43_trust_offsets_followup_20260623_154700.json`.
  M43 is now closed for bounded Step-2 grouped-reduction technical purposes
  through user-provided Antigravity GUI external review plus Codex consensus.
  Antigravity verdict:
  `accept_m43_original_shape_hot_gate_cleared_continue_step2`.
  External review:
  `docs/reviews/antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_review_2026-06-23.md`.
  Codex+Antigravity consensus:
  `docs/reviews/codex_antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_2ai_consensus_2026-06-23.md`.
  This supersedes the earlier temporary external-review blocked state for M43
  only. Next authorized work is Step-2 scorecard synchronization and next-family
  planning under the same generic runtime-trunk discipline. No paid POD,
  all-app run, release, public speedup claim, broad V3-over-V2 claim, V4,
  embedding, C ABI, or true-zero-copy work is authorized.
  M44 Step-2 scorecard sync after M43:
  `docs/reports/phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md`.
  M44 call for review:
  `docs/reviews/call_for_review_phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md`.
  M44 Claude helper:
  `scripts/run_claude_phoenix_v3_m44_scorecard_sync_review_2026_06_23.ps1`.
  M44 recommendation, pending external review, is no all-app, no paid POD, and
  next local work should be M45 Barnes-Hut severe-regression root-cause audit as
  generic runtime-trunk work. This is not release/all-app/POD authorization and
  does not complete the current goal without 3-AI review.
  M45 read-only audit:
  `docs/reports/phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`.
  M45 call for review:
  `docs/reviews/call_for_review_phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`.
  M45 Claude helper:
  `scripts/run_claude_phoenix_v3_m45_barnes_hut_reaudit_review_2026_06_23.ps1`.
  M45 found that Barnes-Hut should be treated as focused-fix-covered for
  planning, pending full-suite validation, not as the next active coding target.
  Do not start more Barnes-Hut route tuning before external review. Next active
  local engineering should move to remaining non-covered scorecard blockers
  such as LibRTS Set-B parity or another Set-A app-win shortfall, pending
  external review.
  M46 LibRTS watch-row status:
  `docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md`.
  M46 call for review:
  `docs/reviews/call_for_review_phoenix_v3_m46_librts_set_b_watch_rows_status_2026-06-23.md`.
  M46 Claude helper:
  `scripts/run_claude_phoenix_v3_m46_librts_watch_rows_review_2026_06_23.ps1`.
  M46 keeps M27's accepted code fix but leaves the LibRTS OptiX cold and Embree
  stress watch rows open. Next work is M47 focused cold-start/stability protocol
  preparation, not all-app, not paid POD, and not a code rewrite before review.
  M47 LibRTS protocol draft:
  `docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`.
  M47 call for review:
  `docs/reviews/call_for_review_phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`.
  M47 Claude helper:
  `scripts/run_claude_phoenix_v3_m47_librts_stability_protocol_review_2026_06_23.ps1`.
  M47 defines two focused scenarios, eight paired samples each, alternating
  V2.14/current order, and green/yellow/red labels. It does not authorize a run
  or paid POD; only explicit external review can authorize exactly one focused
  LibRTS stability POD run.
  M47 local dry-run/intake harness:
  `scripts/v3_phoenix_m47_librts_stability_protocol.py`; tests:
  `tests/v3_phoenix_m47_librts_stability_protocol_test.py`. Focused validation
  passed (`py_compile`; `Ran 5 tests OK`). Dry-run evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_m47_librts_stability_protocol_dry_run_20260623/`
  with `execute=false`, `schedule_row_count=32`, and all claim flags false.
  Real execution requires `--execute` plus token
  `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`.
  M44 goal-completion audit remains open, not complete:
  `docs/reports/phoenix_v3_m44_goal_completion_audit_pending_3ai_2026-06-23.md`.
  Review packet:
  `docs/reviews/call_for_review_phoenix_v3_m44_goal_completion_audit_2026-06-23.md`.
  Antigravity/user-GUI prompt:
  `docs/reviews/antigravity_prompt_phoenix_v3_m44_goal_completion_audit_2026-06-23.txt`.
  Current prompt status: refreshed after M52 so a user-forwarded GUI fallback
  reviews the current packet, not the older M47-only completion shape.
  Antigravity GUI review:
  `docs/reviews/antigravity_phoenix_v3_m44_goal_completion_audit_review_2026-06-23.md`.
  Codex+Antigravity interim consensus:
  `docs/reviews/codex_antigravity_phoenix_v3_m44_goal_completion_audit_interim_2ai_consensus_2026-06-23.md`.
  Claude completion review:
  `docs/reviews/claude_phoenix_v3_m44_goal_completion_audit_recorded_review_2026-06-23.md`.
  Final 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m44_goal_completion_3ai_consensus_2026-06-23.md`.
  Antigravity verdict:
  `accept_m44_substantively_done_but_do_not_mark_complete_until_3ai`.
  Local review-debt/completion-gate validation:
  `docs/reports/phoenix_v3_m44_review_debt_gate_and_rebuild_validation_2026-06-23.md`.
  Claude helper:
  `scripts/run_claude_phoenix_v3_m44_goal_completion_audit_review_2026_06_23.ps1`.
  The current M44 process goal can be called complete because the required
  `3-AI` completion audit is saved. Claude review debt for M43-M52 must still
  be backfilled as discrete milestone reviews. This completion does not
  authorize release, POD, all-app, public speedup wording, or broad V3-over-V2
  claims.
  M48 local continuation while Claude is unavailable:
  `docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`.
  Review request:
  `docs/reviews/call_for_review_phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`.
  Claude helper:
  `scripts/run_claude_phoenix_v3_m48_librts_harness_execution_safety_review_2026_06_23.ps1`.
  M48 hardens the M47 harness with preflight, tree-specific cwd, fixture/contract
  mismatch checks, and current metadata failure red-classification. It ran no
  benchmark and authorizes no POD/all-app/release. Claude review debt for M48
  must also be backfilled.
  M49 current blocker queue refresh:
  `docs/reports/phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md`.
  Review request:
  `docs/reviews/call_for_review_phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md`.
  Claude helper:
  `scripts/run_claude_phoenix_v3_m49_current_blocker_queue_review_2026_06_23.ps1`.
  M49 says old M8 Spatial/RayJoin next-target wording is stale if read as route
  tuning; after M35 it is allowed only as generic topology-stream residency and
  full-M3 phase-accounting work. It authorizes no POD/all-app/release.
  M50 current state: the Spatial/RayJoin topology-stream M3 runner is now
  dry-run by default and requires both `--execute` and token
  `M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED` for any real run. Report:
  `docs/reports/phoenix_v3_m50_spatial_topology_stream_runner_fail_closed_2026-06-23.md`.
  Review request:
  `docs/reviews/call_for_review_phoenix_v3_m50_spatial_topology_runner_fail_closed_2026-06-23.md`.
  Claude helper:
  `scripts/run_claude_phoenix_v3_m50_spatial_topology_runner_fail_closed_review_2026_06_23.ps1`.
  This is a fail-closed safety gate only; it authorizes no POD, all-app,
  release, public speedup, V4, embedding, C ABI, or true-zero-copy work.
  Latest M44 completion direct-review attempt after M50: Claude returned a
  session-limit/quota reset and Gemini returned
  `IneligibleTierError / UNSUPPORTED_CLIENT`. Blocked record:
  `docs/reviews/external_review_blocked_phoenix_v3_m44_completion_claude_gemini_2026-06-23.md`.
  This does not satisfy the required `3-AI` completion audit.
  M51 current state: LibRTS authorized-run runbook prepared at
  `docs/rebuild/v3/phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md`.
  It does not run or authorize POD; it makes a future externally authorized
  focused LibRTS run exact, dry-run-first, separate-tree, and full-copy-back.
  M52 current state: POD runner authorization surface audited at
  `docs/reports/phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md`.
  Current Phoenix V3 execution whitelist is only M47 and M50 token-gated
  surfaces, and both are blocked for execution absent explicit external
  authorization. Historical `v3_phoenix_*pod*` scripts are not current
  authorization.
  Completion status: Claude explicitly accepted the saved Antigravity M44
  completion review as adequate for the original M44 objective while Claude
  reviewed the current packet through M52. Therefore the M44 process goal is
  complete pending Claude debt backfill. This is not release/POD/all-app
  authorization.
  M53 current state:
  `docs/reviews/call_for_review_phoenix_v3_m53_open_claude_debt_backfill_2026-06-23.md`;
  `docs/reviews/claude_phoenix_v3_m53_open_debt_backfill_recorded_review_2026-06-23.md`;
  `docs/reviews/codex_claude_phoenix_v3_m53_open_debt_backfill_2ai_consensus_2026-06-23.md`.
  Claude verdict:
  `accept_m53_open_debt_backfill_no_authorization_continue_m54`.
  Per-debt result: M43, M44-scorecard, and M45-M52 all accepted. This pays the
  open Claude bundle backfill at the technical-review level. M53 goal
  completion is now satisfied by the user-required 3-AI completion audit:
  Codex + Claude + Antigravity. M53 does not authorize
  POD/all-app/release/public speedup claims. Carry forward P1 items before any
  future LibRTS run: supply a real V2.14 root and explicit Linux/POD Python
  paths; do not use the dry-run placeholders literally.
  M54 recommended next item from Claude: prepare a separate bounded external
  review packet requesting authorization for exactly one focused LibRTS
  stability POD run using the M47/M48/M51 suite. This is a recommendation to
  prepare a review packet only, not authorization to run.
  M53 goal-completion audit:
  `docs/reports/phoenix_v3_m53_goal_completion_audit_pending_3ai_2026-06-23.md`.
  Review packet:
  `docs/reviews/call_for_review_phoenix_v3_m53_goal_completion_audit_2026-06-23.md`.
  Antigravity review:
  `docs/reviews/antigravity_phoenix_v3_m53_goal_completion_audit_review_2026-06-23.md`.
  Final 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m53_goal_completion_3ai_consensus_2026-06-23.md`.
  Antigravity prompt:
  `docs/reviews/antigravity_prompt_phoenix_v3_m53_goal_completion_audit_2026-06-23.txt`.
  Gemini M53 completion attempt:
  `docs/reviews/external_review_blocked_phoenix_v3_m53_completion_gemini_2026-06-23.md`.
  Gemini remains unavailable and is now disabled by user instruction until the
  user restores it, but the saved Antigravity review supplies the third
  external-AI seat for M53 completion only. M54 remains not authorized.
  Final M53 local validation after recording the Antigravity CLI/Gemini-disabled
  rule: `v3_rebuild` passed with module_count 126 and 644 tests in 77.784s.
  Captured output:
  `docs/reports/phoenix_v3_m53_v3_rebuild_after_antigravity_cli_rule_2026-06-23.stdout.txt`;
  stderr:
  `docs/reports/phoenix_v3_m53_v3_rebuild_after_antigravity_cli_rule_2026-06-23.stderr.txt`.
  M54 status: completed by 3-AI consensus. Claude authorized exactly one
  focused M47 LibRTS stability POD run with verdict
  `authorize_m47_one_focused_librts_stability_pod_run`; Antigravity accepted
  M54 goal completion with verdict
  `accept_m54_goal_complete_authorization_narrow_one_run_no_release`; Codex
  recorded final 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m54_goal_completion_3ai_consensus_2026-06-23.md`.
  The only authorized token is `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`, for
  one run of `scripts/v3_phoenix_m47_librts_stability_protocol.py` only. Before
  using the token, the executor must identify real current and V2.14 roots plus
  explicit Linux/POD Python paths, run the target-machine dry-run, and confirm
  `failed_check_count=0`. This does not authorize V3 release, all-app
  benchmarking, broad paid POD campaign, public speedup wording, broad
  V3-over-V2 claims, V4, embedding, C ABI, true-zero-copy claims, repeated M47
  runs, changed scenario parameters, or watch-row closure without later
  external review of copied evidence.
  M54 completion audit:
  `docs/reports/phoenix_v3_m54_goal_completion_audit_2026-06-23.md`.
  Final M54 validation: `v3_rebuild` passed with module_count 127 and 649 tests
  in 79.993s. Captured output:
  `docs/reports/phoenix_v3_m54_v3_rebuild_after_authorization_consensus_2026-06-23.stdout.txt`;
  stderr:
  `docs/reports/phoenix_v3_m54_v3_rebuild_after_authorization_consensus_2026-06-23.stderr.txt`.
  M55 status: completed by 3-AI consensus. The one M54-authorized M47 focused
  LibRTS stability POD run was executed on `NVIDIA RTX 4000 Ada Generation`
  driver `550.127.05` with current root `/root/rtdl_v3_rebuild_20260620/current`
  and V2.14 root `/root/rtdl_v3_rebuild_20260620/v2_14`. Current pod SSH key
  that worked: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`;
  plain `id_ed25519` failed and `id_ed25519_rtdl_codex` had local load
  permission failure. Target dry-run and execution evidence were copied back:
  `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_target_dry_run_20260623_2339/`;
  `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/`.
  M55 intake:
  `docs/reports/phoenix_v3_m55_librts_authorized_pod_run_intake_2026-06-23.md`.
  Claude verdict:
  `accept_m55_valid_red_watch_rows_open_no_rerun`.
  Antigravity verdict:
  `accept_m55_goal_complete_valid_red_no_rerun_no_release`.
  Final 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m55_goal_completion_3ai_consensus_2026-06-23.md`.
  Final read: both `optix_cold_single_shot` and `embree_32768_stress` remain
  `red_failure_watch_row_open` because `set_b_control_candidate_missing` appears
  in current metadata. The M54 token is consumed. No rerun, watch-row closure,
  release, all-app benchmark, public speedup wording, broad V3-over-V2 claim,
  V4, embedding, C ABI, or true-zero-copy claim is authorized. Next allowed work
  is local diagnosis/repair planning for `set_b_control_candidate_missing` and,
  only if needed, a future separate authorization packet.
  M55 completion audit:
  `docs/reports/phoenix_v3_m55_goal_completion_audit_2026-06-23.md`.
  Final M55 validation: `v3_rebuild` passed with module_count 128 and 653 tests
  in 76.999s. Captured output:
  `docs/reports/phoenix_v3_m55_v3_rebuild_after_valid_red_consensus_2026-06-23.stdout.txt`;
  stderr:
  `docs/reports/phoenix_v3_m55_v3_rebuild_after_valid_red_consensus_2026-06-23.stderr.txt`.

## Working style for this review

- Audit the current repo state.
- Prefer concrete findings over politeness.
- Keep the review grounded in saved docs, tests, and reports.
- Use generated audits where available, then save Claude/external-AI-style
  reviews and a two-AI consensus report for bounded goal closure. Do not call
  Gemini until the user restores the CLI/policy path.
- Before significant work, inspect current files; do not assume stale memory is
  current.
- Keep user updates concise but frequent during long-running work.
- When a task uses paid cloud, maximize local preparation first and batch cloud
  operations efficiently.

## Phoenix V3 stop-the-churn memory — 2026-06-24

- Current mandate: Phoenix V3 only. Do not resume V4, embedding, C ABI, public
  release wording, all-app benchmarking, or broad V3-over-V2 claims unless the
  user explicitly changes the mandate.
- Required roadmap: follow Claude's
  `docs/rebuild/v3/v3_completion_roadmap_2026-06-24.md` and the connected
  `STOP_THE_CHURN` / T1-T6 Barnes-Hut trunk documents. Progress means a named
  scorecard blocker moves on same-contract same-hardware evidence; process
  audits, review debt, green tests, and new milestone numbers are not progress.
- T1 Barnes-Hut POD evidence is saved at
  `docs/rebuild/v3/evidence/phoenix_v3_barnes_hut_t1_phase_residency_pod_20260624_054636/`.
  Result: current Numba CUDA prepared-session runner does **not** move the
  `set_a_barnes_hut_app_geomean_0_844x` blocker; runner/control geomean is
  `0.9986714962702791`, projected scorecard value is `0.8430749883157705`, and
  native RT fused symbols are present but fail closed as not implemented.
- Contract nuance that must not be forgotten: `aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract`
  permits "RT-native traversal or equivalent device payload accumulation" as an
  implementation requirement, but an implementation that uses CUDA kernels only
  is device-resident V3 evidence, **not** RT-core evidence. RT-core claims need
  a real OptiX pipeline / `optixTrace`.
- Next technical action: implement or reject T2 on the real native fused
  aggregate-tree/vector-sum path. If implementing a CUDA-only fused kernel,
  label it as generic device-resident fused accumulation and keep
  `rt_core_speedup_claim_authorized=false`.
- Phoenix V3 M72/T2 Barnes-Hut current result as of 2026-06-24:
  native CUDA device-resident fused aggregate-tree/vector-sum path now executes
  through the app front door mode `native_fused_vector_sum_cuda_device` and the
  productized prepared-session runner. Evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_m72_barnes_hut_native_leafdfs_t2_20260624_101218/`;
  report:
  `docs/reports/phoenix_v3_m72_barnes_hut_native_leafdfs_t2_result_2026-06-24.md`.
  The generic engine fix was prepared `target_leaf_dfs` plus DFS-interval
  containment in the native fused kernel. Result: blocker moved but did not
  clear parity; native-vs-Numba runner geomean `1.0650085688429665x`, projected
  scorecard value `0.8988672321034636x` from `0.844x`, `crosses_0_98=false`,
  `crosses_1_00=false`. This is real trunk progress but not V3 release
  readiness, not all-app authorization, and not RT-core evidence because the
  current native fused path is CUDA-only and does not call `optixTrace`.
- Major decisions need 3-AI consensus or an explicit documented review-debt
  record when the user allows debt; do not block ordinary trunk implementation
  on micro-review. If uncertain, consult Claude before changing direction.
