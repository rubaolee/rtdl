# RT-DBSCAN Review Opinions Register

Date: 2026-07-07

This register tracks review status for the RT-DBSCAN paper-app bounded line.
It does not convert bounded same-input gates into full RT-DBSCAN paper
reproduction.

## Status Table

| Goal | Subject | Status | Notes |
| --- | --- | --- | --- |
| Goal5089 | Paper-app scaffold | internal report complete | scaffold only; no reproduction claim |
| Goal5090 | Requirements audit / first target | internal report complete | selected fixed-radius core-count as first bounded target |
| Goal5091 | AuthorOfficial build/run plan | internal report complete | build plan only |
| Goal5092 | AuthorOfficial core-count gate packet | internal report complete | patch and runner packet; POD execution deferred to Goal5093 |
| Goal5093 | AuthorOfficial core-count POD execution | evidence complete; consolidated review pending | live POD AuthorOfficial and RTDL OptiX both report `core_count=7`, `matched=true` |
| Goal5094 | AuthorOfficial component signature / first component gate | superseded by amended partition gate for claims | original signature-only evidence on tiny fixture; now the runner and POD summaries use partition-gate v2 |
| Goal5095 | Border/noise component partition gate | externally reviewed and approved | `review_goal5095_amended_component_partition_gate_verified_2026-07-07.md` approved the amendment |
| Goal5096 | Bounded-line closeout | prepared; consolidated review pending | closes only bounded same-input core-count and component-partition gates |
| Goal5097 | Performance regime / runner contract | externally reviewed and approved | approved by `review_goals5097_5103_rt_dbscan_representative_partition_packet_verified_2026-07-07.md`; defines cold process, warm long-lived process, author-reported phase, and author process-wall regimes |
| Goal5098 | Representative synthetic fixtures | externally reviewed and approved | approved in the Goals5097-5103 packet; adds three controlled synthetic fixtures and manifest, not paper datasets |
| Goal5099 | Representative AuthorOfficial partition gate | externally reviewed and approved | approved in the Goals5097-5103 packet; all three representative fixtures match canonical partition, core flags, and signature on POD |
| Goal5100 | Fair performance matrix | externally reviewed and approved | approved in the Goals5097-5103 packet; cold one-shot unfavorable to RTDL, warm process diagnostic only, no public speedup claim |
| Goal5101 | Generic component-partition helper extraction | externally reviewed and approved | approved in the Goals5097-5103 packet; adds reusable `rtdsl` helpers for canonical partitions and signatures |
| Goal5102 | Bottleneck analysis | externally reviewed and approved | approved in the Goals5097-5103 packet; identifies cold setup/compilation as the small-fixture bottleneck |
| Goal5103 | Consolidated packet | externally reviewed and approved | verdict `approve_goals5097_5103_rt_dbscan_representative_partition_and_performance_boundary_packet` |
| Goal5104 | Author warm-loop comparison | internal report complete; review pending | patched AuthorOfficial repeat loop shows RTDL steady medians remain below author inner-loop medians on synthetic representatives |
| Goal5105 | Exact paper dataset provenance audit | internal report complete; review pending | identifies paper dataset candidates and author-local filename hints; exact preprocessed paper inputs remain unpinned |
| Goal5106 | UCI 3DRoad same-source candidate | internal report complete; review pending | public UCI 3DRoad source pinned and transformed; 1K author payload diverges from CPU partition and author teardown segfaults, so not a clean exact gate |
| Goal5107 | UCI 3DRoad author contract analysis / teardown patch | internal report complete; review pending | explains the 1K mismatch as author directional border assignment (`xID > primID`); conventional mismatch=12, author-directional mismatch=0; clean 1K and 16K author outputs produced with comparator-only teardown skip |
| Goal5108 | UCI 3DRoad author-directional app comparator gate / PTX blocker narrowing | internal report complete; review pending | adds app-owned `author_directional_cpu_reference` backend; 1K clean AuthorOfficial payload matches exactly; RTDL OptiX+Numba remains blocked by POD PTX 8.7 vs 8.4 toolchain mismatch |
| Goal5109 | UCI 3DRoad RTDL OptiX+CuPy semantic-gap run | internal report complete; review pending | CuPy route avoids the Numba PTX blocker and runs generic RTDL OptiX grouped-stream labels on 1K, but matches the conventional signature `[102,168,181]/549`, not AuthorOfficial directional `[90,168,181]/561`; core flags match |

## Carry-Forward Boundaries

- Full RT-DBSCAN paper reproduction: not closed.
- Exact paper dataset reproduction: not closed.
- Exact author label-ID parity: not claimed.
- Full DBSCAN output-format parity: not claimed.
- Performance or speedup: not claimed.
- Warm-process representative timing: diagnostic only, not a public paper speedup claim.
- RT-DBSCAN-specific RTDL core primitive: not added.
- Paper dataset provenance: candidates recorded, but exact author-preprocessed inputs not acquired.
- UCI 3DRoad same-source candidate: source and transform pinned, author directional border contract diagnosed and app-side comparator gate added, but RTDL OptiX/Numba 3DRoad correctness gate not closed.
- UCI 3DRoad RTDL OptiX+CuPy execution: runs on POD, but does not match the author-directional border-assignment contract; this is a semantic-contract gap, not a paper reproduction success.
- Owner decision after Goal5109: do not open a new RT-DBSCAN author-directional SoS / border-assignment route. RTDL SoS and degeneracy protocols are fixed from the RayJoin line; `xID > primID` remains a pinned-author implementation detail, not a new RTDL language contract.

## Current Strongest Evidence

Core-count gate:

```text
author.core_count=7
rtdl.core_count=7
matched=true
```

Component-partition gates:

```text
tiny canonical partition=[0,0,0,0,1,1,1,-1]
border/noise canonical partition=[0,0,0,0,0,0,1,1,1,1,1,-1]
signature_matched=true
component_partition_matched=true
core_flags_matched=true
matched=true
```

The component gate uses canonical point partitions modulo component-label
renaming. This fixes the prior signature-only blind spot for border-point
misassignment.

Representative synthetic matrix:

```text
representative_medium_two_clusters3d: core=96, sizes=[48,48], noise=4, matched=true
representative_border_shell3d: core=54, sizes=[29,29], noise=2, matched=true
representative_three_components_noise3d: core=61, sizes=[16,18,27], noise=3, matched=true
```

Timing boundary:

```text
cold one-shot RTDL: 1.61s to 1.72s, slower than author reported phase total
warm in-process RTDL median: 0.0041s to 0.0057s, diagnostic only
author warm-loop inner median: 0.0158s to 0.0406s on the representative fixtures
RTDL / author warm inner-loop: 0.097x to 0.237x, diagnostic only
```

UCI 3DRoad same-source contract analysis:

```text
point_count=1000, epsilon=0.05, minPts=100
author_signature={core_count=329, component_sizes=[90,168,181], noise_count=561}
conventional_signature={core_count=329, component_sizes=[102,168,181], noise_count=549}
conventional_mismatch_count=12
author_directional_mismatch_count=0
runner_backend=author_directional_cpu_reference
runner_matched=true
```

The 12 conventional-reference-only border points have lower-index core
neighbors and no higher-index core neighbors. This matches the author's call-2
directional attachment rule and supersedes the Goal5106 "unexplained mismatch"
classification. Goal5108 turns this into an app-owned runner backend. It does
not close exact paper input reproduction or RTDL OptiX/Numba correctness on
3DRoad.

Current 3DRoad RTDL blocker:

```text
Numba emits PTX 8.7
current CUDA driver/linker path accepts PTX 8.4
minimal Numba CUDA kernel fails with CUDA_ERROR_UNSUPPORTED_PTX_VERSION
```

UCI 3DRoad RTDL OptiX+CuPy semantic-gap run:

```text
backend=optix_cupy_component_signature
matched=false
signature_matched=false
component_partition_matched=false
core_flags_matched=true
rtdl_signature={core_count=329, component_sizes=[102,168,181], noise_count=549}
author_signature={core_count=329, component_sizes=[90,168,181], noise_count=561}
```

This result confirms that the existing generic RTDL grouped-stream component
pipeline behaves like the conventional DBSCAN partition on the 1K UCI 3DRoad
candidate. It does not reproduce the pinned author's index-directional border
attachment rule.

The project will not change RTDL SoS/border semantics to chase this
AuthorOfficial-specific behavior.
