# Phoenix V3 M54 One Focused LibRTS Stability POD Authorization 2-AI Consensus

Date: 2026-06-23

Status: `m54_one_focused_librts_stability_pod_authorized_by_codex_claude_only`

Consensus verdict:

```text
authorize_m47_one_focused_librts_stability_pod_run
```

Allowed token for exactly one focused run:

```text
M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED
```

## Scope

This consensus covers only one execution of:

```text
scripts/v3_phoenix_m47_librts_stability_protocol.py
```

with `--execute --authorization-token M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`.

The run must use:

- two scenarios: `optix_cold_single_shot` and `embree_32768_stress`;
- eight paired samples per scenario;
- seed `2025`;
- alternating V2.14/current order;
- full preflight capture;
- separate current and V2.14 roots;
- explicit Linux/POD Python executable paths for both trees;
- full copy-back of `summary.json`, `README.md`, preflight stdout/stderr, and
  per-command stdout/stderr.

## Consensus Seats

| Seat | AI | Verdict | Evidence |
| --- | --- | --- | --- |
| 1 | Codex | `authorize_m47_one_focused_librts_stability_pod_run` with executor preconditions | `docs/reviews/call_for_review_phoenix_v3_m54_one_focused_librts_stability_pod_authorization_2026-06-23.md`; local M54 gate |
| 2 | Claude | `authorize_m47_one_focused_librts_stability_pod_run` | `docs/reviews/claude_phoenix_v3_m54_one_focused_librts_stability_pod_authorization_recorded_review_2026-06-23.md` |

## Required Executor Preconditions

Before running with `--execute`, the executor must:

1. identify a real V2.14 root on the Linux/POD target;
2. identify explicit Linux/POD Python paths for current and V2.14;
3. run the M51 dry-run shape on the target machine with those real paths;
4. confirm the dry-run has `failed_check_count=0`;
5. then and only then run the exact authorized command with the token above.

Do not copy the local Windows dry-run command lines literally. They contain
local development-machine paths and are not execution commands.

## Non-Authorization

This consensus does not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no second or subsequent M47 run
- no modification of scenario parameters, sample count, or seed
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
- no watch-row closure without a later external review of copied evidence

## Goal-Level Decision Audit

Decision: accept Claude's M54 verdict as sufficient 2-AI authorization for one
focused LibRTS stability POD run, while keeping M54 goal completion pending the
user-required 3-AI completion audit.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   treating this as release/all-app authorization, or running from the local
   Windows dry-run paths.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Keep the authorization narrow, require target-machine dry-run first, and
   record the third AI audit separately before closing M54.
4. Can I now try a different path that actually solves the problem? Yes. Use the
   exact token-gated one-run authorization to collect the missing LibRTS
   stability evidence, then require external review of copied evidence before
   interpreting closure.
