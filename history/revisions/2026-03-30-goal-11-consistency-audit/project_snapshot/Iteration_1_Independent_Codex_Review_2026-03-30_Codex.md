# Iteration 1 Independent Codex Review (2026-03-30, Codex)

## Findings

### Medium: README setup order overstated fresh-checkout behavior

`README.md` instructed users to run `make build` and `make test` before the
Embree install section, but the pre-audit repository state still relied on
Embree in those paths. `make build` executed the full demo, which entered the
Embree path, and Embree-dependent tests were not skipped automatically.

### Medium: Language docs under `docs/rtdl/` were stale

The language-facing docs still described only the older four-workload surface.
They omitted:

- `segment_polygon_hitcount`
- `point_nearest_segment`

That drifted from the public API, examples, and tests.

### Low: Language-doc regression tests encoded the older surface

The language test suite did not validate the Goal 10 workload extensions in the
language docs or plan validation path, so CI would not catch that drift.

## Residual Risk Notes

- The frozen Embree baseline docs intentionally cover only the baseline four
  workloads, while the broader current RTDL surface now includes six. That scope
  split is legitimate, but it needs to remain explicitly labeled.
