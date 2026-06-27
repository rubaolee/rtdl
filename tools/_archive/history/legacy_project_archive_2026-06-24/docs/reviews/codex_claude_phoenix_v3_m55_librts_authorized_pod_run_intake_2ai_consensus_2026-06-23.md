# Phoenix V3 M55 LibRTS Authorized POD Run Intake 2-AI Consensus

Date: 2026-06-23

Status: `m55_valid_red_watch_rows_open_no_rerun`

Consensus verdict:

```text
accept_m55_valid_red_watch_rows_open_no_rerun
```

## Scope

This consensus reviews the copied evidence from the single M54-authorized M47
focused LibRTS stability POD run.

Evidence intake:

- `docs/reports/phoenix_v3_m55_librts_authorized_pod_run_intake_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_target_dry_run_20260623_2339/`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/`

Claude review:

- `docs/reviews/claude_phoenix_v3_m55_librts_authorized_pod_run_intake_recorded_review_2026-06-23.md`

## Consensus Read

M55 was within the exact M54 one-run authorization:

- target-machine dry-run ran first;
- dry-run used real current and V2.14 roots;
- dry-run used explicit Linux/POD Python paths;
- dry-run had `failed_checks=[]`;
- execution used `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`;
- execution completed with rc=0;
- copy-back includes the required summary, README, preflight stdout/stderr, and
  all measured stdout/stderr artifacts.

Both scenarios remain open/red:

| Scenario | M47 label | Geomean | Median | Pass count >=0.95 | Consensus read |
| --- | --- | ---: | ---: | ---: | --- |
| `optix_cold_single_shot` | `red_failure_watch_row_open` | 0.984404x | 0.979645x | 6/8 | valid red/open |
| `embree_32768_stress` | `red_failure_watch_row_open` | 0.931885x | 0.941006x | 4/8 | valid red/open |

The decisive failure is:

```text
set_b_control_candidate_missing
```

Claude's interpretation is accepted: this is a valid M47 red result, not a
green/yellow closure and not an invalid copy-back. The missing metadata means
the productized Set-B control path cannot be asserted from this run.

## Next Allowed Action

Allowed:

- record M55 as valid red evidence;
- keep both LibRTS watch rows open;
- diagnose why `set_b_control_candidate_missing` appears locally/off-POD;
- prepare a future separate repair and authorization packet if another run is
  needed.

Not allowed:

- no rerun from this authorization;
- no watch-row closure;
- no public speedup wording;
- no release/all-app claim.

## Non-Authorization

This consensus does not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no second M47 run
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
- no watch-row closure

## Goal-Level Decision Audit

Decision: accept M55 as a valid red/open intake and keep the authorization token
consumed, with no rerun or closure.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   using near-parity optix numbers to imply closure, or rerunning after the
   metadata failure without a new authorization.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Treat the run as exactly what the protocol says: valid red evidence,
   with missing metadata as the failure that must be diagnosed separately.
4. Can I now try a different path that actually solves the problem? Yes. Close
   this execution/intake goal only after 3-AI audit, then start a separate local
   diagnosis/repair goal for `set_b_control_candidate_missing`.
