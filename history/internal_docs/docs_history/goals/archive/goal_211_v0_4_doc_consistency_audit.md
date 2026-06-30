# Goal 211: v0.4 Doc Consistency Audit

## Objective

Remove stale `v0.4` wording from the live language/feature docs now that the
nearest-neighbor family is no longer merely planned.

## Scope

- update live `docs/rtdl/` pages that still say the nearest-neighbor surfaces
  are only planned or not yet lowered
- update feature-home pages so `knn_rows` is represented as an active preview
  workload instead of an unimplemented idea
- keep archived historical review files untouched

## Non-Goals

- no change to historical reports
- no new workload implementation
- no release/tag claim

## Acceptance

- live docs no longer contradict current `v0.4` implementation state
- feature index lists both nearest-neighbor feature homes clearly
- bounded test/doc verification is rerun
- closure under Codex + external review
