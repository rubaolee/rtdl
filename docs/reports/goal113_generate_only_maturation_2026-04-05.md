# Goal 113 Generate-Only Maturation

Date: 2026-04-05
Author: Codex
Status: accepted

## Goal

Strengthen the Goal 111 generate-only MVP in one way that produces visibly
better user value without broadening the feature irresponsibly.

## Chosen improvement target

Goal 113 chose one explicit improvement target:

- `handoff_bundle` artifact shape

This was chosen instead of broadening workloads or adding many new request
flags.

Why:

- it is a concrete user-visible improvement
- it is easier to evaluate honestly than many shallow options
- it addresses a real gap in Goal 111:
  - Goal 111 produced one runnable file
  - Goal 113 now produces a reviewable handoff package

## What changed

Implementation files:

- `src/rtdsl/generate_only.py`
- `scripts/rtdl_generate_only.py`
- `tests/goal113_generate_only_maturation_test.py`

Tracked worked bundle:

- `examples/rtdl_generated_segment_polygon_bundle/README.md`
- `examples/rtdl_generated_segment_polygon_bundle/request.json`
- `examples/rtdl_generated_segment_polygon_bundle/generated_segment_polygon_hitcount_cpu_python_reference_authored_segment_polygon_minimal.py`

The generator now supports:

- `single_file`
- `handoff_bundle`

The bundle shape contains:

- generated program
- request manifest
- bundle README

## Why this is better than Goal 111

Goal 111 was a narrow MVP proving:

- structured request in
- runnable file out

Goal 113 improves one real user scenario:

- a user wants to hand a generated RTDL artifact to another person for review,
  rerun, or inspection

For that scenario, a bundle is better than a single file because it includes:

- explicit request manifest
- explicit README
- clear run contract
- easier inspection of what was requested versus what was generated

That is a better handoff surface than:

- a single generated Python file alone
- a curated example with manual edits
- a template plus verbal instructions

## Validation

Compile check:

```bash
python3 -m py_compile \
  src/rtdsl/generate_only.py \
  scripts/rtdl_generate_only.py \
  tests/goal113_generate_only_maturation_test.py
```

Test check:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal111_generate_only_mvp_test \
  tests.goal113_generate_only_maturation_test
```

Result:

- `7` tests
- `OK`
- `1 skipped`

The skipped test is still the existing local Mac native-oracle path that lacks
`geos_c`.

## Worked example

Generation command:

```bash
cd /Users/rl2025/rtdl_python_only
python3 scripts/rtdl_generate_only.py \
  --workload segment_polygon_hitcount \
  --dataset authored_segment_polygon_minimal \
  --backend cpu_python_reference \
  --artifact-shape handoff_bundle \
  --output-mode summary \
  --output examples/rtdl_generated_segment_polygon_bundle
```

Bundle contents:

- `examples/rtdl_generated_segment_polygon_bundle/README.md`
- `examples/rtdl_generated_segment_polygon_bundle/request.json`
- `examples/rtdl_generated_segment_polygon_bundle/generated_segment_polygon_hitcount_cpu_python_reference_authored_segment_polygon_minimal.py`

Generated program run:

```bash
cd /Users/rl2025/rtdl_python_only
python3 examples/rtdl_generated_segment_polygon_bundle/generated_segment_polygon_hitcount_cpu_python_reference_authored_segment_polygon_minimal.py
```

Observed payload:

```json
{
  "backend": "cpu_python_reference",
  "dataset": "authored_segment_polygon_minimal",
  "row_count": 2,
  "verification_requested": true,
  "verified_against_cpu_python_reference": true,
  "workload": "segment_polygon_hitcount"
}
```

## Honest boundary

Goal 113 does **not** prove broad code generation.

It closes as:

- one strengthened narrow feature
- one additional artifact shape
- one clearer handoff scenario

It does **not** close as:

- arbitrary project scaffolding
- many-workload code generation
- native-code generation
- general proof that codegen is now a co-equal v0.2 identity pillar

## Keep / pause judgment

Keep the feature.

Why:

- the improvement is real
- the user scenario is concrete
- the new artifact shape is visibly better than the Goal 111 single-file MVP

But keep it narrow.

If future work becomes mostly more flags or more low-signal bundle boilerplate,
pause expansion quickly.
