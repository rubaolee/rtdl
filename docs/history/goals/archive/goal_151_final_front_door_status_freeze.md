# Goal 151: Final Front-Door Status Freeze

## Why

After Goal 150, the main remaining release-shaping risk is wording drift.

The front-door docs, user guide, feature guide, and bootstrap memory file
should all describe the same frozen v0.2 position in the same honest way.

## Scope

- freeze one canonical front-door status statement for v0.2
- update the main top-level docs to match that statement
- add one small audit that checks the frozen workload surface, platform split,
  and Jaccard fallback boundary are all present in the key front-door docs

## Acceptance

- README, docs index, v0.2 user guide, feature guide, and bootstrap memory all
  describe the same frozen v0.2 release-shaping surface
- the accepted v0.2 workload list is explicit in those docs
- Linux-primary / Mac-limited wording is explicit
- Jaccard fallback-vs-native wording is explicit
- one audit script confirms those points structurally
- review coverage is saved before the goal is treated as online
