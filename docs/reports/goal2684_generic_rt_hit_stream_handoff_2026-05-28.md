# Goal2684: Generic RT Hit-Stream Handoff For Full RT+Triton Path

Date: 2026-05-28
Base commit before this goal: `6cb363c7865db3ea46b6ba372ac99293b166ed3d`

## Purpose

Goal2684 closes the main Goal2683 gap: RT traversal can now produce a generic
hit stream that a Triton partner continuation can consume. The design keeps the
engine app-free:

- RTDL/Embree/OptiX own traversal and generic hit-row emission.
- Python app code owns RayDB predicate encoding and primitive-to-payload mapping.
- Triton owns generic grouped continuation.
- Native code must not know RayDB, SQL, tables, predicates, or aggregate names.

## Generic Primitive Contract

Primitive: `RAY_TRIANGLE_HIT_STREAM_3D`

Row schema:

```text
(ray_id, primitive_id)
```

Contract properties:

- rows are app-free IDs only;
- optional primitive deduplication is explicit;
- bounded output is fail-closed: overflow returns no partial rows;
- native APIs report pre-dedup hit events separately from emitted row count;
- no group id, payload value, SQL predicate, RayDB table, or app semantics appear
  in the native engine ABI.

## Implementation Summary

New native ABI:

- Embree: `rtdl_embree_static_triangle_scene_3d_ray_triangle_hit_stream`
- OptiX: `rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream`

New Python API:

- `rtdsl.run_generic_ray_triangle_hit_stream_3d(...)`
- `rtdsl.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE`
- `rtdsl.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA`
- `rtdsl.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_CONTRACT`

RayDB path added:

- `paper_rt_embree_hit_stream_triton`
- `paper_rt_optix_hit_stream_triton`

Execution shape:

```text
RayDB app-owned table encoding
-> generic rays and triangles
-> Embree/OptiX RAY_TRIANGLE_HIT_STREAM_3D
-> app-owned primitive_id -> group/value mapping
-> Triton grouped continuation
-> RayDB-style app rows
```

The older native grouped-reduction path remains available for same-contract
comparison:

- `paper_rt_embree`
- `paper_rt_optix`

## Correctness Evidence

Local checks completed on macOS:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal2684_generic_rt_hit_stream_handoff_test
PYTHONPATH=src:. python3 -m unittest tests.goal2644_raydb_paper_rt_contract_test tests.goal2683_v2_5_triton_partner_gpu_validation_test
python3 -m py_compile src/rtdsl/generic_primitives.py src/rtdsl/embree_runtime.py src/rtdsl/optix_runtime.py examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py
python3 -m py_compile scripts/goal2684_raydb_hit_stream_triton_pod_runner.py
make build-embree
```

Local smoke evidence:

- CPU hit stream deduplicates primitives and fails closed on overflow.
- CPU hit stream reproduces grouped-reduction inputs.
- Embree native hit stream emits app-free rows and matches the CPU contract on a
  small deterministic fixture.
- RayDB full-path mapping is correct with CPU hit stream plus reference
  continuation.
- Native ABI source checks confirm the new exported symbols and reject RayDB/SQL
  vocabulary in the reviewed native files.

Pod checks completed on an NVIDIA L4 pod:

```bash
ssh root@213.173.105.24 -p 10842 -i ~/.ssh/id_ed25519_rtdl_codex
RTDL_OPTIX_LIB=build/librtdl_optix.so PYTHONPATH=src:. python3 -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test
```

Result: `Ran 23 tests ... OK`.

Pod environment:

- GPU: `NVIDIA L4`, driver `580.159.04`, memory `23034 MiB`.
- Torch: `2.4.1+cu124`, CUDA available, CUDA `12.4`.
- Triton: `3.0.0`.
- Embree: Ubuntu `libembree-dev` package, runtime reported `3.12.2`.
- OptiX headers: `/root/vendor/optix-dev`, cloned from NVIDIA `optix-dev`
  tag `v8.0.0`.
- Native libraries built: `build/librtdl_embree.so`,
  `build/librtdl_optix.so`.

Two pod-only implementation issues were found and fixed before accepting the
artifact:

- Triton JIT kernel factories now publish `triton` and `tl` into module globals
  after lazy import so annotations such as `tl.constexpr` compile on the pod.
- `RAY_TRIANGLE_HIT_STREAM_3D` CPU reference now unpacks packed 3-D rays and
  triangles for reference-mode RayDB mapping checks instead of assuming
  tuple-only inputs.

## Performance Evidence Status

No public speedup claim is authorized by this report. The following numbers are
accepted as internal Goal2684 pod evidence by post-pod external review.

Goal2684 adds the implementation and runner needed for pod measurement:

```bash
PYTHONPATH=src:. python3 scripts/goal2684_raydb_hit_stream_triton_pod_runner.py \
  --row-counts 1000,10000 \
  --modes count,sum,min,max,avg_as_sum_count \
  --output docs/reports/goal2684_raydb_hit_stream_triton_pod_2026-05-28.json
```

The runner records:

- native RT grouped-reduction timing;
- RT hit-stream plus Triton continuation timing;
- Embree same-contract timing;
- OptiX same-contract timing;
- phase timing for traversal, hit-stream materialization, Triton continuation,
  and total wall time;
- correctness against the CPU reference.

Pod OptiX timing has now been collected and accepted as internal engineering
evidence by post-pod reviews. Public wording remains blocked until a separate
wording review approves exact subpath claims and caveats.

Pod artifacts:

- `docs/reports/goal2684_raydb_hit_stream_triton_pod_2026-05-28_small.json`
- `docs/reports/goal2684_raydb_hit_stream_triton_pod_2026-05-28_100k.json`

Both artifacts report `status: ok`, `all_correct: true`, and
`no_public_speedup_claim: true`.

Small all-mode matrix, 10k rows, 128 groups, median wall time ratios:

| Mode | Native OptiX vs Embree | Hit-stream OptiX+Triton vs Embree+Triton |
| --- | ---: | ---: |
| `count` | 5.19x | 3.95x |
| `sum` | 11.84x | 11.09x |
| `min` | 10.81x | 9.49x |
| `max` | 13.01x | 8.23x |
| `avg_as_sum_count` | 10.82x | 9.89x |

Larger count/sum matrix, 100k rows, 1024 groups, median wall time:

| Mode | Embree Native | OptiX Native | Native Ratio | Embree Hit-Stream+Triton | OptiX Hit-Stream+Triton | Hit-Stream Ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `count` | 0.7419 s | 0.1666 s | 4.45x | 0.7994 s | 0.1629 s | 4.91x |
| `sum` | 21.1503 s | 1.7618 s | 12.01x | 22.0326 s | 1.6996 s | 12.96x |

100k OptiX hit-stream phase timing:

| Mode | RT Traversal | Hit-Stream Materialization | Triton Continuation | RT Hit-Stream Total |
| --- | ---: | ---: | ---: | ---: |
| `count` | 0.000167 s | 0.009878 s | 0.007876 s | 0.014257 s |
| `sum` | 0.004831 s | 0.810383 s | 0.015351 s | 0.819278 s |

Main performance finding: the generic OptiX traversal is fast, and the Triton
continuation is small for this measured RayDB workload. Claude's post-pod
review also notes that the 100k hit-stream+Triton path is within about 5% of
the native grouped-reduction path for count/sum. The next bottleneck is row
materialization and app-owned mapping for the larger `sum` path, so the next
engineering target should be device-resident hit-stream handoff or typed
primitive payload columns that let Triton consume native output without a large
host-side row presentation step.

## Boundary Decision

This goal intentionally does not move RayDB semantics into native code. The
native hit-stream primitive does not know:

- scan fields;
- group keys;
- revenue or payload columns;
- SQL or DBMS behavior;
- RayDB query names;
- grouped reduction operation names.

The only app-owned step between RT and Triton is primitive-id lookup into
app-owned group/value columns. That step is allowed because primitive payload
interpretation is not a traversal primitive.

## Review Gate

Post-pod external architecture review is complete for internal Goal2684
acceptance. Public performance wording remains blocked. Any future public
speedup statement still needs a separate wording review that narrows the claim
to exact subpaths and accounts for hit-stream materialization cost.

Reviewers checked:

- native ABI remains app-free;
- overflow is fail-closed;
- OptiX any-hit uses real `optixTrace` traversal;
- Triton continuation is reached through public partner APIs;
- performance artifacts separate traversal, row materialization, continuation,
  and total timing;
- RayDB predicate encoding remains app code.

Imported review status:

- Claude review saved at
  `docs/reports/external_reviews/goal2684_v2_4_v2_5_claude_critical_review_2026-05-28.md`
  returned `Accept with fixes`.
- Response and local fixes are recorded in
  `docs/reports/goal2684_claude_review_response_2026-05-28.md`.
- The pre-pod Claude review did not authorize speedup wording; its requested
  fixes were handled before pod validation.
- A post-pod Gemini review was attempted and saved as an unavailable-review log
  at
  `docs/reports/external_reviews/goal2684_gemini_post_pod_review_unavailable_2026-05-28.log`;
  it contains tool/capacity failures rather than a verdict, so it is not counted
  as consensus.
- Antigravity/Gemini post-pod review saved at
  `docs/reports/external_reviews/goal2684_gemini_post_pod_review_2026-05-28.md`
  returned `Accept`: the generic hit-stream boundary is app-free, OptiX uses
  real GAS plus `optixTrace`, fail-closed overflow is correct, and the pod
  artifacts are credible internal evidence.
- The Antigravity/Gemini review explicitly does not authorize public speedup
  claims because Triton continuation remains slower than PyTorch GPU baselines
  in related validation, and the RayDB hit-stream path is bottlenecked by
  CPU/GPU boundary materialization.
- Claude post-pod critical review saved at
  `docs/reports/external_reviews/goal2684_claude_post_pod_critical_review_2026-05-28.md`
  and
  `docs/reports/external_reviews/goal2684_claude_post_pod_critical_review_2026-05-28.docx`
  returned `Accept`: native hit-stream ABI is app-free, overflow is fail-closed
  on all three backends, OptiX uses real GAS plus `optixTrace`, RayDB encoding
  stays in app code, Triton uses the public partner front door, and pod
  artifacts are credible internal evidence.
- The Claude post-pod review also explicitly blocks public speedup claims and
  identifies device-resident hit-stream handoff, typed primitive payload
  columns, and grouped-reduction kernel redesign as the next engineering work.
