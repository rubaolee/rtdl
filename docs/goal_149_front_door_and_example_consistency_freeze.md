# Goal 149: Front-Door And Example Consistency Freeze

## Why

After the v0.2 scope freeze, the main release-facing docs and example paths
must point users at the same accepted live surface.

## Scope

- define one canonical release-facing example index
- update front-door docs so they route users to that index
- keep the v0.2 workload surface and honesty boundaries aligned with Goal 148
- add one small reproducible audit for release-facing example/doc consistency

## Acceptance

- one checked-in release-facing example index exists
- README, docs index, quick tutorial, feature guide, and v0.2 user guide all
  route to that index
- the example index points only to the frozen v0.2 scope
- one audit script confirms example existence and doc links
- review coverage is saved before the goal is treated as online
