# RTNN Paper Reproduction App

This directory is the RTDL reproduction line for:

- **Paper:** *RTNN: Accelerating Neighbor Search Using Hardware Ray Tracing*
- **Author:** Yuhao Zhu
- **Venue:** PPoPP 2022, pages 76-89
- **DOI:** `10.1145/3503221.3508409`
- **Paper:** <https://horizon-lab.org/pubs/ppopp22.pdf>
- **Author repository:** <https://github.com/horizon-research/rtnn>
- **Pinned commit:** `5532e7031d0c8268ffa555972f074f8882b379b5`

## Current Status

`rtnn_scoped_exact_correctness_and_system_extraction_complete__externally_reviewed_and_approved`

Goals5527-5549 are implemented and externally reviewed. The strongest current result is
exact relation correctness through the 12M-search/4,096-query Level-B
same-byte gate plus the generic prepared Q*K system route. Exact paper input
provenance remains `0/9`, so full paper and Figure claims remain false.

Goals5528-5533 now provide two bounded same-input relation-level results on
home Linux smoke hardware:

- the pinned author executable emits 21 strict-radius canonical neighbor rows;
- RTDL emits the same 21 rows with `radius_boundary="open"`;
- missing, unexpected, and distance-mismatch lists are empty;
- a separate facility-safety-zone consumer proves the new generic open/closed
  radius policy outside RTNN;
- on a discriminating exact-KNN fixture, the pinned author and RTDL each emit
  the same 7 canonical `(query_id, neighbor_id, rank, squared_distance)` rows;
- that KNN fixture covers zero-distance duplicate exclusion, open-radius
  exclusion, underfilled and empty queries, more-than-K candidates, and raw
  author result-slot order that differs from canonical rank order.

The bounded results are implemented and awaiting external review. They are not
a full RTNN paper result, dataset/figure reproduction, or performance claim.

Goals5534-5535 extend the exact-KNN comparator beyond the bounded fixture:

- **representative synthetic scale:** 65,536 historical deterministic uniform
  search points and a hashed 4,096-query source-row subset, K=4 and r=0.05;
  the independent reference, author, and RTDL each emit the same 16,384 rows;
- **same-source public geometry:** all 7,108 vertices in the Stanford
  HappyBuddha res4 derivative, K=4 and radius 0.04 times its float32 longest
  axis span; all three routes emit the same 28,432 rows;
- RTDL's raw relation caps did not saturate in either case. Every relation,
  one-based rank, and squared distance matches within 1e-6.

The synthetic case is not a paper dataset. HappyBuddha res4 is a public-source
representative derivative, not the paper's 4.6M-point Buddha input bytes and
not Figure 14 reproduction. Home-Linux GTX 1070 timings remain diagnostics;
author and RTDL phase denominators are not converted into a ratio.

Goal5536 adds two controls without upgrading the paper claim. Replaying the
same HappyBuddha query on one prepared index with cap64 and cap128 produces the
same 228,892 raw-row hash and the same 28,432 canonical rows; the measured
maximum is 62 rows/query, so the cap64 result is not truncated. On those same
221,784 eligible rows, the generic global-lexsort `numpy_group_topk` is
output-identical to the removed per-group-mask algorithm and measures about
`0.053s` versus `0.509s` (about `9.55x`) on the GTX 1070. This is an RTDL
algorithm diagnostic. The repeated relation calls reuse one prepared index and
must not be described as fresh, query-many, author parity, or paper performance.

Goals5537-5538 then isolate and remove the dominant **generic fresh-prepare**
floor without changing the RTNN relation contract. Goal5537 shows that roughly
`1.83s` is first-use runtime `nvcc -cubin` compilation/module setup rather than
input-size or OptiX GAS construction. Goal5538 restores the app-neutral V3
cross-process CUBIN-cache capability with a new build/toolchain/driver-scoped
namespace, secure publication, and a CUBIN metadata/content-digest sidecar.
Across 12 fresh child processes on the home-Linux GTX 1070, prepare medians are
about `1.923s` on miss, `0.0687s` on hit, and `1.900s` with caching disabled
(`28.01x` miss/hit). Every mode preserves the complete Goal5536 raw/canonical
relation hashes; same-size ELF-looking arbitrary corruption is rejected and
rebuilt. This is a generic RTDL prepare diagnostic, not an end-to-end KNN,
author, or paper speedup.

Goal5539 confirms that the prepare win survives the full fresh route. One
fresh cache-prime process is excluded; five fresh cache-hit processes and three
fresh cache-disabled controls each reload inputs, rebuild the input-specific
index, regenerate 228,892 raw rows, rank 28,432 canonical rows, and recheck the
independent reference and author rows. Cache-hit versus disabled medians are
`1.887s` versus `3.737s` for the child-measured route (`1.98x`) and `2.099s`
versus `3.964s` for process wall (`1.89x`). Raw validation and author/reference
comparison are gate work and remain visible; no unmeasured production number is
derived by subtracting them.

Goal5540 then compares the legacy Python-dict row route with the existing
generic raw-row borrowed NumPy-column interface. Across five fresh processes
per mode, measured total improves from about `1.614s` to `1.343s` (`1.20x`)
and process wall from `1.810s` to `1.542s` (`1.17x`), with all raw/canonical
hashes preserved. Native row download is only about `2ms`; the removed floor is
Python dict/object materialization. This is host-column reuse, not device
residency or GPU zero-copy.

Goal5541 promotes that measured route into every RTNN exact-KNN hardware gate.
The bounded and representative gates now call `run_exact_raw()`, borrow NumPy
columns with `copy=False`, complete app-owned exact-zero filtering and generic
grouped top-K before closing the row owner, and materialize only final canonical
rows. A real HappyBuddha rerun preserves 228,892 raw rows, 221,784 eligible
rows, 28,432 final rows, the established canonical hash, and complete
reference/author equality. After one explicitly excluded secure-cache prime,
the measured route phases are about `0.0691s` prepare, `0.00293s` relation,
`0.1418s` filter/top-K, and `0.2151s` route total on GTX 1070. Goal5540 remains
the controlled speedup evidence; Goal5541 is the production-route promotion
and correctness gate.

Goal5542 recovers the paper's experiment ledger from the hash-pinned official
arXiv source archive. An app-owned Igor Pro extractor records all 32
`char.pxp` and 48 `results.pxp` waves, including values, labels, units, shapes,
and scales. Empirical Figures 5-8 and 11-16 now have an explicit wave map. In particular,
Figure 13 contains the five NoOpt/Sched/Partition/Bundle/Oracle variants for
both KITTI-12M and NBody-9M, and Figure 14 exposes exact Buddha-4.6M `r` and
`K` sweep axes. Figure 12 correctly uses `textWave1` categories and stores
already-normalized fractions; Figure 16 preserves a raw twelfth point clipped
by the final graph. This is source-ledger evidence only: final Igor graph
scaling/annotations are not fully extracted, the PDFs have not been numerically
reconstructed, exact input bytes are not recovered, and no Figure or
performance result is claimed.

Goal5543 adds a bounded original-ID mechanism discriminator without promoting
paper semantics into RTDL core. One 48-point/12-query exact-KNN fixture is run
through the pinned author in four configurations: NoOpt, Scheduling, Partition
without bundling, and Bundle. All four emit the same 33 canonical original-ID
neighbor rows and match the independent reference exactly. The gate also proves
that it exercised different behavior: Scheduling changes the query order from
identity to `[7,5,1,0,4,8,11,2,6,10,9,3]`; unbundled Partition has five batches
with two nonempty batches, while Bundle collapses them to one nonempty batch.
The author patch is output-only and fail-closed, and a clean pinned checkout is
required before patching. This is bounded exact mechanism correctness only.
It is not Figure 13, not Oracle, not approximate KNN, not a performance result,
and the fixture-owned `cr=8` discriminator is not an exact paper configuration.

Goal5544 then audits all nine official PXP workload labels before spending a
POD on paper-scale work. Exact input bytes, hashes, and complete construction
contracts are recovered for `0/9` workloads. The audit does pin strong
same-source candidates: Home Linux has 51,025,185 KITTI points across 422 raw
frames; the workspace has the 3,609,600-vertex Stanford Asian Dragon; current
official Bunny and HappyBuddha scan archives total 362,272 and 4,586,124
points. None supplies the missing paper frame/scan selection, transforms,
ordering, serialization, or query construction. Historical Goal4499 KITTI
recipes remain explicitly Level-B (`bounded_family_recipe_not_exact_paper_recipe`).
This is a provenance decision, not a GPU, Figure, or performance result.

Goal5545 crosses the next preparation boundary without weakening that claim.
It replays the historical Goal4499 99-frame recipe into a streamed 12,000,000-
row XYZ file, selects 4,096 deterministic source-row queries, hashes every
source frame and generated file, and packages the 393 MB input as a 104 MB
transfer archive. The exact generated author/RTDL bytes are now ready. The
packet remains Level-B same-source evidence because the paper frame/query
recipe is unavailable; K=4, radius 2.0, approximation-off and the bounded query
subset are Goal5545 comparator settings, not Figure-13 settings. The next gate
is the first point where a GPU POD is required.

Goal5546 executes that gate on one RTX 2000 Ada POD. The pinned author and RTDL
consume the same generated 12,000,000-search/4,096-query files and each emit
16,382 canonical K=4 rows. RTDL completely enumerates 646,391,723 open-radius
relations with no cap-saturated query before applying the app-owned zero-row
rule and generic `numpy_group_topk`.

Strict raw neighbor IDs do not match: 101 relations differ and 12 ranks move.
Every difference is nevertheless inside an exact tie under the author's
float32 squared-distance expression. The accepted comparator stays strict on
query, rank, multiplicity, and distance, and permits an alternate ID only when
both candidates have the exact same float32 score bits. It records 113 tie
substitutions: 104 have bit-identical coordinates and 9 have distinct
coordinates with an exact equal float32 score. Semantic mismatches are zero;
raw-ID equality remains explicitly false. This is Level-B same-source,
same-generated-byte exact-KNN relation evidence, not exact paper input,
Figure 13, approximate KNN, algorithm equivalence, or performance evidence.

Goal5547 removes the RTDL scaling failure exposed by that gate without adding
an RTNN primitive. It extends the existing prepared uniform-cell ranked-row
path with a generic lower/upper distance window, independent open/closed
boundaries, and one-pass native top-K output bounded by `query_count * K`. A
facility-service-radius test proves non-RTNN reuse. On the unchanged 12M-search/
4,096-query packet it emits the same 16,382 semantic rows, preserves strict raw
ID equality as false, and reduces the RTDL query phase from Goal5546's
632.073711s relation plus 151.344119s ranking to a stable 2.244261s median
(about 349.08x RTDL old-route versus new-route). Materialized rows fall by about
39,457x. These are same-POD RTDL system numbers, not author or paper speedups;
the route does not claim candidate-pruned traversal, exact paper inputs,
Figure 13, approximate-KNN correctness, or full paper reproduction.

Goal5548 executes the pinned author's default approximation mode 2 on exactly
the same 12M-search/4,096-query bytes. The author command intentionally omits
`-a`: the pinned parser casts an explicit value to `bool`, so `-a 2` selects
mode 1 rather than the source default mode 2. Output-only instrumentation
supports all six query batches and disables point sorting so raw input IDs stay
observable. Consequently this is not a paper-default point-sort configuration.

Against Goal5547's exact result, all 16,382 approximate rows have the same
per-query float32 squared-distance score multiset: score recall@K is `1.0` for
all 4,096 queries and the maximum kth-distance-squared ratio is `1.0`. Raw-ID
recall is `0.994262`; 94 queries select a different ID only inside an exact
score tie. This is a quality characterization for one Level-B workload, not a
general approximation result and not an RTDL reproduction of the author's
approximation algorithm.

Goal5549 closes the externally approved line at scoped exact correctness plus
generic system extraction. It does not upgrade the
paper claim: exact workload provenance remains `0/9`, no Figure or Oracle is
reproduced, and no author-performance ratio is authorized.

The bounded correctness gates are:

```text
one bounded XYZ point/query fixture
-> pinned author optixNSearch with exact range-search settings
-> app-owned output-only instrumentation emits canonical per-query neighbors
-> RTDL public fixed-radius route emits canonical per-query neighbors
-> compare query id, neighbor id, count, and distance/predicate policy
```

Timing, aggregate checksums, and total-neighbor counts are not substitutes for
this relation-level gate.

```text
one bounded exact-KNN XYZ point/query fixture
-> pinned author optixNSearch compiled with K=4 and approximation disabled
-> app-owned output-only instrumentation emits canonical ranked rows
-> RTDL exact open-radius rows
-> app-owned zero-distance exclusion
-> generic grouped top-K reduction
-> compare complete query id, neighbor id, rank, and squared-distance rows
```

## Prior RTNN Work Is Not Paper Reproduction

RTDL already contains a substantial RTNN-shaped benchmark campaign:

- `examples/current/research_benchmarks/rtnn/`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `src/rtdsl/rtnn_reproduction.py`
- `src/rtdsl/rtnn_manifests.py`
- archived Goals2346-2391 author/RTDL/CuPy evidence

Those assets established author build compatibility, deterministic synthetic
inputs, prepared fixed-radius execution, ranked summaries, batching, and
diagnostic timing. They were explicitly bounded as benchmarks. This paper app
reuses them as engineering assets and historical evidence; it does **not**
reclassify them as RTNN paper reproduction.

## RTDL Program

Existing public RTDL APIs expected to participate include:

- `prepare_optix_fixed_radius_neighbors_3d`
- `prepare_embree_fixed_radius_neighbors_3d`
- `execute_ranked_summary_typed_stream_partner_columns`
- `DeviceColumnBuffer`
- `PreparedGeometrySession`

The first paper gate uses the OptiX exact fixed-radius path. RTDL now exposes an
app-neutral `radius_boundary="closed"|"open"` policy on exact prepared rows;
the default remains closed and the legacy native ABI remains valid. Embree is a
portable system cross-check, not an author-performance denominator.

The bounded exact-KNN route composes that generic open-radius row producer with
the existing generic `rt.numpy_group_topk` reduction. The app owns RTNN's
zero-distance exclusion and the canonical rank comparator. No KNN-specific
native primitive was added for this gate.

Goal5534 also removes a real system scaling defect: `numpy_group_topk` now uses
one global `(group, score, item)` lexicographic ordering followed by vectorized
within-group ranks, instead of rescanning the complete candidate table once
per group. This is a generic grouped-reduction improvement and is regression-
checked against a naive reference outside RTNN-specific code.

Goal5536 measures that generic change against the removed implementation on
the same representative row table. Fresh prepare remains about `1.92s`, while
prepared same-input relation replay is about `0.18-0.19s` and new host top-K is
about `0.053s`. Prepare-phase decomposition, not an assumed device-column
rewrite, was therefore the next system gate. Goal5537 identifies first-use
runtime CUBIN compilation as that floor, and Goal5538 removes it across fresh
processes through the generic hardened cache. Goal5539 now measures that whole
cache-hit fresh route. Its next-gate result is to decompose exact-row
materialization and the combined app-zero-filter/generic-group-topK host phase
before any device-column/native ordering ABI is authorized.

## App-Owned Code

RTNN-specific responsibilities remain in this paper app:

- pinned author checkout and CUDA-version compatibility patching;
- output-only author instrumentation for canonical neighbor rows;
- author CLI option mapping, including exact/approximate KNN policy;
- input provenance, fixtures, paper workload and dataset selection;
- canonical row ordering, comparator, float predicate, and tolerance;
- author/RTDL phase labels and performance-denominator decisions.

RTDL core owns only generic prepared geometry, fixed-radius neighbor rows,
ranked summaries, column buffers, partner continuations, and session lifetime.
No `rtnn`, paper, author, query-partitioning, or RTNN-specific approximation
primitive is authorized in core by this scaffold.

## Reproduction Scope

Externally reviewed evidence levels are:

1. exact fixed-radius bounded same-input canonical-row equality - approved;
2. bounded exact KNN equality, with approximation disabled - approved;
3. representative synthetic and public same-source workload relation coverage
   - approved;
4. bounded original-ID NoOpt/Scheduling/Partition/Bundle exact-relation gate -
   approved;
5. exact-input provenance matrix - approved, with 0/9 exact;
6. Level-B KITTI-12M same-bytes packet - approved;
7. Level-B KITTI-12M complete exact-KNN tie-equivalent relation gate -
   approved;
8. author default approximation-mode-2 quality characterization on those same
   bytes - approved, score recall@K `1.0` on this workload, and no RTDL
   approximation-algorithm claim;
9. scoped exact-correctness and generic-system-extraction closeout -
   externally reviewed and approved;
10. paper dataset/figure/performance work only after input and denominator
   provenance are established.

Approximate KNN is a separate semantic contract. It cannot be used to satisfy
an exact-neighbor correctness gate.

## Performance Scope

There is no author or paper-app performance claim. Goal5547 provides a
same-POD RTDL old-route/new-route diagnostic (`783.417830s -> 2.244261s`
query median, about `349.08x`) and must remain labeled as such. Future matrices
must
separate:

- author build and process startup;
- author data loading and query partition/sort preparation;
- author search kernel/internal time;
- RTDL runtime initialization and prepare/setup;
- RTDL query route and canonical output materialization;
- cold process, warm long-lived process, and prepared replay.

No ratio is allowed unless input, operation, output contract, hardware, phase
boundary, and runtime regime align.

## Boundary

Not claimed:

- RTNN paper reproduction;
- exact paper dataset or figure reproduction;
- author query-scheduling or query-partitioning algorithm equivalence;
- Figure 13 or Oracle reproduction from the bounded mechanism gate;
- exact paper-input or paper-scale exact/approximate KNN reproduction;
- whole-program speedup or author-performance parity;
- native backend completion;
- correctness from timing, aggregate counts, or checksums alone.
