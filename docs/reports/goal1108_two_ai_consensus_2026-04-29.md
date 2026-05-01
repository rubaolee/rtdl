# Goal1108 Two-AI Consensus

Date: 2026-04-29

Verdict: ACCEPT AS ENGINEERING COMPARISON, NOT PUBLIC CLAIM

## Scope

Goal1108 compares existing RTX pod artifacts against the now-complete same-contract non-OptiX baseline artifacts for:

- `facility_knn_assignment / coverage_threshold_prepared_recentered`
- `barnes_hut_force_app / node_coverage_prepared_rich`

## Consensus

Codex verdict: ACCEPT.

Second-AI reviewer verdict: ACCEPT.

Consensus conclusion: the ratios are valid engineering comparison evidence for internal planning, but they are not public speedup claims.

## Ratios

| App | Baseline | RTX median (s) | Baseline median (s) | Engineering ratio |
| --- | --- | ---: | ---: | ---: |
| `facility_knn_assignment` | `cpu_oracle` | `0.135054` | `8.996513` | `66.61x` |
| `facility_knn_assignment` | `embree` | `0.135054` | `29.806781` | `220.70x` |
| `barnes_hut_force_app` | `embree` | `0.230636` | `53.465870` | `231.82x` |

## Boundary

Public RTX speedup claims remain blocked because:

- the comparison is cross-host;
- source commits differ between RTX and baseline artifacts;
- public wording review is still required.

No front-page, README, release, or public performance claim is authorized by this goal.
