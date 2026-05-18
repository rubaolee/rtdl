# RTDL v2.0 Release Package

Status: released source-tree Python+partner+RTDL language boundary.

Version marker: `v2.0`

Release date: 2026-05-18

## Release Statement

RTDL v2.0 is the source-tree Python+partner+RTDL release. It publishes the
current learner-facing Python authoring model, the partner-owned column
contract, and the app-agnostic native release surface.

The release is source-tree based. Use it from a checkout with
`PYTHONPATH=src:.`. It is not a package-install release, not a broad RT-core
speedup claim, not a whole-application speedup claim, and not a claim that RTDL
optimizes arbitrary PyTorch or CuPy programs.

## What v2.0 Includes

- A clean learner path from the front page through tutorials, examples,
  architecture pages, feature homes, and RTDL language docs.
- A Python+partner+RTDL authoring boundary: Python remains the application
  layer, partner frameworks own columns and continuation work, and RTDL owns
  documented RT-shaped primitive calls.
- NumPy, PyTorch CUDA, and CuPy CUDA partner paths where documented.
- An app-agnostic native release surface under the strict tracked `rtdl_...`
  symbol scan.
- Current OptiX/RT release evidence with 16/16 measured v2 rows faster than
  the previous source-tree baseline under documented contracts.
- Partner-owned count, flag, threshold, bounded candidate, and streaming
  witness-column output patterns.
- RayJoin-style LSI/PIP closure as bounded same-query evidence, with no claim
  that RTDL beats the RayJoin paper implementation.

## What v2.0 Does Not Claim

- No package metadata, PyPI artifact, or install command is published by this
  release.
- No universal speedup claim is made for backend flags such as
  `--backend optix`.
- No arbitrary PyTorch/CuPy acceleration claim is made.
- No arbitrary polygon overlay, graph database, DBMS, GIS engine, robotics
  planner, or renderer claim is made.
- No Triton, Numba, Embree CPU partner, v3.0 custom-extension, or custom
  shader-injection support is part of this release.
- No promise is made that stale local native libraries already contain the
  latest v2.0 symbols; rebuild backend libraries from the tagged source.

## Evidence

- [Goal2068 final v2.0 release matrix](../../reports/goal2068_final_v2_0_release_matrix.md)
- [Goal2069 v2.0 pre-release gate](../../reports/goal2069_v2_0_pre_release_gate_2026-05-15.md)
- [Goal2072 final readiness aggregator](../../reports/goal2072_v2_0_final_readiness_aggregator_2026-05-15.md)
- [Goal2085 streaming witness performance table](../../reports/goal2085_v2_perf_table_after_streaming_witness_update_2026-05-15.md)
- [Goal2088 release prep after streaming witness](../../reports/goal2088_v2_0_release_prep_after_streaming_witness_2026-05-15.md)
- [Goal2319 final cleanup release candidate](../../reports/goal2319_v2_0_final_cleanup_release_candidate_2026-05-18.md)
- [Goal2320 Claude final cleanup review](../../reviews/goal2320_claude_final_v2_0_release_cleanup_review_2026-05-18.md)
- [Goal2321 Gemini final cleanup review](../../reviews/goal2321_gemini_final_v2_0_release_cleanup_review_2026-05-18.md)
- [Goal2322 final 3-AI consensus](../../reports/goal2322_final_v2_0_release_cleanup_3ai_consensus_2026-05-18.md)
- [Goal2323 release action](../../reports/goal2323_v2_0_release_action_2026-05-18.md)

## Minimal Smoke Commands

```bash
PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_hello_world.py
PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_feature_quickstart_cookbook.py
PYTHONPATH=src:. python -m unittest tests.goal2323_v2_0_release_action_test
```

## Release Boundary

RTDL v2.0 is released with boundaries. It is the first RTDL release where the
public story is Python+partner+RTDL rather than Python+RTDL alone. It is ready
for learners and developers to use from source, while deeper tuning and new
partner research move to v2.1 and later.
