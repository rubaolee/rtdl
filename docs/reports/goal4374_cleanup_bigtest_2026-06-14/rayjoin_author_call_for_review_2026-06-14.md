# Call For Review: RayJoin Author Feedback Request

Date: 2026-06-14

Audience: RayJoin authors / maintainers

Purpose: ask the RayJoin authors to review our reproduction contract, timing interpretation, and public wording before we publish RTDL-vs-RayJoin statements.

## Short Sendable Email

Subject: Request for review: RayJoin overlay reproduction and RTDL comparison wording

Dear RayJoin authors,

We have been implementing a RayJoin benchmark app in RTDL, with two backend routes: RTDL OptiX on NVIDIA RT cores and RTDL Embree on CPU. Before we publish any performance wording, we would very much appreciate your review of our benchmark contract and interpretation.

Our final staged County x Zipcode overlay result is:

| Implementation | Timing Basis | Overlay Total Wall Time |
|---|---|---:|
| RTDL OptiX / NVIDIA RT cores | warm packed-array cache, warmup=1, repeat=3 median | 5.805 s |
| Your RayJoin RT process run | cold single full-process run in our packet | 7.149 s |
| RTDL Embree / CPU | warm packed-array cache, warmup=1, repeat=3 median | 9.901 s |

We do not want to overclaim. In particular, we are not claiming that RTDL beats RayJoin in every timing view, and we are not treating your bare query timings as directly comparable to our full app-level timings. The timing bases also differ: the RTDL rows above are warm-cache repeated medians, while the author row is one cold full-process command run that includes read/init/build/query/cleanup. We therefore treat the table as a total-wall-time comparison for review, not as a claim that RTDL computes overlay faster than RayJoin.

The main things we would like you to review are:

1. Whether our interpretation of the RayJoin overlay app contract is correct.
2. Whether our treatment of author process wall time versus author-reported query phase is fair.
3. Whether the standalone LSI count difference we observed should be described as a different query/contract rather than a correctness mismatch.
4. Whether our understanding of PIP timing and device-resident data assumptions is correct.
5. Whether boundary-tie behavior in the author implementation is expected to be nondeterministic or input-order sensitive.
6. Whether the public wording below is acceptable or should be revised.

We are happy to update the wording, rerun commands, or add clarifying caveats before publication.

Thank you for releasing RayJoin and for making this comparison possible.

Best,

[Your name / RTDL team]

## Full Review Packet

Dear RayJoin authors,

We are building RTDL, a general ray-tracing-oriented data/runtime system. As part of our benchmark suite, we implemented a RayJoin benchmark app with three program shapes:

- LSI
- PIP
- Polygon overlay

Our goal is not to rewrite your system by hand in C++/CUDA. Our goal is to express the app through RTDL primitives plus Python/partner orchestration, then compare:

- Your RayJoin RT implementation
- RTDL OptiX on NVIDIA RT cores
- RTDL Embree on CPU cores

We are requesting your review before we publish the comparison.

## Dataset And Scope

The result below uses our staged County x Zipcode CDB dataset:

| Input | Chains | Segments | Points | Nonzero Faces |
|---|---:|---:|---:|---:|
| `dtl_cnty_Point.cdb` | 8,662,896 | 8,662,896 | 17,325,792 | 3,144 |
| `USAZIPCodeArea_Point.cdb` | 9,503 | 5,279,181 | 5,288,684 | 4,500 |

Important scope note:

This is a staged/same-source regenerated County x Zipcode packet, not a claim that we have recovered every exact preprocessed dataset from the paper. We currently treat the staged packet as suitable for this focused review of the County x Zipcode app behavior.

## Final Performance Matrix

| Program | Timing View | RayJoin Author RT | RTDL OptiX / RT cores | RTDL Embree / CPU |
|---|---|---:|---:|---:|
| LSI | process / hot median | 17.110517 s | 2.520978 s | 5.892485 s |
| LSI | author query / native median | 0.004386 s | 0.002023 s | n/a |
| PIP | process / hot median | 16.256993 s | 0.277429 s host-points; 0.118584 s device-resident | 0.303879 s |
| PIP | author query / native median | 0.007200 s | 0.118549 s device-resident | 0.303813 s |
| Overlay | cold process / warm-cache median | 7.149181 s | 5.804978 s | 9.900761 s |
| Overlay | load/pack | included | 0.050966 s | 0.040058 s |
| Overlay | compute without load/pack | included | 5.754012 s | 9.860703 s |

Timing note: the author process rows are cold full-process command wall times unless marked as author-reported query phases. The RTDL rows are warm-cache medians under the listed warmup/repeat protocols.

## Count And Contract Matrix

| Program | RayJoin Author Count | RTDL OptiX Count | RTDL Embree Count | Current Interpretation |
|---|---:|---:|---:|---|
| LSI standalone | 180,506 | 181,629 | 181,629 | We think the author standalone query path and our overlay-contract LSI path are not the same count contract. We do not want to report this as a correctness mismatch without your review. |
| PIP | not directly emitted in our author result packet | 3,823,783 positive faces | 3,823,783 positive faces | RTDL OptiX and Embree are count-consistent for the measured all-query-points PIP contract. |
| Overlay LSI | author overlay path did not directly emit a final comparable count in our clean result structure | 181,629 | 181,629 | RTDL OptiX and Embree use the same overlay LSI contract and match each other. |

## What We Optimized In RTDL Before Comparing

We initially had much worse RTDL overlay results. We treated those results as invalid for publication because they still included avoidable RTDL overhead. Before making the final comparison, we removed the following overhead:

- Repeated CDB text parsing and packing via packed-array partner cache.
- Full PIP row materialization in no-output overlay mode.
- Repeated point-location prepare handles for vertex and midpoint PIP.
- Python object midpoint sorting/materialization for no-output overlay.
- OptiX LSI TSV pair dumps and `np.loadtxt`, replaced by binary `uint64` pair output.
- Missing overlay warmup/repeat median support in the RTDL runner.
- Missing timing separation for point-location prepare/build-index time.
- Embree AABB scene build-quality tuning for the RayJoin LSI overlay path. We treat this as a benchmark-path configuration for this collide-heavy workload; build quality changes construction/traversal tradeoffs, not the result set.

This is why our final comparison is much faster than the earlier RTDL warm-cache baseline.

## Final Overlay Timing Breakdown

| Backend | Total Median | Load/Pack | Compute Without Load/Pack | LSI Hot | Point-Location Prepare Wall | PIP Hot Sum | Midpoint Projection |
|---|---:|---:|---:|---:|---:|---:|---:|
| RTDL OptiX | 5.804978 s | 0.050966 s | 5.754012 s | 2.438230 s | 1.325645 s | 1.420532 s | 0.099911 s |
| RTDL Embree | 9.900761 s | 0.040058 s | 9.860703 s | 4.977931 s | 3.310194 s | 1.147167 s | 0.066300 s |

For Embree, the measured `rtcCollide` traversal inside LSI is about 0.82 s in the final runs, while the LSI hot time is about 4.98 s. We interpret the difference as native scene/index construction, row production, and related non-traversal work.

## Specific Questions For You

### 1. Overlay App Contract

Our overlay implementation performs:

- LSI between the two maps
- vertex point-location from map0 into map1
- vertex point-location from map1 into map0
- midpoint point-location between consecutive intersections

Question:

Is this the correct high-level contract for comparing to your polygon overlay program when output-chain file writing is not requested?

### 2. Standalone LSI Count Difference

We observed:

- Author standalone LSI query result: 180,506 intersections
- RTDL overlay-contract LSI route: 181,629 intersections
- RTDL OptiX and RTDL Embree agree with each other at 181,629

Our current interpretation is that the author standalone LSI query path and the overlay LSI path are not identical count contracts.

Question:

Is this the right way to describe it, or should we investigate a specific semantic mismatch?

### 3. PIP Timing And Device Residency

Your PIP author query timing is extremely small, about 0.0072 s in our captured run. RTDL's fastest device-resident OptiX count route is about 0.1186 s.

Question:

Does your PIP query timing assume that CDB/index/query data are already resident on the GPU/device, with preprocessing and transfer excluded? If yes, we will explicitly state that your author query timing is not the same timing view as an end-to-end RTDL app call.

### 4. Overlay Timing View

For overlay, the author process wall time in our packet is about 7.149 s as one cold full-process command run. The author-reported internal phases include very small "Intersection edges" and "Computer output polygons" timings, but the process wall time includes read/init/build/cleanup work.

Question:

For public comparison, would you prefer that we report process wall time as the primary full-app author number, with author phase timings listed separately?

### 5. Boundary Ties / Nondeterminism

During our analysis we observed boundary-tie sensitivity in the author path, especially around map0 boundary cases. Our current plan is to describe this conservatively as boundary-tie behavior that may be input-order or tie-break sensitive, and not as a correctness bug.

Question:

Is boundary-tie nondeterminism or sensitivity expected in RayJoin for points/rays exactly on CDB boundaries? If so, how would you recommend reporting it?

### 6. Public Wording

We propose this public wording:

> On the staged County x Zipcode RayJoin overlay workload, RTDL's optimized OptiX route completes the full overlay app path in 5.80 s median total wall time, measured with a warm packed-array input cache (warmup=1, repeat=3). For reference, a cold full-process run of the author's RayJoin RT implementation, which reads, builds, queries, and tears down on every invocation, measured 7.15 s, and RTDL's Embree CPU route measured 9.90 s on the same warm-cache basis as RTDL OptiX. These are total-wall-time figures on different timing bases: the RTDL numbers amortize ingestion and acceleration-structure build across repeated runs and report load/pack separately (0.05 s), whereas the author figure includes cold read and build each run. We therefore do not claim RTDL computes the overlay faster than the author implementation; the author's overlay-compute phases are not separately isolated in our packet. The RTDL result reflects app-level LSI, vertex point-location, and midpoint point-location phases, achieved by removing avoidable RTDL overhead (repeated CDB parsing, full PIP row materialization, text pair dumps) while keeping the user-facing implementation in RTDL/Python plus partner-cache logic, with no user-written C++/CUDA.

Question:

Is this wording fair to RayJoin? If not, what should we change?

## What We Will Not Claim Without Your Review

We will not claim:

- RTDL beats RayJoin in every timing view.
- RTDL computes overlay faster than RayJoin from the available timing packet.
- That `5.80 s` versus `7.15 s` is a clean same-protocol compute comparison; the RTDL number is a warm-cache repeated median, while the author number is a cold single full-process run.
- RTDL's standalone LSI count and author standalone LSI count are directly comparable without caveat.
- Author query phase timing and RTDL full app-level timing mean the same thing.
- Boundary-tie differences are author bugs.
- We have completed all exact paper datasets beyond the staged County x Zipcode packet.

## Evidence Files We Can Share

Primary final files:

- `rayjoin_app_closeout_report_2026-06-14.md`
- `cleanup_bigtest_summary.md`
- `author_vs_rtdl_p0_final_default_low_summary_20260614.md`
- `author_vs_rtdl_p0_final_default_low_summary_20260614.json`
- `p0_final_overlay_county_zipcode_all_w1r3_default_low_20260614.json`

Supporting files:

- `cleanup_bigtest_lsi_county_zipcode_all_fixedroute_w1r3_20260614.json`
- `cleanup_bigtest_pip_county_zipcode_all_w5r60_20260614.json`
- `partner_cache_overlay_county_zipcode_all_warm_w0r1_20260614.json`
- `p0_binary_lsi_numpy_overlay_county_zipcode_all_warm_w0r1_20260614.json`
- `p0_backend_aware_prepare_overlay_county_zipcode_all_warm_w0r1_20260614.json`
- `p0_embree_aabb_quality_low_overlay_county_zipcode_w1r3_20260614.json`

## Requested Response

It would be extremely helpful if you could reply with:

1. Any correction to our benchmark contract.
2. Any correction to our interpretation of author timing fields.
3. Any correction to the LSI count-contract explanation.
4. Any guidance on boundary-tie behavior.
5. Whether the proposed public wording is acceptable.

If you prefer, we can also open a GitHub issue with the same content so the review is easier to discuss inline.
