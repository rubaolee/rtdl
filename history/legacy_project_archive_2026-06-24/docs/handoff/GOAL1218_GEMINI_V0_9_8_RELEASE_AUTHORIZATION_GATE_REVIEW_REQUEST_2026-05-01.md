# Goal1218 External Review Request

Please review Goal1218 as an external AI reviewer for RTDL.

## Scope

Goal1218 is a v0.9.8 release-authorization gate. It is not a release action:
it must not tag, publish, push, upload packages, or bump `VERSION` to `v0.9.8`.

The gate separates:

- local/hardware evidence readiness;
- public-claim boundary;
- actual release authorization.

## Files To Review

- `scripts/goal1218_v0_9_8_release_authorization_gate.py`
- `tests/goal1218_v0_9_8_release_authorization_gate_test.py`
- `docs/reports/goal1218_v0_9_8_release_authorization_gate_2026-05-01.json`
- `docs/reports/goal1218_v0_9_8_release_authorization_gate_2026-05-01.md`
- supporting current evidence:
  - `docs/reports/goal1216_v0_9_8_release_candidate_audit_2026-05-01.md`
  - `docs/reports/goal1216_two_ai_consensus_2026-05-01.md`
  - `docs/reports/goal1217_two_ai_consensus_2026-05-01.md`
  - `docs/v1_0_rtx_app_status.md`

## Validation Already Run

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal1218_v0_9_8_release_authorization_gate_test -v
```

Result: 4 tests OK.

## Expected Gate State

- `valid_gate`: `True`
- `release_authorized`: `False`
- `pod_needed_before_authorization`: `False`
- blocker: `v0_9_8_release_package_missing`
- next action: `write_v0_9_8_release_package_and_seek_final_authorization`

## Requested Verdict

Please answer with `ACCEPT` or `BLOCK`.

Focus on:

1. Whether the gate is correct to say saved evidence is valid but release is
   not yet authorized.
2. Whether the gate is correct to say no new pod is needed before release
   package/authorization paperwork.
3. Whether the public claims remain bounded: 11 reviewed RTX rows, road hazard
   only newly reviewed, DB/Jaccard speedup wording still blocked.
4. Whether the missing v0.9.8 release package is correctly treated as the next
   blocker rather than a hardware blocker.

If accepted, write or return a concise review suitable for saving as:

`docs/reports/goal1218_gemini_v0_9_8_release_authorization_gate_review_2026-05-01.md`
