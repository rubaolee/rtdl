# Call For Review: V4 Goal4693 Specialized Hit Callback Probe

Date: 2026-06-25
Requested verdict labels:

- `accept_goal4693_complete_continue_goal4694`
- `reject_goal4693_not_hit_program_evidence`
- `accept_with_required_amendments`

## Files To Review

- Completion report:
  `future/v4/v4_goal4693_specialized_hit_callback_probe_2026-06-25.md`
- Machine evidence:
  `future/v4/evidence/v4_goal4693_specialized_hit_callback_probe_2026-06-25.json`
- Evidence summary:
  `future/v4/evidence/v4_goal4693_specialized_hit_callback_probe_2026-06-25.md`
- Probe implementation:
  `scripts/v4_goal4693_specialized_hit_callback_probe.py`
- Contract module:
  `src/rtdsl/v4_goal4693_specialized_hit_callback_probe.py`

## Review Questions

1. Does the evidence prove a real OptiX traversal/hit-program-shaped callback
   path, rather than another raygen-only microbench?
2. Is it correct that this path avoids SBT direct-callable overhead?
3. Is the output correctness proof sufficient for this minimal scalar callback
   shape?
4. Does the report preserve non-authorization boundaries?
5. Should Goal4694 proceed to overhead/productization decision for this
   specialized hit-callback track?

## Non-Authorization

This review request does not authorize:

- final V4 release
- public Tier-3 callback support
- arbitrary callback support
- callback performance claims
- app-level benchmark claims
