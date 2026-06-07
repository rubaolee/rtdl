# Goal3798 RayJoin Future TODO LSI Status Cleanup

Status: implemented locally.

## Purpose

Goal3798 removes stale planning language from the future-version to-do list.
The list still described RayJoin LSI count performance as open after Goal3698,
but later goals had already changed the state:

- Goal3725 measured the generic grouped-range direct exact-count route at
  `3.291x` versus the same-source RayJoin LSI query on the bundled Brazil
  contract.
- Goal3729 wired the RayJoin benchmark app's LSI count route to the generic
  exact-count front door.
- Goal3733 showed the 4096-chain mixed composite is now dominated by overlay
  active-count, not LSI.

## Action

`docs/research/future_version_to_do_list.md` now preserves the historical LSI
diagnosis while marking it superseded by Goals3725/3729/3733. The live RayJoin
future target remains overlay active-count and broader topology/overlay
contracts, not another LSI scalar-count repair.

## Boundary

Goal3798 does not authorize public RayJoin speedup claims, RayJoin paper
reproduction claims, release claims, broad RT-core speedup claims, true
zero-copy claims, whole-app acceleration claims, or app-specific native-engine logic.

## Validation

Focused validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3798_rayjoin_future_todo_lsi_status_cleanup_test tests.goal3725_rayjoin_lsi_grouped_range_policy_sweep_test tests.goal3729_rayjoin_lsi_exact_count_front_door_adoption_test tests.goal3733_rayjoin_safe_mixed_composite_after_lsi_front_door_test
```
