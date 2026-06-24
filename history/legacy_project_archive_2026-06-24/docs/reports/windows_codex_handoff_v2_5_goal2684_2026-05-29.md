# Windows Codex Handoff: RTDL v2.5 After Goal2684

Date: 2026-05-29
Repo: `https://github.com/rubaolee/rtdl.git`
Branch: `main`

Read this file first in a fresh Windows Codex session. It is intended to be
self-contained enough to continue development from a clean clone.

## Current Project State

RTDL is in the v2.5 `Python + RTDL + Triton` partner track.

The key execution architecture is:

```text
Python app logic
-> RTDL native traversal through Embree/OptiX
-> generic RT hit stream
-> Triton partner continuation
-> app-owned result formatting
```

RT traversal remains in RTDL native backends. Triton is the continuation partner
after traversal; it must not replace RT traversal.

Current standing rule: native engines must stay app-free. Do not add RayDB,
SQL, DBSCAN, Barnes-Hut force law, graph, collision, or other benchmark-specific
semantics into native Embree/OptiX engine code.

Public speedup wording is still blocked unless a separate exact-wording review
approves the precise claim. Internal engineering evidence is allowed.

## Goal2684 Status

Goal2684 is accepted as an internal architecture/correctness milestone.

Implemented primitive:

- `RAY_TRIANGLE_HIT_STREAM_3D`
- Row schema: `(ray_id, primitive_id)`
- Backends: CPU reference, Embree, OptiX
- Overflow policy: fail-closed bounded rows. On overflow, no partial rows are
  returned.

Implemented full RayDB path:

- `paper_rt_embree_hit_stream_triton`
- `paper_rt_optix_hit_stream_triton`

Execution shape:

```text
RayDB app-owned table/predicate encoding
-> generic rays and triangles
-> Embree/OptiX RAY_TRIANGLE_HIT_STREAM_3D
-> app-owned primitive_id -> group/value mapping
-> Triton grouped continuation through public partner adapters
-> RayDB-style app rows
```

## Main Files To Know

Generic primitive and wrappers:

- `src/rtdsl/generic_primitives.py`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/primitive_hierarchy.py`
- `docs/rtdl_primitive_catalog.md`

Native Embree implementation:

- `src/native/embree/rtdl_embree_prelude.h`
- `src/native/embree/rtdl_embree_scene.cpp`
- `src/native/embree/rtdl_embree_api.cpp`

Native OptiX implementation:

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`

Triton partner and migration state:

- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/v2_5_triton_app_migration.py`

RayDB benchmark app:

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `examples/v2_0/research_benchmarks/raydb_style/README.md`

Runner and tests:

- `scripts/goal2684_raydb_hit_stream_triton_pod_runner.py`
- `tests/goal2684_generic_rt_hit_stream_handoff_test.py`
- `tests/goal2662_v2_5_partner_continuation_contract_test.py`
- `tests/goal2671_v2_5_preview_gate_test.py`
- `tests/goal2679_v2_5_triton_grouped_argmin_preview_test.py`

## Evidence And Reports

Primary Goal2684 report:

- `docs/reports/goal2684_generic_rt_hit_stream_handoff_2026-05-28.md`

Consensus:

- `docs/reports/goal2684_post_pod_consensus_2026-05-28.md`

Pod artifacts:

- `docs/reports/goal2684_raydb_hit_stream_triton_pod_2026-05-28_small.json`
- `docs/reports/goal2684_raydb_hit_stream_triton_pod_2026-05-28_100k.json`

External reviews:

- `docs/reports/external_reviews/goal2684_v2_4_v2_5_claude_critical_review_2026-05-28.md`
- `docs/reports/goal2684_claude_review_response_2026-05-28.md`
- `docs/reports/external_reviews/goal2684_gemini_post_pod_review_2026-05-28.md`
- `docs/reports/external_reviews/goal2684_claude_post_pod_critical_review_2026-05-28.md`

External review verdicts:

- Pre-pod Claude: `Accept with fixes`; fixes were handled.
- Post-pod Antigravity/Gemini: `Accept`.
- Post-pod Claude: `Accept`.
- All reviews block public speedup wording for now.

## Validation Already Done

Local macOS checks passed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test

python3 -m py_compile \
  src/rtdsl/generic_primitives.py \
  src/rtdsl/triton_partner_continuation.py \
  scripts/goal2684_raydb_hit_stream_triton_pod_runner.py \
  examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py

git diff --check
```

Pod validation passed on NVIDIA L4:

- Pod SSH used during validation:
  `ssh root@213.173.105.24 -p 10842 -i ~/.ssh/id_ed25519`
- On this Mac the working key path was:
  `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`
- GPU: `NVIDIA L4`, driver `580.159.04`, memory `23034 MiB`
- Torch: `2.4.1+cu124`
- CUDA: `12.4`
- Triton: `3.0.0`
- OptiX headers: `/root/vendor/optix-dev`, NVIDIA `optix-dev` tag `v8.0.0`
- Embree runtime: `3.12.2`

Pod test command passed:

```bash
RTDL_OPTIX_LIB=build/librtdl_optix.so PYTHONPATH=src:. python3 -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test
```

Result: `Ran 23 tests ... OK`.

Pod runner artifacts report `status: ok`, `all_correct: true`, and
`no_public_speedup_claim: true`.

## Performance Conclusions

Internal evidence only:

- OptiX traversal is fast.
- Triton continuation is small for the measured RayDB count/sum cases.
- The 100k hit-stream+Triton path is within about 5% of native grouped
  reduction for count and sum, per Claude post-pod review.
- OptiX vs Embree internal ratios on the measured RayDB subpaths are positive.

Blocked public claims:

- Do not publish any broad speedup claim.
- Do not claim Triton continuation is production-performance-ready.
- Do not claim external database/tool speedups from Goal2684 artifacts; no
  PostgreSQL/DuckDB/pandas baseline is part of these artifacts.

Main bottleneck:

- `sum` at 100k is dominated by hit-stream materialization and app-owned mapping.
- Example from the 100k OptiX hit-stream artifact:
  - RT traversal: `0.004831 s`
  - hit-stream materialization: `0.810383 s`
  - Triton continuation: `0.015351 s`
  - RT hit-stream total: `0.819278 s`

## Critical Design Boundary

Native code may know:

- rays;
- triangles;
- primitive ids;
- row capacity;
- overflow bit;
- backend traversal state.

Native code must not know:

- RayDB;
- SQL;
- table fields;
- scan predicates;
- group keys;
- aggregate names;
- revenue/quantity/discount/ship-year semantics;
- any benchmark-specific continuation math.

If a future implementation needs group ids, values, or payloads near the native
boundary, it must be expressed as a generic typed payload-column contract, not a
RayDB-specific ABI.

## Recommended Next Goal

Suggested next goal: `Goal2685: Device-Resident Hit-Stream Handoff And Typed
Payload Columns`.

Purpose:

Remove the current host-side materialization bottleneck while preserving the
app-free native engine boundary.

Measurable milestones:

1. Define a generic device-resident hit-stream contract.
   Output must remain app-free, e.g. typed columns for `ray_id` and
   `primitive_id`, plus explicit row count and overflow metadata.
2. Add a safe ownership/lifetime model between OptiX output buffers and partner
   continuation.
   Triton must be able to consume the RT-produced columns without Python
   rebuilding large host rows.
3. Define generic typed primitive payload columns.
   Payload columns can map primitive ids to group ids and values, but names and
   types must remain generic, not RayDB-specific.
4. Implement RayDB count/sum through the new device-resident path.
   Correctness must match CPU reference.
5. Measure phase timings separately:
   scene build, query prep, RT traversal, device handoff, Triton continuation,
   host materialization, total.
6. Compare against the current Goal2684 native grouped-reduction and
   hit-stream+Triton paths.
7. Preserve public-claim gate:
   internal evidence only until exact wording receives external review.

Likely technical risk:

- Python/Triton currently expects torch tensors. OptiX native buffers are not
  automatically torch tensors. The next work needs a principled buffer handoff,
  possibly via DLPack/CUDA array interface/explicit device pointer wrapper, or a
  controlled intermediate that still avoids large host-side row reconstruction.

## Suggested First Commands For Windows Codex

From a clean clone:

```bash
git clone https://github.com/rubaolee/rtdl.git
cd rtdl
git status --short --branch
PYTHONPATH=src:. python3 -m unittest tests.goal2684_generic_rt_hit_stream_handoff_test
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test
```

If using a GPU pod:

```bash
make build-embree
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev
RTDL_OPTIX_LIB=build/librtdl_optix.so PYTHONPATH=src:. python3 -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test
```

## Operational Notes

- Use source-tree execution: `PYTHONPATH=src:. python ...`.
- Do not claim `pip install -e .` support.
- Preserve existing reports and JSON artifacts. Do not rewrite historical
  artifacts unless a current generator/test explicitly owns the file.
- For public claim, roadmap, release, or architecture boundary changes, write a
  report under `docs/reports/`, obtain external review, and write consensus only
  after review artifacts exist.
- Gemini CLI can fail with capacity/tool errors; save failures honestly and do
  not count them as consensus.
- Claude/Gemini/Antigravity reviews count only when their output is saved in
  the repo and includes a clear verdict.

## Current Bottom Line

RTDL v2.5 has a validated first full `RT + Triton` app path. The architecture is
accepted. The next development should focus on making the RT-to-Triton boundary
device-resident and generic, not on adding app-specific native shortcuts.
