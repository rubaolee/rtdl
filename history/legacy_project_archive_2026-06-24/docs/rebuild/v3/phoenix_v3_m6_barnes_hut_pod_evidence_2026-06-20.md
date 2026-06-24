# Phoenix V3 M6 Barnes-Hut Pod Evidence

Status: internal M6 route-parity evidence, 2026-06-20.

This is not release authorization and not a Barnes-Hut RT-core speedup claim.

## Scope

Goal4392 M6 asks whether Barnes-Hut-style workloads can be expressed as
generic frontier, node-summary, and vector-accumulation work without creating a
native Barnes-Hut force-law engine.

This run tests the current V3 answer under one force-summary contract:

- fused CPU/Numba;
- fused Numba CUDA;
- prepared RTDL/OptiX aggregate-frontier device columns plus Numba;
- prepared RTDL/OptiX aggregate-frontier device columns plus CuPy.

The generic capability is:

```text
aggregate_frontier_vector_accumulation
```

## Pod And Artifacts

Pod:

- `root@213.173.108.14 -p 11592`
- GPU: NVIDIA RTX 4000 Ada Generation, driver `550.127.05`, 20475 MiB
- workdir: `/root/rtdl_v3_rebuild_20260620/current`
- artifact root copied locally to
  `docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620`

Important files:

```text
docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_rerank.log
docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_partitioned.log
docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json
docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_intake_summary.json
docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_intake_summary.md
```

The first single-process attempt is intentionally preserved. It failed with
CUDA out-of-memory while running the prepared OptiX route because the historical
rerank runner retains raw payloads across body counts. The successful run uses
one body count per process and then merges the JSON outputs.

## Result

Intake status:

```text
status: pass
overall_status: internal_m6_route_parity_evidence
release_authorized: false
public_speedup_claim_authorized: false
rt_core_speedup_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

Route matrix:

| Bodies | Fastest route | Fastest | OptiX+Numba | OptiX+Numba / fastest | Contribution rows | Checksum parity |
|---:|---|---:|---:|---:|---:|---|
| 32,768 | `numba_cuda_fused` | 11.249 ms | 82.435 ms | 7.328x | 15,514,679 | pass |
| 65,536 | `numba_cuda_fused` | 34.738 ms | 177.858 ms | 5.120x | 55,935,606 | pass |
| 131,072 | `numba_cuda_fused` | 44.445 ms | 618.302 ms | 13.912x | 68,023,506 | pass |

Ratios in this table use mixed timing bases: fused Numba CUDA uses CUDA-event
kernel time when available, while CPU/Numba and prepared OptiX routes use the
runner's wall-clock hot median. These ratios are internal route guidance, not
kernel-to-kernel comparisons.

All three scales have all four routes present, matching contribution row
counts, checksum deltas inside tolerance, and false release/public/RT-core
speedup claim flags.

## Interpretation

The useful V3 lesson is not that RT cores win this route. They do not, under the
current prepared aggregate-frontier contract.

The current high-performance Barnes-Hut shape is fused continuation:

```text
traversal + opening decision + weighted-vector accumulation
```

The prepared RTDL/OptiX route remains valuable as bounded device-column and
aggregate-frontier evidence, but it emits the wrong hot-path shape for this
workload. It still pays the aggregate-frontier contract before vector
accumulation, so it loses to the fused Numba CUDA route in this run.

The 32,768-body row changed relative to the historical M62 packet, where
CPU/Numba was fastest. That does not authorize automatic route selection. It
means Barnes-Hut route choice is scale- and environment-sensitive. V3 must keep
route and partner choice explicit until an M7-quality policy exists.

## Boundary

This evidence does not claim:

- Barnes-Hut RT-core speedup;
- whole N-body speedup;
- paper reproduction;
- automatic route or partner selection;
- native Barnes-Hut force-law ABI;
- true zero-copy product behavior.

Large rows are route-parity evidence, not full exact-force oracle rows. Exact
force validation above 2048 bodies is intentionally not used as the timed large
row because it would measure a different O(N^2) reference workload.

## M6 Decision

M6 now has serious internal pod evidence for the aggregate-frontier/vector
capability. It should remain internal until M7 row review.

The next M6-related work is not more tuning of the prepared OptiX frontier row
emission contract. The only plausible RT-core Barnes-Hut performance path is a
reviewed, app-agnostic fused aggregate-tree weighted-vector primitive that
avoids frontier row emission and is compared directly against fused CPU/Numba
and fused Numba CUDA.

## Goal-Level Decision Audit

Decision: accept the partitioned pod rerun as internal M6 route-parity evidence,
but keep all release/public claim flags false.

1. Was I foolish?

   The corrected decision is not foolish. The failed single-process run was a
   useful warning about runner memory retention, and the successful partitioned
   run preserves the same logical route contract without hiding the failure.

2. If yes, what actions made the decision foolish?

   The foolish action was attempting 32k/65k/131k in one process even though the
   runner stores raw payloads. That made CUDA OOM possible before evidence could
   be interpreted.

3. Was there another path?

   Yes. Run one body count per process from the start, then merge the artifacts.

4. Can I now try a different path that actually solves the problem?

   Yes. The current path solves the evidence problem: preserve the OOM log,
   gather non-toy route-parity rows, record the claim boundary, and keep M6 out
   of release wording until M7 review.
