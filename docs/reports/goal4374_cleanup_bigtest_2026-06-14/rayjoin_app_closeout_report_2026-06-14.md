# RayJoin Benchmark App Closeout Report

Date: 2026-06-14

## Closing Decision

Yes, we can close the RayJoin benchmark app work in its current scope.

The app now has a serious, reproducible, and professionally explainable comparison across:

- Author RayJoin RT code
- RTDL OptiX on NVIDIA RT cores
- RTDL Embree on CPU cores

The final overlay benchmark is no longer dominated by avoidable Python parsing, repeated packing, full PIP row materialization, TSV text dumps, or stale unoptimized Embree paths. The remaining costs are measured and explainable.

## Final Headline

For the staged County x Zipcode RayJoin overlay case:

| Implementation | Timing Basis | Total Wall Sec | Load/Pack Sec | RTDL Compute Without Load/Pack Sec | Relative To RTDL OptiX |
|---|---|---:|---:|---:|---:|
| RTDL OptiX / NVIDIA RT cores | warm packed-array cache, warmup=1, repeat=3 median | 5.804978 | 0.050966 | 5.754012 | 1.00x |
| Author RayJoin RT process | cold single full-process run; includes read/init/build/query/cleanup | 7.149181 | included | not separable in this packet | 1.23x higher wall time than RTDL OptiX warm-cache total |
| RTDL Embree / CPU cores | warm packed-array cache, warmup=1, repeat=3 median | 9.900761 | 0.040058 | 9.860703 | 1.71x slower |

Conclusion: RTDL OptiX is the fastest measured RTDL overlay backend in this final packet, and RTDL Embree is now just under 10 seconds. Against the author code, the supported claim is narrower: RTDL OptiX warm-cache total wall time is lower than one cold author full-process run. This is not a claim that RTDL computes overlay faster than the author implementation, because the author's overlay-compute phases are not isolated in the same timing view.

## Final Performance Matrix

| Program | Timing View | Author RayJoin RT | RTDL OptiX / RT cores | RTDL Embree / CPU |
|---|---|---:|---:|---:|
| LSI | process / hot median | 17.110517 | 2.520978 | 5.892485 |
| LSI | author query / native median | 0.004386 | 0.002023 | n/a |
| PIP | process / hot median | 16.256993 | 0.277429 host-points; 0.118584 device-resident | 0.303879 |
| PIP | author query / native median | 0.007200 | 0.118549 device-resident | 0.303813 |
| Overlay | end-to-end median | 7.149181 | 5.804978 | 9.900761 |
| Overlay | load/pack | included | 0.050966 | 0.040058 |
| Overlay | compute without load/pack | included | 5.754012 | 9.860703 |

Timing note: author process rows are cold full-process command wall times unless marked as author-reported query phases. RTDL hot/overlay rows are warm-cache medians with the listed warmup/repeat protocol.

## Count And Contract Matrix

| Program | Author Count | RTDL OptiX Count | RTDL Embree Count | Interpretation |
|---|---:|---:|---:|---|
| LSI standalone | 180,506 | 181,629 | 181,629 | Author standalone query path and RTDL overlay-contract LSI path are not the same count contract. Do not mix these as a direct correctness table. |
| PIP | not directly emitted in the author result packet | 3,823,783 positive faces | 3,823,783 positive faces | RTDL OptiX and Embree are count-consistent for the measured all-query-points PIP contract. |
| Overlay LSI | author overlay does not directly emit a final comparable count in the same clean result structure | 181,629 | 181,629 | RTDL OptiX and Embree use the same overlay LSI contract and match each other. |

## Speedup Summary

| Comparison | Ratio | Meaning |
|---|---:|---|
| RTDL OptiX overlay vs RTDL Embree overlay | 1.71x | RT cores are clearly faster than CPU/Embree for final overlay. |
| RTDL OptiX warm-cache overlay total vs cold author RayJoin process wall time | 1.23x lower wall time | RTDL OptiX warm-cache total is lower than one cold author process-level overlay run; not a compute-speed claim. |
| RTDL Embree warm-cache overlay total vs cold author RayJoin process wall time | 0.72x as fast | Embree is slower than the cold author process-level overlay run, but now just under 10 seconds. |
| RTDL OptiX overlay improvement from warm-cache baseline | 2.75x | P0 cleanup removed major materialization and text-dump costs. |
| RTDL Embree overlay improvement from warm-cache baseline | 1.84x | CPU path also benefited strongly from no-output/materialization cleanup and AABB scene tuning. |
| RTDL OptiX device-resident PIP vs RTDL Embree PIP | 2.56x | RT cores/device-resident route is much faster for PIP count. |
| RTDL OptiX LSI hot median vs RTDL Embree LSI hot median | 2.34x | RTDL OptiX LSI route remains much faster than Embree's current LSI row route. |

## What Was Optimized

The important work was not cosmetic. The initial overlay numbers were bad because the benchmark still contained avoidable RTDL-side overhead. Those costs were removed or isolated.

Completed optimizations:

- Added app-agnostic directed-segment point-location naming for OptiX and Embree.
- Kept legacy RayJoin CDB point-location symbols as compatibility fallbacks.
- Fixed standalone RTDL LSI to use the same RayJoin LSI row route as overlay.
- Added packed-array partner cache for CDB load/pack reuse.
- Added no-output overlay PIP fast path.
- Reused prepared point-location handles for vertex and midpoint PIP.
- Changed no-output PIP from full row materialization to count-only calls.
- Replaced Python object midpoint processing with NumPy midpoint projection from structured LSI rows.
- Replaced OptiX LSI TSV pair dumps with binary `uint64` pair output.
- Added overlay warmup/repeat median support to the runner.
- Added timing separation for load/pack, LSI, midpoint projection, point-location prepare, PIP hot calls, and native traversal where available.
- Used low-build-quality AABB scene construction for the RayJoin Embree LSI overlay path, preserving explicit user overrides. This is a benchmark-path configuration for this collide-heavy workload; build quality changes construction/traversal tradeoffs, not the result set.

## Why The Final Comparison Is Fair Enough To Close

The final comparison satisfies the intended benchmark contract:

- Same staged County x Zipcode CDB inputs.
- Same overlay app shape: LSI plus vertex PIP plus midpoint PIP.
- Same RTDL frontend principle for both hardware paths.
- Same RTDL app-level partner/cache policy for OptiX and Embree.
- Avoidable ingestion and materialization costs removed before making the performance claim.
- End-to-end and internal timing views separated.
- Author code kept as author code, not rewritten into RTDL.
- RTDL user path does not require app users to write C++ or CUDA.
- The author-vs-RTDL headline states its timing basis inline: warm-cache repeated RTDL medians versus a cold single author process run.

This makes the final overlay result suitable as the primary closeout comparison. External/public use must keep the timing-basis caveat next to the numbers.

## What "Partner" Means Here

The final RTDL implementation uses partner logic in the acceptable RTDL sense:

- A packed-array partner cache avoids repeated CDB text parsing and packing.
- NumPy is used for host-side projection/postprocess work where Python object loops were unnecessary.
- Native RTDL primitives provide OptiX and Embree acceleration.

This does not violate the RTDL architecture. The user-facing model remains:

1. General RTDL runtime and primitives.
2. App-level orchestration in Python.
3. Optional partner/cache logic for data preparation and postprocess.
4. No requirement that benchmark users write C++ or CUDA to get the optimized route.

## Why OptiX Wins

RTDL OptiX wins the final overlay comparison because the actual RT-heavy pieces now have a clean path:

- LSI hot median is 2.438230 seconds in the final overlay packet.
- Point-location prepare wall time is 1.325645 seconds.
- PIP hot calls sum to about 1.420532 seconds.
- Load/pack is only 0.050966 seconds.

After removing Python/TSV/materialization drag, RT cores show their advantage clearly over the RTDL Embree CPU backend. The final RTDL OptiX overlay result is 5.804978 seconds median on the warm-cache protocol.

## Why Embree Is Still Slower

Embree is now respectable, but its remaining cost is real and measured:

- Embree overlay total median is 9.900761 seconds.
- Embree LSI hot median is 4.977931 seconds.
- Embree LSI measured `rtcCollide` traversal is about 0.819 seconds in the final runs.
- The difference is scene/index construction, row production, and other native non-traversal work.
- Point-location prepare wall time contributes another 3.310194 seconds.

So the remaining gap is not unexplained Python overhead. It is CPU-side native scene/index and prepare cost. This is exactly the kind of cost one expects when comparing RT-core acceleration against CPU BVH construction/traversal for this workload.

## What Not To Overclaim

The public wording should be careful:

- Do not claim RTDL beats the author implementation on every timing view.
- Do not claim RTDL computes overlay faster than the author implementation. The author's overlay-compute phases are not separately isolated in our packet.
- Do not present `5.80 s` versus `7.15 s` without saying that RTDL is a warm-cache repeated median while the author number is a cold single full-process run.
- Do not compare author bare query timing directly to RTDL app-level timing without saying what each timing includes.
- Do not treat standalone LSI author count 180,506 and RTDL overlay-contract count 181,629 as a direct mismatch. They are different paths/contracts.
- Do not claim Embree is faster than RT cores for final overlay. It is not.
- Do not claim all 24 exact paper cases are complete. This staged dataset has 3 ready cases for County x Zipcode: LSI, PIP, and Overlay.

## Recommended Public Wording

Use this wording:

> On the staged County x Zipcode RayJoin overlay workload, RTDL's optimized OptiX route completes the full overlay app path in 5.80 s median total wall time, measured with a warm packed-array input cache (warmup=1, repeat=3). For reference, a cold full-process run of the author's RayJoin RT implementation, which reads, builds, queries, and tears down on every invocation, measured 7.15 s, and RTDL's Embree CPU route measured 9.90 s on the same warm-cache basis as RTDL OptiX. These are total-wall-time figures on different timing bases: the RTDL numbers amortize ingestion and acceleration-structure build across repeated runs and report load/pack separately (0.05 s), whereas the author figure includes cold read and build each run. We therefore do not claim RTDL computes the overlay faster than the author implementation; the author's overlay-compute phases are not separately isolated in our packet. The RTDL result reflects app-level LSI, vertex point-location, and midpoint point-location phases, achieved by removing avoidable RTDL overhead (repeated CDB parsing, full PIP row materialization, text pair dumps) while keeping the user-facing implementation in RTDL/Python plus partner-cache logic, with no user-written C++/CUDA.

Short version:

> RTDL now has a credible RayJoin overlay implementation on both RT cores and Embree CPU. On the RTDL warm-cache total-wall-time protocol, the RT-core path is fastest at 5.80 s median, with Embree at 9.90 s; a cold author RayJoin RT process run measured 7.15 s. Timing bases differ, so this is a total-wall-time comparison, not a claim about overlay-compute speed.

## Recommended Internal Wording

Use this wording inside planning and docs:

> RayJoin overlay can be closed for v2.12 app-level performance. Further work is native CPU polishing, not correctness or basic viability. The next CPU debt is Embree LSI/point-location prepare reuse or lower-cost scene/index build, but that is incremental optimization rather than a blocker.

## Remaining Debt After Close

This app can close with known follow-up items:

- Embree LSI still spends most of its time outside the measured `rtcCollide` traversal.
- Embree point-location prepare is still a multi-second wall-time contributor.
- Author-side variance and same-protocol repeats are not reported in this packet; quote the author comparison as one cold full-process run unless rerun.
- Author standalone LSI and RTDL overlay-contract LSI counts should not be merged into one correctness claim.
- Full exact paper reproduction for all 24 cases still depends on exact paper datasets beyond this staged County x Zipcode packet.

These are not blockers for closing the current app work.

## Evidence Files

Primary final files:

- `p0_final_overlay_county_zipcode_all_w1r3_default_low_20260614.json`
- `author_vs_rtdl_p0_final_default_low_summary_20260614.md`
- `author_vs_rtdl_p0_final_default_low_summary_20260614.json`
- `cleanup_bigtest_summary.md`

Supporting files:

- `cleanup_bigtest_lsi_county_zipcode_all_fixedroute_w1r3_20260614.json`
- `cleanup_bigtest_pip_county_zipcode_all_w5r60_20260614.json`
- `partner_cache_overlay_county_zipcode_all_warm_w0r1_20260614.json`
- `p0_binary_lsi_numpy_overlay_county_zipcode_all_warm_w0r1_20260614.json`
- `p0_backend_aware_prepare_overlay_county_zipcode_all_warm_w0r1_20260614.json`
- `p0_embree_aabb_quality_low_overlay_county_zipcode_w1r3_20260614.json`

## Validation

Validation completed:

- Local Python compile passed for the RayJoin overlay and benchmark scripts.
- Local unit tests passed: 21 tests.
- Pod Python compile passed.
- Pod unit tests passed: 21 tests.
- Pod OptiX build passed after binary LSI dump changes.
- Pod Embree backend was rebuilt/probed after AABB scene quality changes.
- Final pod RTDL overlay benchmark completed with `warmup=1, repeat=3`.
- Author overlay comparison in this packet is a cold single full-process run.

## Final Closeout

Close this app.

The remaining work is not "make RayJoin viable." That is done. The remaining work is optional native CPU polishing and broader exact-paper dataset expansion.
