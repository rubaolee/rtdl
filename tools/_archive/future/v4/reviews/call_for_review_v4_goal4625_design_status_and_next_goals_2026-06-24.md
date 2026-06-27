# Call For Review: V4 `goal4625` Design Status And Next Goals

Date: 2026-06-24
Requested verdict labels:

- `accept_goal4625_status_and_next_goals`
- `accept_with_required_amendments`
- `reject_goal4625_status_or_goals_misleading`

## Review Request

Please critically review:

- `future/v4/v4_claude_design_implementation_status_and_next_goals_2026-06-24.md`

Scope:

- Does the document honestly map Claude's V4 three-tier fused design to what is
  actually implemented?
- Does it clearly distinguish development-state completion from performance
  release completion?
- Are the next goals ordered correctly?
- Are any missing goals or incorrect priorities present?

## Current Claimed State

Current decision:

- `development_state_documentation_disclosure_not_release`

Implemented development-state surface:

- five measured Torch CUDA Tier-2 surfaces
- one candidate Tier-2 surface
- Tier-3 protocol-only boundary
- final POD catalog gate passed
- fixed-radius Section 8 chain completed for one bounded primitive:
  - original whole-call app route failed
  - prepared hot-path credit accepted
  - Route D independent hand-written OptiX ceiling acquired
  - Torch device-array front door accepted as the current product-boundary fix
    for this contract

Not implemented:

- app-catalog coverage audit
- general push-down recognizer
- Tier-3 implementation
- release or release-candidate authorization
- catalog-wide performance-release scorecard beyond fixed-radius

## Proposed Next Goals

- `goal4626`: Section 8 evidence reconciliation and release-scorecard protocol
- `goal4627`: Tier-2 operator coverage audit
- `goal4628`: second Tier-2 same-contract POD gate
- `goal4629`: weighted-sum candidate promotion/rejection decision
- `goal4630`: push-down recognizer minimum slice
- `goal4631`: Tier-3 Stage-1/Stage-2 spike execution
- `goal4632`: V4 performance release decision

## Questions For Review

1. Is the completion matrix accurate?
2. Does the document overstate current implementation?
3. Does the amended document correctly avoid pretending the fixed-radius
   Section 8/Route D/device-array work is still unrun?
4. Is `goal4626` correctly reframed as evidence reconciliation and scorecard
   protocol rather than a duplicate experiment?
5. Should coverage audit happen immediately after `goal4626`, before choosing
   the second same-contract POD gate?
6. Are weighted-sum promotion, push-down recognizer, and Tier-3 spike correctly
   ordered?
7. What amendments are required before execution resumes?

## Non-Authorization

This review request does not authorize:

- V4 release
- V4 release-candidate status
- public broad speedup wording
- whole-application speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels
