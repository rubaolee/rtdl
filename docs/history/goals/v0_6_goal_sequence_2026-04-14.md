# v0.6 Goal Sequence

Date: 2026-04-14
Last Updated: 2026-04-14
Status: active

## Purpose

Record the corrected `v0.6` ladder after the public rollback from the earlier
mis-scoped graph-runtime line.

## Sequence

1. Goal 385
   - define `v0.6` as an RTDL-kernel graph version aligned with the SIGMETRICS
     2025 paper

2. Goal 386
   - define the RT graph kernel surface users actually write

3. Goal 387
   - define the RT graph execution interpretation:
     - graph data mapping into the RT view
     - `traverse`
     - `refine`
     - `emit`

4. Goal 388
   - define the graph lowering/runtime contract for the RT-kernel form

5. Goal 389
   - bounded Python truth-path closure for RT-kernel `bfs`

6. Goal 390
   - bounded Python truth-path closure for RT-kernel `triangle_count`

7. Goal 391
   - bounded native/oracle truth-path closure for RT-kernel `bfs`

8. Goal 392
   - bounded native/oracle truth-path closure for RT-kernel `triangle_count`

9. Goal 393
   - Embree RT graph mapping and first workload closure

10. Goal 394
    - OptiX RT graph mapping and first workload closure

11. Goal 395
    - Vulkan RT graph mapping and first workload closure

12. Goal 396
    - Embree RT graph mapping and second workload closure

13. Goal 397
    - OptiX RT graph mapping and second workload closure

14. Goal 398
    - Vulkan RT graph mapping and second workload closure

15. Goal 399
    - first bounded multi-backend correctness/integration gate under the RT-kernel model

16. Goal 400
    - PostgreSQL-backed all-engine correctness gate

17. Goal 401
    - large-scale performance gate for Embree / OptiX / Vulkan with PostgreSQL as indexed external baseline

18. Goal 402
    - final corrected RT `v0.6` correctness and performance closure

19. Goal 403
    - pre-release code and test cleanup for the corrected `v0.6` line

20. Goal 404
    - pre-release doc check for the corrected `v0.6` line

21. Goal 405
    - pre-release flow audit for the corrected `v0.6` line

22. Goal 406
    - internal release hold after Goals 403-405 while external independent
      release checks are performed

23. Goal 407
    - final corrected RT release decision

24. Goal 408
    - git release act for `v0.6.1`

25. Goal 409
    - repo-wide file-by-file status audit with checker / verifier / final-proof AI chain

## Discipline

Each goal must stay bounded, preserve the RTDL-kernel identity, and save the
required review chain before being called closed.

For Goals 403-406, the minimum closure requirement is 3-AI consensus:

- Gemini
- Claude
- Codex
