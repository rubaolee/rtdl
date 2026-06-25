# Codex Independent Review: V4 Goal4642 Final Authorization And Amendment Recheck

Reviewer: independent Codex sub-agent.

Status: completed.

## Initial Verdict

`authorize_with_amendments_before_publication`

Initial findings:

- Major: machine-readable forbidden-claim coverage was incomplete. The packet
  forbade Barnes-Hut coverage, Spatial RayJoin coverage, and LibRTS paper
  reproduction, but `src/rtdsl/v4_release_decision.py` and
  `src/rtdsl/v4_goal4642_final_authorization_packet.py` did not yet include
  those three claims in their `forbidden_claims` tuples.
- Major: `README.md` still said release was gated on public-doc cleanup and
  clean-tree reproducibility even though Goal4640 and Goal4641 had passed.
- Minor: the clean-tree audit trail was split. Goal4641 machine state did not
  mirror the final clean-tree revalidation evidence clearly enough.

Initial conclusion:

The narrow release label was supported, but publication required amendments.

## Amendments Applied

- Added `Barnes-Hut covered by V4.0`, `Spatial RayJoin covered by V4.0`, and
  `LibRTS paper reproduction` to machine-readable forbidden-claim tuples in:
  - `src/rtdsl/v4_release_decision.py`
  - `src/rtdsl/v4_goal4642_final_authorization_packet.py`
- Added tests for the missing machine-denylist entries:
  - `tests/v4_goal4632_release_decision_test.py`
  - `tests/v4_goal4642_final_authorization_packet_test.py`
  - `tests/v4_goal4644_post_release_guardrails_test.py`
- Updated `README.md` to state that public-doc cleanup and clean-tree
  reproducibility have passed, with final publication still gated on release
  authorization and publication.
- Split clean-tree revalidation evidence correctly:
  - Goal4641 machine state records `final_revalidation_commit =
    884aeda8084d4c84bae8ec858f4b7436461ee783`;
  - Goal4642 packet machine state records
    `packet_clean_tree_revalidation_commit =
    437b79a2a382082e269d0d0ee128528caf0ae112`;
  - the Goal4642 packet and review record document both revalidation points.

## Final Recheck Verdict

`amendments_satisfied_authorize_publication`

Final recheck findings:

- Remaining blockers: none.
- Confirmed Goal4641/Goal4642 revalidation commits are no longer mixed.
- Confirmed targeted tests passed: `15 tests OK`.

## Non-Authorization Boundary

This review authorizes only the narrow requested label:

`RTDL v4.0.0 formal high-performance generic RT-core operator release`

It does not authorize broad V4 speedup, whole-application speedup,
all-benchmark speedup, public true-zero-copy, Tier-3 callback support, raw
OptiX callback support, CuPy performance, C ABI, embedding, non-Python host
bindings, app-specific native kernels, Barnes-Hut V4.0 coverage, Spatial
RayJoin V4.0 coverage, or LibRTS paper reproduction.
