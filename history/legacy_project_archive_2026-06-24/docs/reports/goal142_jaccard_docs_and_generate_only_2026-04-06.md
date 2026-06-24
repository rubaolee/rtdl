# Goal 142 Jaccard Docs And Generate-Only Expansion

## Status

Accepted as a narrow product/documentation expansion.

## What landed

- generate-only support for:
  - `polygon_set_jaccard`
- updated CLI surface:
  - [rtdl_generate_only.py](/Users/rl2025/rtdl_python_only/scripts/rtdl_generate_only.py)
- updated generator:
  - [generate_only.py](/Users/rl2025/rtdl_python_only/src/rtdsl/generate_only.py)
- focused tests:
  - [goal142_generate_only_jaccard_test.py](/Users/rl2025/rtdl_python_only/tests/goal142_generate_only_jaccard_test.py)
- checked-in worked bundle:
  - [README.md](/Users/rl2025/rtdl_python_only/examples/generated/rtdl_generated_polygon_set_jaccard_bundle/README.md)
  - [request.json](/Users/rl2025/rtdl_python_only/examples/generated/rtdl_generated_polygon_set_jaccard_bundle/request.json)
  - [generated program](/Users/rl2025/rtdl_python_only/examples/generated/rtdl_generated_polygon_set_jaccard_bundle/generated_polygon_set_jaccard_cpu_python_reference_authored_polygon_set_jaccard_minimal.py)

## Documentation updates

- [v0_2_user_guide.md](/Users/rl2025/rtdl_python_only/docs/v0_2_user_guide.md)
- [workload_cookbook.md](/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md)

## Validation

- `python3 -m py_compile` on the updated generator/CLI/tests:
  - clean
- focused generate-only tests:
  - `5 tests`, `OK`, `1 skipped`
- generated handoff bundle program run:
  - workload: `polygon_set_jaccard`
  - backend: `cpu_python_reference`
  - row count: `1`
  - verified against `cpu_python_reference`: `true`
- direct CLI single-file generation and run:
  - workload: `polygon_set_jaccard`
  - backend: `cpu_python_reference`
  - row count: `1`
  - verified against `cpu_python_reference`: `true`

## Honest boundary

Goal 142 does **not** claim that generate-only already covers the whole public
Jaccard line.

It only closes a narrow handoff surface for the authored `polygon_set_jaccard`
case, which is the right product step after Goals 140 and 141.
