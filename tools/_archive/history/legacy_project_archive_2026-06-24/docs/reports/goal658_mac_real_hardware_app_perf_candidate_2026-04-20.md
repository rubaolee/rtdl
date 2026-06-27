# Goal658: Mac Real-Hardware Performance App Candidate

Date: 2026-04-20

Status: candidate selected

## Question

Find an RTDL application that can use the Mac's real Apple hardware resources and support a fair performance comparison against existing solutions.

## Recommendation

Use a 2D line-of-sight / robot-collision-screening application built on `ray_triangle_any_hit` and `visibility_rows`.

This should be the first Mac real-hardware performance app because it maps directly to the current-main Apple RT 2D any-hit path:

- RTDL input: observer-target rays or robot-link edge rays.
- RTDL build data: obstacle triangles.
- RTDL traversal: Apple Metal/MPS-backed prism traversal.
- RTDL output: `{ray_id, any_hit}` rows.
- App reduction: `rt.reduce_rows(..., op="any")` converts edge/blocker rows into pose-collision or visibility flags.

## Why This App

This app is the cleanest Apple-hardware story because the useful output is a boolean early-exit result. It does not require counting every intersection, sorting neighbors, or materializing large candidate lists. That matches what ray-tracing hardware is good at: find whether a ray is blocked and stop after the first accepted hit.

The application is also easy to explain to users:

- "Given many visibility rays and many obstacles, tell me which sight lines are blocked."
- "Given many candidate robot poses and obstacle polygons, tell me which poses collide."

This is a real application shape, not only a microbenchmark.

## Existing-Solution Baselines

The fair comparison set should be:

| Baseline | Role | Notes |
| --- | --- | --- |
| RTDL Apple RT any-hit | target backend | Uses Apple Metal/MPS RT through current-main `run_apple_rt(..., native_only=True)` where available. |
| RTDL Embree any-hit | mature RTDL CPU baseline | Local, optimized, already documented as the mature RTDL baseline. |
| RTDL CPU/oracle | correctness baseline | Used for exact row parity, not performance positioning. |
| Shapely/GEOS STRtree or prepared geometry | external existing geometry solution | Best external comparison for 2D segment/triangle obstacle intersection on macOS. It must be installed in a local benchmark environment because the current Python environment does not have Shapely. |
| Pure Python brute force | sanity baseline | Useful only to show why an acceleration structure matters; not a professional competitor. |

If the user wants a no-new-dependency benchmark, use Apple RT vs Embree vs CPU first. If the user wants a stronger external comparison, add Shapely/GEOS in an isolated virtual environment and report install/version details.

## Why Not Hausdorff First

Hausdorff is useful, but it is not the best Mac hardware performance showcase right now:

- mature nearest-neighbor libraries such as SciPy/scikit-learn/FAISS are strong specialized baselines;
- the current local Python environment does not have SciPy or scikit-learn installed;
- Apple RT nearest-neighbor paths are documented as native/native-assisted but not currently the strongest Apple-vs-Embree performance result;
- the app reduction is max-over-nearest-neighbor rows, so the benchmark can become dominated by neighbor materialization and Python reduction rather than hardware early-exit.

Hausdorff should remain a secondary benchmark after the any-hit visibility/collision benchmark is stable.

## Why Not DB Or Graph First

Do not use DB or graph workloads as the first Mac real-hardware performance app. On Apple chips, current DB and graph support is Apple GPU compute/native-assisted, not Apple MPS ray-tracing traversal. Those workloads are important for portability, but they would blur the hardware claim.

## Benchmark Shape

Use two generated datasets with fixed random seeds:

1. Dense-blocked visibility:
   - many rays are blocked early;
   - expected to favor any-hit early-exit traversal.

2. Sparse-clear visibility:
   - most rays are not blocked;
   - exposes worst-case traversal and setup overhead.

Suggested sizes:

| Tier | Rays | Obstacle triangles | Purpose |
| --- | ---: | ---: | --- |
| correctness | 128 | 64 | fast parity gate |
| medium | 10,000 | 1,000 | interactive benchmark |
| large | 100,000 | 5,000 | real Mac hardware stress test |

Every result must report:

- setup/build time;
- query time;
- total time;
- blocked/visible counts;
- parity against CPU oracle;
- median and interquartile range over repeated runs;
- hardware/software versions.

## Fairness Rules

- Separate one-shot total time from prepared/repeated-query time.
- Give Shapely/GEOS its own spatial-index build phase if it uses STRtree.
- Give RTDL Apple RT and Embree the same input geometry and same finite rays.
- Validate exact boolean parity before timing claims.
- Do not claim a broad Apple RT speedup unless the benchmark demonstrates it on this Mac.
- Do not use Apple DB/graph timings as ray-tracing-hardware evidence.

## Implementation Target

The current app closest to this target is:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_robot_collision_screening_app.py`

It already uses:

- `ray_triangle_any_hit`
- `rt.reduce_rows(..., op="any")`
- pose-level collision summarization

However, it currently exposes only:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix`

The next implementation should add an Apple-capable benchmark harness rather than overloading the tutorial app:

- create a dedicated Mac benchmark script for visibility/collision screening;
- expose `apple_rt`, `embree`, `cpu`, and optional `shapely`;
- keep the tutorial app small and stable.

## Decision

Selected app: Mac visibility / robot collision screening using RTDL any-hit.

Reason: it is the most honest, application-shaped benchmark for current Mac Apple RT hardware because it naturally benefits from early-exit traversal and has a credible existing-solution baseline through GEOS/Shapely.
