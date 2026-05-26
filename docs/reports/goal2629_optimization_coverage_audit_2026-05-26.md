# Goal2629 Optimization Coverage Audit For Embree vs OptiX Baseline

Date: 2026-05-26

This is an internal RTDL engineering note. It audits whether the current
Goal2628 Embree-vs-OptiX matrix exercised the runtime optimizations already
built in the project, especially prepared scenes, grouped continuations,
partner/device-resident data paths, typed buffers, and zero-copy-like paths.

## Short Answer

No, the current matrix did not use every optimization we have built. It did use
the important RT-shaped optimizations for several apps, and those are exactly
the rows where OptiX wins clearly. It did not fully use true zero-copy,
typed/partner-resident column buffers, or same-contract device-resident
continuations in several slower rows.

The useful conclusion is not "RT is slow." The useful conclusion is: RTDL now
has enough optimized paths to show strong OptiX wins on several benchmark apps,
but the remaining slow apps are still running through first-wave or fallback
paths rather than the best runtime mechanisms.

## Optimization Coverage By App

| App / path | Important optimizations actually used | Important optimizations not fully used | Current implication |
| --- | --- | --- | --- |
| RT-DBSCAN | Prepared OptiX scene, CuPy partner columns, device output reuse, threshold count, blocked grouped stream continuation, no Python neighbor-row materialization on OptiX. | Whole-path true zero-copy is still not authorized; Embree row still materializes neighbor rows. | Strong RT evidence: OptiX wins once scale amortizes setup. |
| RTNN | Prepared OptiX search structure, device-ranked summary rows, no OptiX neighbor-row materialization. | Embree path materializes rows and folds in Python; whole-app broad RT claim still blocked. | Strong OptiX evidence for ranked fixed-radius summaries. |
| LibRTS AABB index | Generic OptiX AABB index path, prepared scene/query phases, no LibRTS-specific native symbol. | Embree path is generic columnar conjunctive scan and can become pathological; no partner-resident data reuse across query batches in the reported row. | Strong OptiX evidence for high-volume AABB queries, but Embree implementation is not yet equally optimized. |
| Hausdorff / X-HD | Prepared fixed-radius threshold query, native threshold decision, no heavy Python postprocess. | Scene preparation is still material; full multi-query scene reuse was not the primary reported metric. | Good RT evidence; larger-scale result remains OptiX-positive. |
| Robot collision | Prepared collision flags, device-buffer path, native app-agnostic primitive route. | Wall time still dominated by app setup/lowering in some runs. | Native timing shows RT win; wall-time claims need care. |
| Contact manifold | Native `COLLECT_K_BOUNDED` sort/copy path, fail-closed bounded collector semantics. | App-owned Python witness discovery dominates wall time; witness discovery is not yet generic RT traversal. | Good primitive semantics evidence, weak RT-throughput evidence. |
| RayDB-style count/sum | Direct columnar record-set lowering; experimental partner-resident descriptor probe exists. | Main matrix does not use true zero-copy or typed host buffers; metadata says `true_zero_copy_authorized=false`, `all_numeric_columns_use_typed_host_buffers=false`, and six columns are copied. Partner-resident probe is descriptor-only and not RT-core accelerated. | This is a real runtime gap; current OptiX loss is mostly a data-movement/layout/reduction-path problem. |
| Spatial RayJoin | Generic same-front-door route exists; prepared OptiX route exists for narrower PIP/LSI paths. | Full reported route does not use prepared device-resident row-stream continuation for overlay; setup dominates tiny fixture. | Current OptiX loss is not a valid final RT claim path. |
| Triangle counting | Native continuation front door exists and is app-agnostic. | Reported OptiX path says `rt_core_accelerated=false`; it is a host-indexed fallback, not a real RT-core graph triangle path. | Current loss is a missing primitive/path issue, not RT evidence. |
| Barnes-Hut | Some prepared node-coverage / candidate-summary native paths exist. | Embree and OptiX rows are not same-contract; no generic hierarchical aggregate-frontier primitive with parity yet. | Current loss is not a clean benchmark comparison. |

## Zero-Copy Status

We should be precise with vocabulary:

- Some current OptiX paths use device output reuse or direct device handoff.
- Some paths avoid Python row materialization.
- Some paths pass partner/device descriptors experimentally.
- Those are not the same as a fully authorized, whole-path true zero-copy
  claim.

The strongest evidence that zero-copy is not fully active is RayDB. Its
Goal2628 payload explicitly reports:

- `true_zero_copy_authorized=false`
- `all_numeric_columns_use_typed_host_buffers=false`
- `typed_host_buffer_column_count=0`
- `transfer_path=direct_columnar_record_set_to_columnar_payload`

The partner-resident RayDB probe did observe CUDA device pointers and used
descriptor-only transfer mode, but it still reports:

- `true_zero_copy_authorized=false`
- `direct_device_handoff_authorized=false`
- `rt_core_accelerated=false`

So RayDB is the clearest place where we spent serious work on partner/device
boundaries, but the current benchmark matrix did not yet exercise the final
fast version of that idea.

## What We Did Use Successfully

The current OptiX wins came from concrete runtime features:

- Prepared RT scenes and prepared search structures.
- Native threshold/count/reduction summaries instead of row-returning Python
  loops.
- Blocked grouped stream continuation for RT-DBSCAN.
- Device-ranked summaries for RTNN.
- App-agnostic AABB index queries for LibRTS.
- Native bounded collection for contact-manifold semantics.
- CUDA 12.6 `nvcc` PTX path on the pod, avoiding driver/toolchain mismatch.

These are real and should be preserved as the positive RT story.

## What We Did Not Use Enough

The next RT-performance work should not be broad reruns. It should target the
missing fast paths:

1. RayDB needs typed, partner-resident column buffers, chunking past the current
   1M-row native cap, and a device-resident grouped reduction/finalize path.
2. Spatial RayJoin needs prepared device-resident row-stream continuation for
   overlay-style workloads.
3. Triangle counting needs a real RT-core graph triangle-count path; current
   OptiX is fallback.
4. Barnes-Hut needs a same-contract hierarchical aggregate-frontier primitive
   for Embree and OptiX.
5. Contact manifold needs generic RT witness discovery before it can be an
   RT-throughput benchmark rather than a bounded-collector semantics benchmark.

## Current Performance Interpretation

For RT performance claims, the current clean positive rows are:

- Hausdorff / X-HD: OptiX `1.55x` to `3.17x` faster depending on scale.
- RT-DBSCAN: OptiX `17.0x` faster at calibrated 8192-point clustered workload.
- Robot collision: OptiX `6.51x` faster for prepared collision flags.
- LibRTS AABB index: OptiX `21.4x` faster at 1024 boxes / 512 queries in the
  calibrated report.
- RTNN: OptiX `171x` to `314x` faster for ranked fixed-radius summary.
- Contact native collector: OptiX `1.09x` faster, but this is primitive-copy /
  bounded-sort evidence, not full traversal evidence.

The current negative rows should be treated as optimization backlog:

- RayDB: real data movement / reduction gap.
- Spatial RayJoin: missing prepared continuation for the full route.
- Triangle counting: fallback instead of RT-core graph path.
- Barnes-Hut: contract mismatch.

## Recommended Next Pod Use

While the pod is available, the best use is:

1. Re-run the clean positive RT paths at larger second-scale workloads to reduce
   setup noise and strengthen the baseline.
2. Run targeted RayDB experiments with partner-resident typed/chunked paths
   before broad matrix reruns.
3. Do not spend pod time rerunning fallback Triangle/Barnes-Hut/Spatial-RayJoin
   rows unless the missing primitive path is implemented first.
4. If we collect v2.0-era Embree-vs-OptiX app comparisons, label them as
   historical app-era evidence, not promoted-benchmark evidence.

