# v0.5 Goal Sequence

Date: 2026-04-11
Last Updated: 2026-04-12
Status: active

## Purpose

Record the working goal ladder from the `v0.5` charter to the first meaningful
paper-consistency milestones.

## Sequence

1. Goal 258
   - open the `v0.5` paper-consistency charter

2. Goal 259
   - close the first engineering design decision for the 3D nearest-neighbor
     line

3. Goal 260
   - add first-class 3D point public types and Python-reference nearest-neighbor
     support

4. Goal 261
   - add runtime normalization and CPU/oracle contract closure for the 3D point
     line, with honest platform/back-end boundaries

5. Goal 262
   - decide and document the paper-consistent bounded-radius KNN public contract

6. Goal 263
   - implement the additive `bounded_knn_rows` public surface

7. Goal 264
   - close the 2D CPU/oracle truth path for `bounded_knn_rows`

8. Goal 265
   - add an RTNN dataset-family registry and acquisition-plan layer

9. Goal 266
   - baseline-library harness decisions and first adapters

10. Goal 267
   - first labeled reproduction matrix:
     - exact reproduction
     - bounded reproduction
     - RTDL extension

11. Goal 268
   - bounded dataset manifests for the RTNN family set

12. Goal 269
   - first external baseline adapter skeleton for cuNSearch

13. Goal 270
   - deterministic bounded KITTI frame acquisition helper

14. Goal 271
   - executable KITTI bounded point loader from saved manifests

15. Goal 272
   - portable KITTI bounded point-package materialization

16. Goal 273
   - bounded cuNSearch fixed-radius response parser

17. Goal 274
   - bounded offline RTDL-vs-external fixed-radius comparison harness

18. Goal 275
   - live Linux cuNSearch fixed-radius driver from RTDL request JSON

19. Goal 276
   - first live bounded Linux RTDL-vs-cuNSearch comparison on portable 3D packages

20. Goal 277
   - Linux KITTI acquisition prep and readiness gate

21. Goal 278
   - real KITTI raw-layout support and bounded frame offsets

22. Goal 279
   - first real KITTI bounded live RTDL-vs-cuNSearch comparison on Linux

23. Goal 280
   - live cuNSearch output-precision hardening for larger-radius real KITTI parity

24. Goal 281
   - bounded 3D PostGIS fixed-radius support

25. Goal 282
   - PostGIS 3D n-D index hardening and live plan audit

26. Goal 283
   - first three-way KITTI performance result across RTDL, cuNSearch CUDA, and PostGIS 3D

27. Goal 284
   - bounded KITTI three-way scaling sweep and first cuNSearch correctness boundary capture

28. Goal 285
   - minimal real KITTI duplicate-point reproducer for the cuNSearch correctness boundary

29. Goal 286
   - duplicate-point preflight guard for the live cuNSearch strict-parity comparison path

30. Goal 287
   - duplicate-free KITTI frame-pair selector for strict cuNSearch comparisons

31. Goal 288
   - duplicate-free KITTI three-way rerun beyond the blocked duplicate-point case

32. Goal 289
   - first large duplicate-free KITTI boundary at `4096` points

33. Goal 290
   - duplicate-free KITTI continuation at `8192` points

34. Goal 291
   - duplicate-free KITTI continuation at `16384` points with widened search
     window

35. Goal 292
   - native CPU/oracle closure for 3D `fixed_radius_neighbors`

36. Goal 293
   - native CPU/oracle closure for 3D `bounded_knn_rows`

37. Goal 294
   - native 3D RTDL versus PostGIS performance on duplicate-free KITTI
     fixed-radius workloads

38. Goal 295
   - native 3D RTDL versus PostGIS performance on duplicate-free KITTI
     bounded-KNN workloads

39. Goal 296
   - native CPU/oracle closure for 3D `knn_rows`

40. Goal 297
   - native 3D RTDL versus PostGIS performance on duplicate-free KITTI
     `knn_rows` workloads

41. Goal 298
   - Embree 3D `fixed_radius_neighbors` closure

42. Goal 299
   - Embree 3D `bounded_knn_rows` closure

43. Goal 300
   - Embree 3D `knn_rows` closure

44. Goal 310
   - first Linux large-scale Embree nearest-neighbor performance and KNN
     optimization closure on duplicate-free KITTI

45. Goal 311
   - Linux OptiX 3D nearest-neighbor closure

46. Goal 312
   - first Linux large-scale native-vs-Embree-vs-OptiX nearest-neighbor
     benchmark on duplicate-free KITTI

47. Goal 313
   - same-scale Linux backend table on expanded KITTI data for:
     - PostGIS
     - Embree
     - OptiX
   - with Vulkan explicitly excluded from 3D point nearest-neighbor claims
     until that backend line is actually closed

48. Goal 315
   - Vulkan 3D nearest-neighbor closure on Linux for:
     - `fixed_radius_neighbors`
     - `bounded_knn_rows`
     - `knn_rows`

49. Goal 316
   - first Linux large-scale accelerated backend table at `32768 x 32768` for:
     - Embree
     - OptiX
     - Vulkan

50. Goal 317
   - consolidated Linux four-backend nearest-neighbor performance report for:
     - PostGIS
     - Embree
     - OptiX
     - Vulkan

51. Goal 318
   - first release-facing `v0.5` preview support matrix with explicit Linux,
     local macOS, and Windows boundaries

52. Goal 319
   - bounded cross-platform Embree correctness matrix for the 3D
     nearest-neighbor trio on:
     - Linux
     - local macOS
     - Windows

53. Goal 320
   - preview-level readiness audit for the current `v0.5` line, separating:
     - preview-ready
     - final-release-ready

54. Goal 321
   - frontpage clarity pass for version state, backend names, and platform
     support boundaries

55. Goal 322
   - adopt the rewritten comprehensive transition audit as the canonical
     `Goals 241-320` whole-slice audit artifact

56. Goal 323
   - publish the `v0.5 preview` call-for-test document through the preview
     support package and stable repo path

57. Goal 324
   - adopt the final preview-session audit summary as a bounded sign-off
     artifact for the `Goals 258-323` slice

## Discipline

Each goal must stay bounded, save its review trail, and preserve the honesty
boundary between:

- what is online
- what is planned
- what is still missing for paper-faithful reproduction
