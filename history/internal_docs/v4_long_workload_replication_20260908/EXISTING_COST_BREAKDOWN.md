# Existing successor cost and measurement-boundary recount

Date: 2026-09-08 America/New_York.

This report derives coarse costs from every formal worker in the immutable
1,049-member archive
`rtdl-v4-long-perf-successor-02e84374f-affinity-final.tar.gz`, SHA-256
`ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc`.
It does not rerun GPU code and is not pooled into the planned temporal
replication.

## 1. Timing boundary

- `load` runs before the primary timer. It loads and derives the shared input,
  including graph CSR construction and other common preprocessing.
- `prepare` creates the arm-specific owner and deploys its static state.
- `complete` primary time starts after load and includes prepare, one checked
  adapter action, and close.
- `prepared` primary time includes one checked adapter action after one untimed
  warmup. The table reports the worker median of 32 Particle actions, four
  com-dblp/LibRTS actions, or three cit-Patents actions.
- The checked adapter action still includes synchronous native/device status,
  result comparison or digest checks, and compact evidence construction before
  return. It is not isolated OptiX traversal time.
- Journal writes follow the action timer. The worker output/digest oracle that
  consumes the returned action result follows the action timer, but checks
  performed inside the adapter do not.
- `worker wall` additionally includes imports, identity checks, the untimed
  warmup, all repetitions, evidence handling and process overhead. It is not a
  primary endpoint.

Each number below is a separate median over the eight workers for that arm and
endpoint. Columns must not be added: medians are taken independently, complete
already encloses prepare/action/close, and worker wall overlaps all phases.

## 2. Coarse measured costs

All values are milliseconds. Each cell is `successor RTDL / public PyOptiX`.

| Task/input | Endpoint | Load | Prepare | Primary | Close | Worker wall |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Particle/5K | Complete | 1137.675 / 1201.898 | 407.258 / 2400.685 | 449.191 / 2401.614 | 4.803 / 0.046 | 1873.519 / 3936.628 |
| Particle/5K | Prepared | 1067.494 / 1058.382 | 410.427 / 2211.284 | 0.401628 / 0.542063 | 4.873 / 0.063 | 2286.942 / 4005.828 |
| com-dblp/1M | Complete | 1532.687 / 1525.024 | 437.913 / 2356.844 | 3764.218 / 3636.298 | 0.403 / 0.035 | 5659.652 / 5522.544 |
| com-dblp/1M | Prepared | 1660.386 / 1557.820 | 445.200 / 2511.312 | 478.396 / 435.101 | 0.484 / 0.040 | 7995.634 / 7592.578 |
| LibRTS point | Complete | 2175.796 / 2184.718 | 1382.965 / 4432.572 | 1448.309 / 4433.528 | 64.565 / 0.051 | 3942.953 / 6998.504 |
| LibRTS point | Prepared | 2159.110 / 2204.456 | 1387.049 / 4351.350 | 0.256184 / 0.251229 | 64.847 / 0.054 | 4047.387 / 6979.398 |
| LibRTS range | Complete | 3889.206 / 3912.718 | 1564.935 / 4450.697 | 1629.449 / 4451.665 | 63.913 / 0.060 | 5854.549 / 8732.995 |
| LibRTS range | Prepared | 3869.503 / 3839.604 | 1577.111 / 4327.355 | 0.252307 / 0.259447 | 65.083 / 0.067 | 5934.570 / 8621.229 |
| cit-Patents/4M | Complete | 15512.179 / 15314.788 | 468.538 / 2422.500 | 12712.176 / 12257.453 | 0.457 / 0.051 | 28634.731 / 27899.620 |
| cit-Patents/4M | Prepared | 16056.433 / 15680.513 | 453.267 / 3118.971 | 9347.909 / 8802.240 | 0.511 / 0.062 | 58857.128 / 55973.524 |

The separate arm medians do not define the paired ratio. The formal statistic
first divides the integer-nanosecond worker medians within each block and then
takes the median of eight ratios. For example, the displayed cit-Patents
prepared arm medians divide to about `1.061992`, while the correct paired
median is `1.057361` and the largest block is `1.083735`.

## 3. Source-backed route mechanisms

These are implementation facts, not allocations of measured time.

| Route | Successor RTDL | Public PyOptiX | Comparison limitation |
| --- | --- | --- | --- |
| Particle | Hash-admitted `.rtdlexe`; strict-interior standard-library specialization; full ordered U32x3 output, equality check, digest and compact traversal evidence inside adapter action | Hash-bound precompiled PTX; semantically matched closest-hit program; full ordered U32x3 output, equality check, digest and operation/status evidence inside adapter action | Device programs and physical algorithms differ. This row does not measure arbitrary user callback code or full 50,000-step advection. |
| Triangle | Hash-admitted general-leaf `.rtdlexe`; device columns retained; CuPy checked-U64 weighted reduction; every deterministic segment and compact receipt checked | Hash-bound precompiled PTX; public RT-2A1 owner; retained module/pipeline/SBT, per-segment geometry/GAS and checked-U64 device accumulation | Same application algorithm and output, separately authored physical implementations. Per-segment work remains in prepared action; it is not pure traversal. |
| LibRTS | Fixed AABB count specialization, prepared index/query handles, synchronous scalar/status/receipt return | Public custom-AABB intersection owner, prepared query columns and device U64 count reduction | Layouts, flags and compact kernels differ. Output-equivalent count does not imply instruction identity. |

The large RTDL complete-time gains are consistent with source-visible removal
of repeated compilation/materialization and admitted executable reuse. The
coarse timers do not prove how much of any A/C or old/new difference belongs to
compilation, transfer, traversal, reduction, checking, Python, CuPy or one
specific safeguard.

## 4. Scale and memory facts

| Task | Bound static shape | What is not measured |
| --- | --- | --- |
| Particle | 314,587 vertices, 3,392,530 triangles, 5,000 queries, ordered `5000 x 3` U32 output. The six frozen NumPy arrays alone are about 71.8 MB decimal before runtime copies. | Peak host RSS, peak device allocation, allocator cache, GAS scratch/output, duplicate host/device columns. |
| com-dblp | 8 deterministic segments, 1,006,685 total segment primitives and 3,413,500 total segment queries. | Per-segment peak device memory and preprocessing peak RSS. |
| cit-Patents | 28 deterministic segments, 15,853,615 total segment primitives and 69,850,749 total segment queries. | Per-segment peak device memory, GAS temporary/output and the O(E) CSR preprocessing peak. |
| LibRTS | 11,544,398 indexed boxes and 100,000 queries. The frozen host index columns have a theoretical 36-byte-per-row payload before copies or allocator overhead. | Actual host/device peak, normalized-query copies, GAS scratch/output and owner/runtime overhead. |

The Particle and LibRTS byte calculations are static payload lower bounds, not
formal memory measurements. No manuscript sentence may present them as peak
memory. Formal peak GPU memory remains unmeasured.

## 5. Defensible interpretation

The existing evidence establishes coarse checked-route costs for five exact
task/input configurations on one CPU-pinned RTX A4500 population. It does not
establish a fine-grained causal decomposition. The planned cit-Patents
replication can test temporal repeatability of the only multi-second prepared
row, but it cannot fill the missing traversal/transfer/memory instrumentation
or broaden application coverage.
