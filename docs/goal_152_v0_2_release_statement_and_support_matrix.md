# Goal 152: v0.2 Release Statement And Support Matrix

## Why

After the scope freeze, release-surface freeze, readiness pass, and front-door
freeze, the repo now needs the canonical v0.2 release documents themselves.

These should be the shortest documents a reader can cite to answer:

- what v0.2 is
- what v0.2 stands on
- what v0.2 does not claim
- which workloads, backends, and platforms are part of the accepted release
  surface

## Scope

- add the canonical v0.2 release statement
- add the canonical v0.2 support matrix
- keep those docs aligned with Goals 148 through 151
- record Antigravity as supplementary external evidence, not as the canonical
  release definition

## Acceptance

- `docs/release_reports/v0_2/` exists
- `release_statement.md` exists
- `support_matrix.md` exists
- the docs keep the frozen four-workload v0.2 scope explicit
- the docs keep Linux-primary / Mac-limited explicit
- the docs keep the Jaccard fallback-vs-native boundary explicit
- the docs are reviewed before they are treated as online
