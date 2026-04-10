# Goal 209: v0.4 Bounded Scaling Note

## Objective

Close the remaining `v0.4` acceptance item requiring at least one benchmark or
scaling note for the new nearest-neighbor workload family.

## Scope

- add one bounded local benchmark/scaling harness for:
  - `fixed_radius_neighbors`
  - `knn_rows`
- use only correctness-closed backends:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
- include SciPy only if it is available locally
- use deterministic fixture-derived cases rather than large public benchmark
  claims

## Non-Goals

- no benchmark-win claim
- no nationwide/public large-scale benchmark package
- no PostGIS benchmark requirement in this slice
- no GPU benchmark work

## Acceptance

- one runnable harness exists in the repo
- one bounded JSON artifact is generated from the harness
- one report summarizes the local results honestly
- bounded tests cover the harness shape and output contract
- closure under Codex + Gemini
