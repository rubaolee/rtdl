# Call For Review: V4 Goal4688 Tier-3 Semantic Wrapper Module-Link Probe

Date: 2026-06-25
Requested verdict labels:

- `accept_goal4688_complete_continue_goal4689`
- `reject_goal4688_not_complete`
- `accept_with_required_amendments`

## Files To Review

- Completion report:
  `future/v4/v4_goal4688_tier3_module_link_probe_2026-06-25.md`
- Machine evidence:
  `future/v4/evidence/v4_goal4688_tier3_module_link_probe_2026-06-25.json`
- Evidence summary:
  `future/v4/evidence/v4_goal4688_tier3_module_link_probe_2026-06-25.md`
- Probe implementation:
  `scripts/v4_goal4688_tier3_module_link_probe.py`
- PTX composition helper:
  `src/rtdsl/v4_goal4688_tier3_module_link_probe.py`
- Semantic wrapper scaffold:
  `src/rtdsl/v4_goal4686_tier3_wrapper_abi_scaffold.py`
- Numba PTX probe:
  `scripts/v4_tier3_numba_ptx_probe.py`

## Review Questions

1. Does the evidence prove the narrow Goal4688 gate: Numba callback PTX plus
   semantic wrapper PTX can be accepted by OptiX through module creation,
   program group creation, and pipeline creation?
2. Is the `--keep-device-functions` fix correctly identified as necessary for
   exposing the direct callable as an OptiX-visible entry?
3. Is the empty raygen entry acceptable for Goal4688, given that Goal4689 owns
   the minimal launch and callable invocation semantics?
4. Does the report preserve all non-authorization boundaries: no Tier-3 support,
   no raw callback support, no performance claim, no release claim?
5. Should Goal4689 proceed as a minimal launch/correctness probe, or is another
   ABI/linking correction required first?

## Expected Honest Reading

Goal4688 is real progress, but only at the module/pipeline construction layer.
It does not prove callback correctness, launchability, overhead, or product
support. A reviewer should reject any wording that turns this into public
Tier-3 support.

## Non-Authorization

This review request does not authorize:

- V4 release or tag
- public high-performance wording
- arbitrary callback support
- app-level benchmark claims
- whole-app V4-over-V2/V3 claims
- app-specific native kernels
