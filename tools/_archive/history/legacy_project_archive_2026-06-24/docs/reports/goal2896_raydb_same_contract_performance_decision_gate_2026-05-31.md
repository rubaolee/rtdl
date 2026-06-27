# Goal2896: RayDB Same-Contract Performance Decision Gate

Date: 2026-05-31
Status: accepted as internal performance-decision evidence with pod artifact

## Purpose

Claude's strategic assessment correctly says the next v2.5 step needs a concrete same-contract performance number, not more architecture prose. Goal2896 converts that into a small executable gate for the RayDB scalar grouped-reduction row.

The question is narrow:

Should v2.5 route RayDB-style grouped `count` / `sum` through the typed hit-stream plus Triton continuation path, or should it choose the existing fused app-agnostic RTDL primitive when that primitive exactly matches the requested continuation?

## Gate Inputs

The pod runner uses:

- GPU: sm_70+ NVIDIA pod
- row counts: `250000`, `1000000`
- group count: `256`
- modes: `count`, `sum`
- repeats: `3`
- warmup: `1`
- backends:
  - `paper_rt_optix`
  - `paper_rt_optix_v2_5_primitive_first`
  - `paper_rt_optix_device_hit_stream_triton_prepared`

The raw runner remains:

```bash
PYTHONPATH=src:. python3 scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py \
  --row-counts 250000,1000000 \
  --group-count 256 \
  --modes count,sum \
  --backends paper_rt_optix,paper_rt_optix_v2_5_primitive_first,paper_rt_optix_device_hit_stream_triton_prepared \
  --repeats 3 \
  --warmup 1 \
  --output docs/reports/goal2896_pod_artifacts/goal2896_raydb_same_contract_raw_pod_69_30_85_171_2026-05-31.json
```

The decision gate is:

```bash
PYTHONPATH=src:. python3 scripts/goal2896_raydb_same_contract_performance_decision_gate.py \
  --input docs/reports/goal2896_pod_artifacts/goal2896_raydb_same_contract_raw_pod_69_30_85_171_2026-05-31.json \
  --output docs/reports/goal2896_pod_artifacts/goal2896_raydb_same_contract_performance_decision_gate_pod_69_30_85_171_2026-05-31.json
```

## Acceptance Bar

Required:

- all backend cases match the CPU reference;
- primitive-first records `prepared_fused_generic_grouped_reduction`;
- primitive-first does not force typed hit streams;
- primitive-first does not require partner continuation;
- prepared hit-stream plus Triton is at least `10x` slower than primitive-first for `count`;
- prepared hit-stream plus Triton is at least `50x` slower than primitive-first for `sum`;
- diagnostic old `paper_rt_optix` full-call baseline is at least `20x` slower than primitive-first for `count`;
- diagnostic old `paper_rt_optix` full-call baseline is at least `5x` slower than primitive-first for `sum`;
- no case authorizes release, public speedup, broad RT-core speedup, whole-app speedup, or true zero-copy wording.

## Current Result

Artifacts:

- `docs/reports/goal2896_pod_artifacts/goal2896_raydb_same_contract_raw_pod_69_30_85_171_2026-05-31.json`
- `docs/reports/goal2896_pod_artifacts/goal2896_raydb_same_contract_performance_decision_gate_pod_69_30_85_171_2026-05-31.json`

Pod:

- host: `69.30.85.171`
- port: `22167`
- GPU: `NVIDIA RTX A5000, 570.211.01, 24564 MiB`
- source commit: `3dc64b9ce2846a00a26b3058a72207f156e69a25`

The gate passed:

- `status = pass`
- `all_correct = true`
- `errors = []`

Same-contract decision comparison:

| Rows | Mode | Primitive-first sec | Prepared hit-stream + Triton sec | Hit-stream slowdown vs primitive-first | Required |
| ---: | --- | ---: | ---: | ---: | ---: |
| 250000 | count | 0.000433 | 0.016973 | 39.155x | >= 10x |
| 250000 | sum | 0.001875 | 0.384626 | 205.085x | >= 50x |
| 1000000 | count | 0.000521 | 0.011770 | 22.582x | >= 10x |
| 1000000 | sum | 0.002118 | 0.348804 | 164.657x | >= 50x |

Diagnostic full-call baseline comparison:

| Rows | Mode | Primitive-first sec | Old `paper_rt_optix` sec | Primitive-first speedup | Required |
| ---: | --- | ---: | ---: | ---: | ---: |
| 250000 | count | 0.000433 | 0.655806 | 1512.862x | >= 20x |
| 250000 | sum | 0.001875 | 1.370460 | 730.737x | >= 5x |
| 1000000 | count | 0.000521 | 2.040713 | 3915.458x | >= 20x |
| 1000000 | sum | 0.002118 | 3.267547 | 1542.485x | >= 5x |

## Design Decision

If the gate passes, the v2.5 RayDB scalar grouped-reduction rule is:

1. Use the fused generic RTDL primitive when it exactly expresses the continuation.
2. Reserve typed hit-stream plus partner continuation for computations not expressible by the fused primitive set.
3. Do not promote Triton simply to use Triton.
4. Keep v3.0 user-defined shader injection out of this release lane.

## Boundary

This is an internal decision gate, not a release claim.

It is not a public speedup claim, not a true-zero-copy claim, not a whole-app RayDB reproduction claim, and not evidence that every v2.5 app should prefer primitive-first routing. It answers one important planning question for a scalar grouped-reduction workload whose continuation already matches a fused app-agnostic RTDL primitive.
