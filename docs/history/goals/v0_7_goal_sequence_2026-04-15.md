# v0.7 Goal Sequence

Date: 2026-04-15
Last Updated: 2026-04-15
Status: active

## Purpose

Record the bounded `v0.7` ladder for RTDL database-style analytical workloads
after the released `v0.6.1` RT graph line.

## Version boundary

`v0.7` is a new workload-family line. It does not replace the released
`v0.6.1` graph scope. It extends RTDL toward bounded database-style analytical
workloads justified by RTScan and RayDB.

## Sequence

1. Goal 413
   - define `v0.7` scope and the implementation ladder

2. Goal 414
   - define the RTDL database-kernel surface users actually write

3. Goal 415
   - define the RT database execution interpretation:
     - data encoding assumptions
     - build/probe roles
     - traverse/refine/emit meaning

4. Goal 416
   - define the lowering/runtime contract for RT database kernels

5. Goal 417
   - bounded Python truth-path closure for RT-kernel `conjunctive_scan`

6. Goal 418
   - bounded Python truth-path closure for RT-kernel `grouped_count`

7. Goal 419
   - bounded Python truth-path closure for RT-kernel `grouped_sum`

8. Goal 420
   - bounded native/oracle truth-path closure for RT-kernel `conjunctive_scan`

9. Goal 421
   - bounded native/oracle truth-path closure for RT-kernel `grouped_count`

10. Goal 422
    - bounded native/oracle truth-path closure for RT-kernel `grouped_sum`

11. Goal 423
    - PostgreSQL-backed correctness gate for the bounded RT database workload family

12. Goal 424
    - PostgreSQL-backed grouped correctness gate for the bounded RT database workload family

13. Goal 425
    - public tutorial/example introduction for the bounded DB-workload surface

14. Goal 426
    - Embree backend closure for:
      - `conjunctive_scan`
      - `grouped_count`
      - `grouped_sum`

15. Goal 427
    - OptiX backend closure for:
      - `conjunctive_scan`
      - `grouped_count`
      - `grouped_sum`

16. Goal 428
    - Vulkan backend closure for:
      - `conjunctive_scan`
      - `grouped_count`
      - `grouped_sum`

17. Goal 429
    - cross-engine correctness gate against PostgreSQL for:
      - Python truth
      - native/oracle CPU
      - Embree
      - OptiX
      - Vulkan
      - PostgreSQL

18. Goal 430
    - bounded performance gate for the first RTDL DB workload family against PostgreSQL

19. Goal 431
    - release review/doc/audit gates for the bounded `v0.7` DB line

## Discipline

Each goal must stay bounded, preserve RTDL as a workload-kernel/runtime system,
and avoid turning `v0.7` into a DBMS claim.

Every completed goal in this line requires at least 2-AI consensus before it is
called closed.
