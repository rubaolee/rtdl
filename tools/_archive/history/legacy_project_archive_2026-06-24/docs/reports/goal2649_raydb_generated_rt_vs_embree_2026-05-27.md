# Goal2649 RayDB Generated RT-vs-Embree Evidence

Date: 2026-05-27

Status: internal engineering evidence. Public performance wording remains
blocked until review/consensus cites the exact scripts, artifacts, hardware,
commit, and output contract.

## Purpose

The earlier RayDB repeated fixture was not a fair RT-core benchmark. It created
millions of triangles by repeating only eight base records, which collapsed the
RayDB paper mapping onto very few coordinates and very few query rays. That
shape is useful for regression, but it starves RT-core parallelism and creates
duplicate/atomic pressure that does not represent the paper's intended
ray-triangle execution.

This goal adds a deterministic generated fixture and reruns correctness and
performance evidence under the paper-shaped RayDB contract.

## Paper Contract Checked

The current RTDL RayDB paper-shaped path follows the core RayDB strategy:

- each logical row is encoded as one right triangle;
- aggregate value is encoded on `X`;
- dense group id is encoded on `Y`;
- scan predicate tuple is mixed-radix encoded on `Z`;
- query predicates produce `+Z` rays through the query region;
- any-hit/native traversal deduplicates primitive ids;
- grouped integer reductions consume generic primitive group ids and values.

The native engine contract remains app-agnostic. Native Embree/OptiX code sees
only generic 3-D rays, triangles, primitive ids, group ids, integer payload
values, deduplication, and reductions. It does not contain RayDB, SQL, table,
SSB, database, or query-plan vocabulary.

## Correctness

PostgreSQL was used as an external SQL oracle on the generated fixture:

- artifact: `docs/reports/goal2649_raydb_generated_postgres_correctness_100k_2026-05-27.json`
- script: `scripts/goal2648_raydb_postgres_rt_correctness.py`
- fixture: `generated`, 100,000 rows, 128 groups, revenue modulus 64
- backends: `paper_rt_embree`, `paper_rt_optix`
- modes: `count`, `sum`
- result: all compared rows match PostgreSQL.

This verifies both native paths against SQL semantics for the generated fixture.

## Performance Results

Pod hardware and environment:

- host: `4b7c6ab4b262`
- GPU: NVIDIA RTX A5000, driver 565.57.01, CUDA 12.7
- OptiX SDK: `/workspace/optix-8.1`
- build: `make build-embree` and `make build-optix OPTIX_PREFIX=/workspace/optix-8.1 OPTIX_CUDA_ARCH=sm_86`
- source commit recorded by pod artifact: `43419882d805e9d71a798c901cb97f05d8b6c8c8`

Same-contract generated 2M-row comparison:

Artifact: `docs/reports/goal2649_raydb_generated_embree_vs_optix_2m_2026-05-27.json`

| mode | rows | triangles | rays | Embree median s | OptiX median s | Embree / OptiX | correctness |
|---|---:|---:|---:|---:|---:|---:|---|
| count | 2,000,000 | 2,000,000 | 110,592 | 1.403637 | 0.983565 | 1.427x | true |
| sum | 2,000,000 | 2,000,000 | 4,755,456 | 1.910426 | 1.378547 | 1.386x | true |

Same-contract generated 100k-row comparison:

Artifact: `docs/reports/goal2649_raydb_generated_embree_vs_optix_100k_2026-05-27.json`

| mode | rows | triangles | rays | Embree median s | OptiX median s | Embree / OptiX | correctness |
|---|---:|---:|---:|---:|---:|---:|---|
| count | 100,000 | 100,000 | 97,536 | 0.077891 | 0.049762 | 1.565x | true |
| sum | 100,000 | 100,000 | 4,194,048 | 0.551186 | 0.451998 | 1.219x | true |

The generated fixture now produces the desired RT-vs-Embree result: OptiX is
faster than Embree on the same paper-shaped generic primitive contract.

## Prepared Query Buffers

The next optimization target was prepared ray/query buffers and partner-owned
query columns. That path is now implemented and measured.

Prepared host ray batch, generated 2M rows:

Artifact: `docs/reports/goal2649_raydb_generated_prepared_host_2m_2026-05-27.json`

| mode | rays | workload build s | prepare scene/payload s | prepare ray batch s | prepared query median s | correctness |
|---|---:|---:|---:|---:|---:|---|
| count | 110,592 | 0.528242 | 0.498125 | 0.002238 | 0.000233 | true |
| sum | 4,755,456 | 0.813706 | 0.123695 | 0.126912 | 0.001108 | true |

Prepared Torch-owned CUDA query columns, generated 2M rows:

Artifact: `docs/reports/goal2649_raydb_generated_prepared_torch_2m_2026-05-27.json`

| mode | rays | workload build s | prepare scene/payload s | partner ray columns s | prepare ray batch s | prepared query median s | correctness |
|---|---:|---:|---:|---:|---:|---:|---|
| count | 110,592 | 0.551310 | 0.507182 | 1.633784 | 0.004490 | 0.000286 | true |
| sum | 4,755,456 | 0.768676 | 0.098692 | 0.005165 | 0.010682 | 0.001141 | true |

The Torch count partner-column build includes first-use Torch/CUDA startup cost.
The sum row is the better steady-state indicator: partner-owned ray columns are
built on CUDA in about 5 ms, then packed into the generic prepared RTDL ray
batch in about 11 ms.

Transfer metadata confirms:

- partner CUDA device pointers were observed;
- query rays were packed on device once;
- query rays were not uploaded on each repeated run;
- primitive group ids and values were not uploaded on each repeated run;
- the prepared static scene and prepared primitive payload remained device-side.

This is not claimed as true zero-copy yet, because RTDL still packs partner ray
columns into its internal prepared ray batch.

## Python-vs-Partner Boundary

Python still owns RayDB semantics:

- fixture/table generation;
- predicate-to-axis encoding;
- query-region construction;
- output row naming and comparison to SQL oracle.

The runtime now supports partner-owned query columns for the generic ray batch.
That removes per-query Python ray materialization from the repeated-query path.
Remaining overhead is mostly app-side workload construction and host-side
triangle/payload preparation. The next meaningful optimization, if RayDB stays
active, is partner-owned triangle/payload columns or a reusable prepared table
descriptor so generated query batches can be run without rebuilding the table
shape.

## Conclusion

The weak earlier 2M-row result was caused by the wrong benchmark fixture, not by
the absence of RT execution. With a generated fixture that exercises the RayDB
paper shape, `paper_rt_optix` is now faster than `paper_rt_embree`:

- 1.43x for `count` at 2M rows;
- 1.39x for `sum` at 2M rows;
- both match PostgreSQL on the generated correctness fixture.

This is the correct internal direction for RayDB: keep the native primitive
generic, keep RayDB lowering in Python/app space, and measure RT-vs-Embree on
generated or real workloads with enough ray/triangle diversity.
