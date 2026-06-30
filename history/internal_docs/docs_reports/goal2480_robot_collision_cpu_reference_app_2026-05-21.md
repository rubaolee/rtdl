# Goal2480 Robot Collision CPU Reference App

Date: 2026-05-21

## Result

Goal2480 adds a CPU-reference robot collision benchmark app under:

```text
examples/v2_0/research_benchmarks/robot_collision/
```

The app implements the first scoped robot-collision contract:

```text
static obstacle triangles + batched transformed query meshes -> compact any-hit flags
```

No native code was changed. No Embree or OptiX work is included in Goal2480.

## Paper And Code Status

Working research anchor:

- *Hardware-Accelerated Ray Tracing for Discrete and Continuous Collision Detection on GPUs*.
- Authors recorded in the app metadata: Sizhe Sui, Luis Sentis, Andrew Bylard.
- Source links checked on 2026-05-21:
  - `https://arxiv.org/abs/2409.09918`
  - `https://ssz990220.github.io/publications/`

Status:

- Official implementation was not verified.
- Official benchmark data was not verified.
- The citation remains tentative for paper-facing wording until a later scoping goal confirms authorship, venue status, DOI, code, and data availability.
- If authors' code becomes available, comparison requires a separate scoping goal before claims or performance wording.

## Implemented App

File:

- `examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py`

CLI:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py --dataset tiny --include-rows
```

Datasets:

| Dataset | Purpose |
| --- | --- |
| `tiny` | Five deterministic two-link poses against one static rectangular obstacle; includes clear, single-link, both-link, and rotated-query cases. |
| `scaled` | Deterministic larger CPU fixture with configurable pose, obstacle, and link counts. |

Outputs:

| Field | Meaning |
| --- | --- |
| `pose_summaries` | Per-pose compact any-hit summaries. |
| `link_flags` | Per-pose/per-link any-hit flags. |
| `compact_link_flags` | Pose-major compact `0/1` flag vector. |
| `hit_pairs` | Optional query-triangle/static-triangle witness pairs when `--include-rows` is passed. |

The tiny fixture expected compact flags are:

```text
[0, 0, 0, 1, 1, 1, 0, 0, 0, 1]
```

## RTDL Design Boundary

Goal2480 deliberately keeps all robotics semantics in Python:

- link construction;
- pose generation;
- transforms;
- collision policy;
- fixture labels;
- per-pose/per-link summaries.

The future generic runtime target is app-agnostic:

```text
prepared_static_triangles_plus_batched_transformed_query_geometry_to_compact_any_hit_flags
```

The CPU reference is intentionally 2D. Goal2481 must explicitly decide whether
the first native contract remains 2D for this benchmark lane, generalizes to 3D
transformed triangles, or requires an additional 3D CPU reference before native
Embree/OptiX parity work starts.

Goal2481 must decide whether compact native output should be byte-per-query,
bit-packed, or a typed partner/native column. That decision should follow
existing RTDL buffer and tensor conventions, not robot-link convenience.

## Claim Boundary

The app metadata sets:

- `paper_reproduction_claim_authorized = false`
- `authors_code_comparison_claim_authorized = false`
- `public_speedup_claim_authorized = false`
- `native_robot_abi_added = false`
- `native_collision_abi_added = false`
- `native_engine_touched = false`
- `continuous_collision_supported = false`
- `cpu_reference_only = true`

This app is a CPU oracle and contract seed. It does not authorize performance
claims.

The paper citation, venue status, DOI, official code, and official data must be
rechecked before any external-facing or paper-facing wording. Goal2481 should
also broaden native vocabulary enforcement beyond ABI-prefix scans before native
work begins.

## Validation

Local validation:

```bash
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m py_compile \
  examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py

PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2480_robot_collision_cpu_reference_app_test
```

The tests check:

- tiny fixture expected flags;
- CLI JSON output;
- scaled fixture shape;
- app and docs claim boundaries;
- no native robot/collision ABI was added.

## Next Gate

Goal2481 should design the generic RTDL contract before any native Embree or
OptiX implementation starts.
