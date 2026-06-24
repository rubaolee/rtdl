# Goal 1436 v1.5.1 COLLECT_K_BOUNDED Release-Surface Proposal False-Flag Hardening

## Verdict

ACCEPTED as a release-surface proposal hardening patch.

## Change

The v1.5.1 `COLLECT_K_BOUNDED` release-surface proposal now carries an explicit `whole_app_speedup_claim_authorized_by_this_proposal: False` field, matching the readiness gate and release-surface gate false-flag boundary.

The release-surface proposal validator now rejects any attempt to set that proposal-level whole-app speedup flag to `True`.

## Boundary

This patch is traceability hardening only. It does not authorize public docs changes, stable `COLLECT_K_BOUNDED` promotion, speedup wording, zero-copy wording, whole-app speedup claims, release tags, or release action.
