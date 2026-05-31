# Goal2797 - Triangle Counting v2.5 Canonical Harness

Date: 2026-05-31

## Purpose

Goal2797 closes the Triangle Counting `needs_single_rerunnable_harness` gap in
the v2.5 tiered benchmark manifest.

The benchmark remains primitive-first: RT-Graph-style triangle counting lowers
to generic RTDL ray/triangle scalar-summary primitives. This goal does not
force a Triton continuation when the scalar summary is already the right
generic RTDL primitive.

## What Changed

Added:

- `scripts/goal2797_triangle_counting_v25_canonical_harness.py`
- `tests/goal2797_triangle_counting_v25_canonical_harness_test.py`
- pod artifacts under `docs/reports/goal2797_pod_artifacts/`

Updated:

- `src/rtdsl/v2_5_triton_app_migration.py`

The new harness:

- generates deterministic disjoint-triangle graphs;
- runs both RT-Graph lowerings:
  - `rt_graph_2a1_generic_rt`
  - `rt_graph_1a2_generic_rt`
- records oracle count, RTDL result count, ray count, primitive count, warm
  median query time, scene-preparation time, and v2.4 phase timing metadata;
- preserves claim-boundary flags blocking public speedup, whole-app speedup,
  Triton speedup, true zero-copy, and paper-reproduction claims.

## Pod Evidence

Artifact:

- `docs/reports/goal2797_pod_artifacts/triangle_counting_v25_canonical_harness_5000_optix.json`

Pod:

- Host: `root@69.30.85.171`, port `22167`, key:
  `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`.
- GPU: NVIDIA RTX A5000, driver `570.211.01`, memory `24564 MiB`.
- Commit basis: `87ff955a` plus the Goal2797 script copied into the pod
  working tree.
- OptiX library: `/root/rtdl_goal2785_work/build/librtdl_optix.so`.

Command:

```text
PYTHONPATH=src:. python3 scripts/goal2797_triangle_counting_v25_canonical_harness.py \
  --triangle-counts 16,1024,5000 \
  --backends optix \
  --warmup 2 \
  --repeat 5 \
  --output docs/reports/goal2797_pod_artifacts/triangle_counting_v25_canonical_harness_5000_optix.json
```

Result:

| Triangles | Method | Backend | Partner | Oracle | Result | Match | Rays | Primitives | Query Median ms | Prepare ms |
| ---: | --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 16 | `rt_graph_2a1_generic_rt` | OptiX | CuPy | 16 | 16 | yes | 16 | 48 | 0.310070 | 392.105660 |
| 16 | `rt_graph_1a2_generic_rt` | OptiX | none | 16 | 16 | yes | 48 | 16 | 0.065343 | 0.221932 |
| 1024 | `rt_graph_2a1_generic_rt` | OptiX | CuPy | 1024 | 1024 | yes | 1024 | 3072 | 0.322954 | 0.650669 |
| 1024 | `rt_graph_1a2_generic_rt` | OptiX | none | 1024 | 1024 | yes | 3072 | 1024 | 0.104297 | 0.273930 |
| 5000 | `rt_graph_2a1_generic_rt` | OptiX | CuPy | 5000 | 5000 | yes | 5000 | 15000 | 0.315068 | 1.032203 |
| 5000 | `rt_graph_1a2_generic_rt` | OptiX | none | 5000 | 5000 | yes | 15000 | 5000 | 0.285376 | 0.791945 |

The first 16-triangle RT-2A1 `prepare_ms` includes one-time OptiX/CUDA warm
initialization. The useful evidence is correctness plus a rerunnable warm
median harness, not a public speedup comparison.

## Manifest Update

The v2.5 tiered benchmark manifest now records:

- `triangle_counting.canonical_harness_status`:
  `ready_with_goal2797_canonical_harness`
- `triangle_counting.pod_evidence_status`:
  current Goal2797 OptiX evidence for RT-2A1 and RT-1A2 primitive-first summary
  rows.

## Decision

`accept-with-boundary`

Goal2797 accepts Triangle Counting as having a canonical v2.5 rerunnable
primitive-first OptiX harness. It does not promote a Triton path for scalar
summary counting, because the primitive-first design says not to route scalar
summaries through a partner just to use a partner.

## Claim Boundary

Still blocked:

- public speedup claims;
- whole-app speedup claims;
- Triton speedup claims;
- true zero-copy claims;
- paper-reproduction claims;
- any claim that v2.5 Triangle Counting has reproduced RT-Graph paper
  performance.

This is same-contract harness evidence and correctness evidence, not a public speedup claim and not a public performance claim.

## Validation

Local Windows validation:

```text
PYTHONPATH=src;. py -3 -m py_compile \
  scripts\goal2797_triangle_counting_v25_canonical_harness.py \
  tests\goal2797_triangle_counting_v25_canonical_harness_test.py \
  src\rtdsl\v2_5_triton_app_migration.py

OK

PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2797_triangle_counting_v25_canonical_harness_test.Goal2797TriangleCountingV25CanonicalHarnessTest.test_disjoint_triangle_generator_has_expected_oracle_shape \
  tests.goal2797_triangle_counting_v25_canonical_harness_test.Goal2797TriangleCountingV25CanonicalHarnessTest.test_cpu_harness_matches_oracle_for_both_lowerings \
  tests.goal2797_triangle_counting_v25_canonical_harness_test.Goal2797TriangleCountingV25CanonicalHarnessTest.test_manifest_records_goal2797_canonical_harness_status \
  tests.goal2730_triangle_counting_v2_5_primitive_first_plan_test \
  tests.goal2723_v2_5_tiered_benchmark_manifest_test

Ran 12 tests
OK
```

Full Goal2797 validation after the Gemini review and consensus file were added:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2797_triangle_counting_v25_canonical_harness_test \
  tests.goal2730_triangle_counting_v2_5_primitive_first_plan_test \
  tests.goal2723_v2_5_tiered_benchmark_manifest_test \
  tests.goal2736_tier_a_primitive_first_plan_alignment_test \
  tests.goal2795_v2_5_tier_label_reconciliation_test

Ran 21 tests
OK
```

Pod clean-check validation from Git:

```text
Host: 69.30.85.171
Port: 22167
Commit: 5a79728d9fd5467342148b907b1c3bd02b131588

git fetch origin main
git reset --hard origin/main
git clean -fd
OPTIX_PREFIX=/root/vendor/optix-sdk make build-optix

PYTHONPATH=src:. python3 scripts/goal2797_triangle_counting_v25_canonical_harness.py \
  --triangle-counts 16,1024,5000 \
  --backends optix \
  --warmup 2 \
  --repeat 5 \
  --output /tmp/goal2797_clean_harness.json

harness pass 6
16 rt_graph_2a1_generic_rt pass 0.3700628876686096
16 rt_graph_1a2_generic_rt pass 0.0745218712836504
1024 rt_graph_2a1_generic_rt pass 0.39024907164275646
1024 rt_graph_1a2_generic_rt pass 0.13312697410583496
5000 rt_graph_2a1_generic_rt pass 0.3820951096713543
5000 rt_graph_1a2_generic_rt pass 0.32616988755762577

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2797_triangle_counting_v25_canonical_harness_test \
  tests.goal2730_triangle_counting_v2_5_primitive_first_plan_test \
  tests.goal2723_v2_5_tiered_benchmark_manifest_test \
  tests.goal2736_tier_a_primitive_first_plan_alignment_test \
  tests.goal2795_v2_5_tier_label_reconciliation_test

Ran 21 tests
OK
```
