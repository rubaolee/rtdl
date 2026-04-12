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

## Discipline

Each goal must stay bounded, save its review trail, and preserve the honesty
boundary between:

- what is online
- what is planned
- what is still missing for paper-faithful reproduction
