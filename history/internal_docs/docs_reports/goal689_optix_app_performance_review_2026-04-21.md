# Goal689: OptiX App Performance Review

Date: 2026-04-21

Scope: review the current public app surface from the viewpoint of the new
performance priority: RTDL should make NVIDIA OptiX the first-class path for
users who want NVIDIA GPU and RT-core acceleration.

This is a performance-engineering review, not a release announcement. It
classifies where the current RTDL app paths are genuinely OptiX traversal
paths, where they are CUDA compute paths behind the OptiX backend, where they
are host-indexed fallbacks, and where Python/app-layer work dominates.

## Executive Verdict

OptiX should be RTDL's primary high-performance engine, but the current app
surface is not uniformly OptiX-optimized yet.

The main risk is semantic overloading: an app can expose `--backend optix`
without the dominant operation necessarily being NVIDIA RT-core traversal. In
the current codebase, OptiX app paths fall into four different categories:

| Category | Meaning | Performance implication |
| --- | --- | --- |
| OptiX traversal eligible | Uses OptiX ray traversal/custom primitives; eligible for RTX hardware acceleration on RTX-class GPUs | Best candidate for flagship RTDL speedups |
| CUDA-through-OptiX | Uses CUDA kernels compiled/loaded by the OptiX backend library, not RT traversal | GPU-accelerated, but not an RT-core claim |
| Host-indexed fallback | OptiX-facing API dispatches to CPU-side indexed code | Correctness path, not an OptiX performance path |
| Python/interface dominated | Native candidate rows are emitted, then Python packing, dict conversion, reduction, clustering, or JSON dominates | Need raw arrays, prepared datasets, and native reductions |

This distinction must be visible in every future OptiX performance review.

## Public App Classification

| App | Current OptiX exposure | Dominant current path | Performance review |
| --- | --- | --- | --- |
| `examples/rtdl_database_analytics_app.py` | Exposed | OptiX DB BVH candidate discovery plus CPU exact filtering/grouping and Python row conversion | Real RT traversal is present for candidate discovery. The bottlenecks are Python/ctypes preparation, candidate copy-back, CPU aggregation, and dict-row materialization. Prepared columnar datasets and native aggregate outputs are required before claiming high app-level performance. |
| `examples/rtdl_graph_analytics_app.py` | Exposed | Host-indexed graph routines behind OptiX API symbols | This is the largest honesty/performance gap. BFS and triangle OptiX app execution is correctness-useful, but not currently an RT-core acceleration story. It needs native GPU graph kernels or a downgraded app-level status. |
| `examples/rtdl_road_hazard_screening.py` | Exposed | Segment/polygon path defaults to host-indexed candidate reduction unless native mode is explicitly enabled | Correct app shape, weak default OptiX performance story. Native OptiX segment/polygon mode must become the default only after correctness and performance gates pass. |
| `examples/rtdl_segment_polygon_hitcount.py` | Exposed | Same segment/polygon host-indexed default risk | Same as road hazard. It should not be used as an RT-core flagship until native mode is default and measured. |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | Exposed | Same segment/polygon host-indexed default risk | Same as road hazard, plus row-volume risk when many pair rows are emitted. |
| `examples/rtdl_hausdorff_distance_app.py` | Exposed | KNN rows through CUDA-style OptiX backend path; Python max reduction | Good GPU-compute evidence exists on GTX 1070, but this is not RT-core evidence. Python reduction should be replaced by native max/argmax output for performance mode. |
| `examples/rtdl_ann_candidate_app.py` | Exposed | KNN rows through CUDA-style OptiX backend path; Python recall/metric computation | Useful GPU candidate-search app, but not an RT-core traversal claim. Optimize packing and return compact nearest rows or recall counters directly. |
| `examples/rtdl_outlier_detection_app.py` | Exposed | Fixed-radius rows through CUDA-style OptiX backend path; Python count/threshold logic | Current app is interface/output sensitive. For high performance, emit per-query neighbor counts directly instead of all neighbor rows when the app only needs density. |
| `examples/rtdl_dbscan_clustering_app.py` | Exposed | Fixed-radius rows through CUDA-style OptiX backend path; Python clustering expansion | Candidate generation can be GPU-accelerated, but full app speed is dominated by output volume and Python expansion. Needs a native neighbor-count/core-point pass and compact adjacency representation. |
| `examples/rtdl_robot_collision_screening_app.py` | Exposed | OptiX ray/triangle any-hit traversal, then Python `rt.reduce_rows(any)` | This is the best current OptiX flagship candidate. Any-hit traversal maps naturally to OptiX and early exit. The bottleneck is app-level row materialization and Python reduction; performance mode should return pose-level collision flags or scalar counts directly. |
| `examples/rtdl_barnes_hut_force_app.py` | Exposed | Candidate generation through KNN/radius-style backend path; Python tree/opening-rule/force reduction | RTDL can accelerate candidate discovery, but the app is not yet an end-to-end OptiX speedup story. It needs native reduction or an explicit "candidate-generation only" claim. |
| `examples/rtdl_apple_rt_demo_app.py` | Not applicable | Apple-specific | Not part of OptiX performance goal. |
| `examples/rtdl_hiprt_ray_triangle_hitcount.py` | Not exposed | HIPRT-specific | Not part of OptiX performance goal. |
| `examples/rtdl_service_coverage_gaps.py` | Not exposed by app CLI | Embree/SciPy-facing app today | Could become an OptiX fixed-radius app, but current public CLI does not expose OptiX. |
| `examples/rtdl_event_hotspot_screening.py` | Not exposed by app CLI | Embree/SciPy-facing app today | Same as service coverage. |
| `examples/rtdl_facility_knn_assignment.py` | Not exposed by app CLI | Embree/SciPy-facing app today | Same as service coverage. |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | Not exposed by app CLI | CPU-only public script | Not an OptiX performance path today. |
| `examples/rtdl_polygon_set_jaccard.py` | Not exposed by app CLI | CPU-only public script | Not an OptiX performance path today. |

## Bottleneck Taxonomy

1. Backend algorithm mismatch.

   Some app-level OptiX paths dispatch to CPU host-indexed algorithms inside
   the OptiX native library. This is most important for graph BFS/triangle and
   default segment/polygon app paths. These paths can be correct, but they must
   not be described as RT-core accelerated.

2. One-shot setup cost.

   GPU JIT, BVH construction, data upload, and output allocation can dominate
   small or one-shot app calls. Prior reports show visible warmup outliers for
   GPU backends. Future performance gates must report cold, warm, prepared,
   and repeated-query timings separately.

3. Python/ctypes preparation overhead.

   Prior DB review evidence already showed that a large part of DB "prepare"
   time can be Python-side data encoding and ctypes marshaling rather than
   native BVH work. This overhead is part of RTDL's user-visible performance
   and needs direct measurement.

4. Python row materialization.

   The default OptiX runtime returns `tuple[dict, ...]` rows. That is useful for
   examples and debugging, but it is not a high-performance interface for large
   outputs. Apps should use raw/array result modes or native aggregate outputs
   when they do not need every row as a Python object.

5. Python reductions and app post-processing.

   `rt.reduce_rows(...)` is a useful programming-model helper, but it is a
   Python standard-library reduction over already-emitted rows. It is not a
   native backend reduction. Robot collision, Hausdorff, outlier detection,
   DBSCAN, and Barnes-Hut all need native summary forms if app-level speed is
   the target.

6. Output volume.

   Pair-row and neighbor-row workloads can produce large result sets. If the
   app only needs a count, any-hit flag, max distance, core-point flag, or
   collision flag, emitting all rows and then reducing in Python is the wrong
   performance contract.

7. Hardware evidence gap.

   Several existing Linux performance reports were run on a GTX 1070. Those
   results are useful GPU/backend evidence, but the GTX 1070 has no NVIDIA RT cores.
   They cannot prove RT-core acceleration. RTX-class hardware is needed before
   RTDL can make strong NVIDIA RT-core performance claims.

## Required OptiX Performance Review Method

Every public app with `--backend optix` should have a phase-split benchmark:

| Phase | Measurement |
| --- | --- |
| Python input construction | time spent generating or loading app data |
| RTDL packing/normalization | Python-to-native conversion and ctypes/array packing |
| Native prepare | OptiX context, module, pipeline, BVH, prepared dataset, or device buffer setup |
| Native execute | actual kernel/traversal launch time |
| Copy-back | device-to-host result transfer |
| Row materialization | native result to Python dict/tuple/list conversion |
| App reduction/postprocess | Python reductions, clustering, force computation, JSON formatting |
| Total app wall time | what the user experiences |

The report must include cold and warm timings, and prepared/unprepared timings
where a prepared API exists. A single total wall time is insufficient for this
performance goal.

## Action Plan

1. Make OptiX truth classification machine-readable.

   Add an app-level performance classification field for each OptiX-exposed
   app: `optix_traversal`, `cuda_compute`, `host_indexed`, or
   `python_dominated`. This prevents future docs from equating OptiX selection
   with RT-core acceleration.

2. Build an OptiX phase profiler for public apps.

   The profiler should run every OptiX-exposed app at small, medium, and large
   scales and emit the phase table above. It must record GPU model and whether
   the GPU has RT cores.

3. Promote prepared and raw result APIs in performance paths.

   Use prepared datasets/scenes for repeated queries. Use raw/array output
   instead of `tuple[dict, ...]` when the app is doing a scalar or compact
   reduction.

4. Convert flagship apps to native summary outputs.

   Priority order:

   - Robot collision: native pose-level any-hit/collision count.
   - DB analytics: prepared columnar dataset plus native grouped outputs.
   - Hausdorff: native max nearest-distance output.
   - Outlier/DBSCAN: native neighbor-count/core-point outputs.
   - Barnes-Hut: native candidate count and optional partial force reduction.

5. Fix or reclassify host-indexed OptiX app paths.

   Graph and segment/polygon apps should either get native GPU/OptiX kernels or
   be explicitly marked as correctness/compatibility paths until that work is
   done.

6. Run RTX-class validation.

   Future OptiX performance claims must include at least one RTX-class NVIDIA
   host. GTX 1070 results remain valid for backend portability and CUDA-driver
   behavior, but not for RT-core claims.

## Definition Of Done For This Performance Goal

RTDL should not consider an OptiX app performance goal complete until every
OptiX-exposed public app has:

- correctness parity against the CPU oracle or accepted external baseline;
- phase-split timing that exposes Python, interface, native, copy-back, and
  app-postprocess costs;
- an explicit acceleration classification: OptiX traversal, CUDA compute,
  host-indexed fallback, or Python dominated;
- cold and warm timings;
- prepared and repeated-query timings when relevant;
- fair baselines for the app domain;
- no RT-core acceleration claim unless tested on RTX-class hardware and the
  dominant operation uses OptiX traversal.

## Immediate Recommendation

Use robot collision / visibility / ray-triangle any-hit as the first OptiX
performance flagship. It has the cleanest mapping to RT cores, already uses
early-exit traversal, and has a clear next optimization: avoid emitting all
ray rows when the app only needs pose-level collision flags or counts.

Treat DB analytics as the second flagship after prepared columnar datasets and
native aggregation are tightened. Treat KNN/radius apps as GPU-compute
applications unless and until their dominant algorithm is rewritten around
OptiX traversal. Treat graph and default segment/polygon OptiX app paths as
correctness/compatibility paths until host-indexed work is replaced or clearly
reclassified.

## Current Release Boundary

This review does not block the current released version by itself. It creates
the next performance goal. The release-safe statement today is:

RTDL has multiple public apps that expose OptiX, and several have credible GPU
backend evidence. However, only a subset of those paths are currently OptiX
traversal paths eligible for RT-core acceleration; several app bottlenecks live
in Python packing, Python row materialization, Python reductions, CPU
host-indexed fallbacks, or CUDA-compute kernels rather than RT traversal.
