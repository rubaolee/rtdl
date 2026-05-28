# Goal2653 RayDB Paper-Shaped RT Benchmark Closeout

Status: internal closeout. Public speedup wording remains unauthorized until
the normal external-review gate explicitly accepts the exact claim text.

## Scope

This closes the reopened RayDB benchmark slice that started at Goal2644. The
earlier Goal2520-era path was a useful Python+partner+RTDL grouped-reduction
study, but it was not the RayDB paper's RT-core execution shape. The reopened
work changed the benchmark contract to the paper-shaped strategy:

- one logical row lowers to one generic 3-D triangle;
- scan predicates lower to dense `Z` coordinates and `+Z` query rays;
- group ids lower to primitive group ids;
- aggregate values lower to primitive integer payload values;
- native backends perform only generic ray/triangle traversal, primitive-id
  deduplication, and grouped integer reduction.

Python owns RayDB semantics: table generation, predicate encoding, group
encoding, result interpretation, and SQL correctness checks. RTDL native code
does not contain RayDB, SQL, SSB, DBMS, table, query-plan, or database-specific
logic.

## Implemented Result

The app now has paper-shaped RT backends:

- `paper_rt_cpu_reference` for contract checking;
- `paper_rt_embree` for the same generic contract on CPU Embree;
- `paper_rt_optix` for real OptiX GAS plus `optixTrace` execution.

The benchmark runner supports:

- generated deterministic fixtures suitable for RT-vs-Embree stress testing;
- typed packed host buffers, avoiding Python `Triangle3D`/`Ray3D` object
  construction on the measured path;
- prepared static scene, prepared primitive grouped i64 payload, and prepared
  ray batches;
- an app-owned reusable table descriptor that prepares dense scan/group
  encodings once without moving RayDB semantics into the engine;
- optional Torch/CuPy partner-owned query-ray columns for the OptiX path.

The reusable RTDL primitive is still app-agnostic:
`generic_ray_triangle_primitive_grouped_i64_reduction_3d`.

## Correctness Evidence

PostgreSQL was used as an external SQL correctness oracle for generated
fixtures:

- artifact: `docs/reports/goal2649_raydb_generated_postgres_correctness_100k_2026-05-27.json`;
- script: `scripts/goal2648_raydb_postgres_rt_correctness.py`;
- fixture: generated, 100,000 rows, 128 groups, revenue modulus 64;
- backends checked: `paper_rt_embree`, `paper_rt_optix`;
- modes checked: `count`, `sum`;
- result: all compared rows match PostgreSQL.

The focused local/pod unit tests also cover the contract and runner shape:

- `tests.goal2644_raydb_paper_rt_contract_test`;
- `tests.goal2645_raydb_rt_perf_runner_test`.

## Performance Evidence

Primary pod evidence:

- pod: `root@194.68.245.16 -p 22072`;
- GPU: NVIDIA RTX A5000, driver `565.57.01`;
- OptiX SDK: `/workspace/optix-8.1`;
- repo path on pod: `/workspace/rtdl_goal2645`;
- source commit recorded for the current local/pod run:
  `43419882d805e9d71a798c901cb97f05d8b6c8c8`;
- script: `scripts/goal2646_raydb_prepared_payload_perf_pod.py`;
- common workload: generated 2,000,000 rows, 128 groups, revenue modulus 64;
- timing protocol: table descriptor, workload construction, scene/payload
  preparation, and ray-batch preparation complete first; then the prepared query
  is repeated until measured query time reaches about 10 seconds.

Goal2652 artifacts:

- `docs/reports/goal2652_raydb_10s_embree_host_2m_2026-05-27.json`;
- `docs/reports/goal2652_raydb_10s_optix_host_2m_2026-05-27.json`;
- `docs/reports/goal2652_raydb_10s_optix_torch_2m_2026-05-27.json`;
- `docs/reports/goal2652_raydb_10s_prepared_query_configs_2026-05-27.md`.

Goal2652 supersedes the Goal2651 single-run prepared-query speedup numbers for
closeout wording. Goal2651 remains useful for diagnosing setup costs and table
descriptor reuse, but Goal2652's duration-driven protocol runs many prepared
queries for about 10 seconds per configuration and is the designated final
RayDB prepared-query comparison.

Steady-state prepared-query results:

| config | mode | query median ms | measured query iterations | measured query total s | queries/s | correct |
|---|---|---:|---:|---:|---:|---|
| Embree host | count | 4.7154 | 2,062 | 10.002 | 206.2 | yes |
| OptiX host | count | 0.1704 | 56,418 | 10.000 | 5,641.8 | yes |
| OptiX Torch | count | 0.1798 | 53,248 | 10.000 | 5,324.7 | yes |
| Embree host | sum | 98.5329 | 104 | 10.077 | 10.3 | yes |
| OptiX host | sum | 0.9476 | 10,499 | 10.000 | 1,049.9 | yes |
| OptiX Torch | sum | 0.9560 | 10,392 | 10.001 | 1,039.1 | yes |

Allowed internal performance statement:

> For the generated 2M-row RayDB-style fixture, using the same app-owned
> paper-shaped lowering and the same generic RTDL grouped ray/triangle reduction
> contract, steady-state prepared OptiX RT queries are 27.7x faster than
> prepared Embree queries for grouped count and 104.0x faster for grouped sum on
> the RTX A5000 pod.

The comparison row for the main RT-vs-Embree claim is `embree_host` versus
`optix_host`. The `optix_torch` row is a Python+partner+RTDL configuration and
should be reported separately. It shows that partner-owned query columns can
reduce large ray-batch setup, but the steady-state prepared query kernel is the
same OptiX kernel as `optix_host`.

## Claim Boundaries

This closeout does authorize the following internal statement:

- RayDB now has a paper-shaped RT-core benchmark slice in RTDL using a generic
  app-agnostic ray/triangle grouped-reduction primitive.

This closeout does not authorize:

- a whole-app RayDB speedup claim;
- a public speedup claim;
- an authors-code comparison;
- a Crystal, GPU database, PostgreSQL, DuckDB, cuDF, or full DBMS comparison;
- a full SSB paper reproduction;
- a package-install support claim;
- a true zero-copy claim;
- a claim that Torch/CuPy is the fair Embree-vs-OptiX comparison row.

The main reason is setup separation. The strong 27.7x and 104.0x rows measure
steady-state prepared query only. Table descriptor construction, typed workload
buffer construction, scene/GAS build, payload preparation, and ray-batch
preparation remain outside that timing row.

## Engineering Lessons

RayDB clarified three RTDL design points:

- RTDL can express a database-shaped RT workload without native DBMS semantics
  when the app owns query lowering and the engine owns generic traversal plus
  grouped reduction.
- Prepared/static workload reuse is essential. Without separating setup from
  query, RT traversal speed is hidden by Python-owned lowering and buffer
  preparation.
- Partner-owned query buffers are useful, but they should be represented as a
  session-level prepared-buffer contract rather than mixed into the fair
  Embree-vs-OptiX row.

## Remaining Work

These are future improvements, not blockers for the internal benchmark closeout:

- turn the app-owned table descriptor and prepared ray/payload buffers into a
  cleaner reusable RayDB session wrapper;
- reduce setup overhead further through persistent partner/host typed buffers;
- add a reviewed external authors-code or DBMS comparison only if the input,
  query, output contract, and environment can be made comparable;
- promote public wording only after Claude/Gemini review and a consensus file
  explicitly approve the exact claim.

## Closeout Decision

RayDB is closed as an internal benchmark app for RTDL design pressure and
RT-vs-Embree prepared-query evidence. It should remain in the promoted benchmark
app list with a strict prepared-query boundary and with the old partner-resident
Goal2520 path treated as historical supporting evidence, not the current RT-core
claim.
