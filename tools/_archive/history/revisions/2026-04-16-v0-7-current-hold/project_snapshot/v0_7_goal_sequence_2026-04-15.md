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

20. Goal 432
    - phase-split performance clarification:
      - RTDL prepare / execute / total
      - PostgreSQL setup / query

21. Goal 433
    - define the native prepared DB dataset contract:
      - Python becomes a thin wrapper
      - large table encoding/build moves to native backend ownership
      - repeated-query semantics are explicit

22. Goal 434
    - Embree native prepared DB dataset implementation and correctness gate

23. Goal 435
    - OptiX native prepared DB dataset implementation and correctness gate

24. Goal 436
    - Vulkan native prepared DB dataset implementation and correctness gate

25. Goal 437
    - repeated-query DB performance gate against PostgreSQL on Linux:
      - RTDL native prepared dataset build once + many queries
      - PostgreSQL setup/index once + many queries

26. Goal 438
    - refresh the `v0.7` branch release-gate package after native prepared
      datasets and repeated-query performance are closed

27. Goal 439
    - external tester report intake and triage gate:
      - preserve each external report as evidence
      - classify findings as blocker / follow-up / non-blocking note
      - map accepted issues to concrete v0.7 goals
      - keep no-tag/no-merge hold until tester findings are resolved or
        explicitly waived with consensus

28. Goal 440
    - Embree columnar prepared DB dataset transfer path:
      - add a first native columnar table ingestion ABI
      - keep row-struct compatibility path intact
      - prove row/columnar parity for the bounded DB family
      - measure prepare-time effect before extending to OptiX and Vulkan

29. Goal 441
    - OptiX columnar prepared DB dataset transfer path:
      - mirror the accepted Embree columnar ABI pattern
      - keep row-struct compatibility path intact
      - prove row/columnar parity for the bounded DB family on Linux
      - measure prepare-time effect on the Linux GPU host

30. Goal 442
    - Vulkan columnar prepared DB dataset transfer path:
      - mirror the accepted Embree/OptiX columnar ABI pattern
      - keep row-struct compatibility path intact
      - prove row/columnar parity for the bounded DB family on Linux
      - measure prepare-time effect on the Linux GPU host

31. Goal 443
    - refreshed cross-backend repeated-query performance gate after columnar
      prepared dataset transfer:
      - measure Embree, OptiX, and Vulkan with `transfer="columnar"`
      - include PostgreSQL setup/query on Linux
      - keep the old Goal 437 row-transfer gate as historical evidence

32. Goal 444
    - refresh release-facing v0.7 docs after columnar prepared dataset transfer:
      - replace stale row-transfer ingestion caveats
      - point current performance claims to Goal 443
      - keep DBMS/PostgreSQL boundaries explicit

33. Goal 445
    - use columnar transfer in the high-level prepared DB kernel path:
      - `prepare_embree(...).bind(...)`
      - `prepare_optix(...).bind(...)`
      - `prepare_vulkan(...).bind(...)`
      - keep direct prepared dataset row-transfer compatibility intact

34. Goal 446
    - post-columnar DB regression sweep:
      - run correctness and prepared-dataset tests for Goals 420-424, 432,
        434-436, 440-442, and 445
      - include Linux PostgreSQL where available
      - record pass/fail/skip evidence without changing release status

35. Goal 447
    - packaging-readiness audit for the v0.7 DB columnar block:
      - record current dirty-tree shape
      - confirm which goals have consensus
      - identify active hold conditions
      - recommend next packaging action without staging, committing, tagging, or
        merging

36. Goal 448
    - concrete packaging manifest for the v0.7 DB columnar block:
      - enumerate the runtime, test, script, report, handoff, and consensus
        files that belong to the package
      - separate included evidence from deliberately preserved invalid/review
        trail artifacts
      - define a safe staging strategy
      - keep no-stage/no-commit/no-tag/no-merge status until explicit user
        approval

37. Goal 449
    - packaging manifest validation gate:
      - mechanically verify that the core Goal 448 package paths exist
      - verify that required consensus anchors exist
      - verify that known invalid review attempts are not counted as valid
        consensus
      - write machine-readable evidence without staging, committing, tagging, or
        merging

38. Goal 450
    - Linux correctness and performance refresh:
      - validate PostgreSQL availability on `lestat-lx1`
      - build/probe Embree, OptiX, and Vulkan backends from the synced checkout
      - run the v0.7 DB correctness sweep with live PostgreSQL enabled
      - run the PostgreSQL-inclusive columnar repeated-query performance gate
      - record evidence and consensus without staging, committing, tagging, or
        merging

39. Goal 451
    - PostgreSQL baseline index audit:
      - compare no-index, current single-column predicate indexes, and
        composite/covering indexes on Linux PostgreSQL
      - capture `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` evidence
      - compare setup, query, and total repeated timing
      - clarify whether Goal 450 PostgreSQL timing was naive, indexed, or
        fully tuned
      - keep RTDL-vs-PostgreSQL claims bounded and honest

40. Goal 452
    - RTDL versus best-tested PostgreSQL performance rebase:
      - combine Goal 450 RTDL columnar timings with Goal 451 PostgreSQL
        index-mode audit evidence
      - compare RTDL against the best tested PostgreSQL query-time mode and
        best tested PostgreSQL total setup-plus-repeated-query mode
      - keep the older single-column indexed PostgreSQL baseline as historical
        continuity, not the strongest baseline
      - report query-only and total-time claims separately

41. Goal 453
    - release-facing performance wording refresh after Goal 452:
      - make Goal 452 the canonical v0.7 DB performance comparison
      - keep Goal 450 as historical single-column indexed PostgreSQL evidence
      - state that query-only results are mixed against best-tested PostgreSQL
      - state that total setup-plus-10-query time favors RTDL in the measured
        Linux evidence
      - preserve the no-DBMS, no-arbitrary-SQL, no-exhaustive-PostgreSQL-tuning
        boundary

42. Goal 454
    - post-wording v0.7 DB evidence/package validation:
      - mechanically verify Goal 450-453 evidence and consensus files
      - verify Linux correctness/performance evidence fields
      - verify release-facing docs use Goal 452 and avoid stale Goal 443/450-only
        performance wording
      - verify no DBMS, arbitrary SQL, exhaustive PostgreSQL tuning, or release
        authorization claim is introduced

43. Goal 455
    - post-454 packaging manifest refresh:
      - extend the v0.7 DB package boundary to include Goals 450-454
      - keep runtime/test/script/docs/evidence/consensus categories explicit
      - identify generated/archive artifacts that should not be staged by
        default
      - recommend a safe staging split without performing staging, commit, tag,
        push, merge, or release

44. Goal 456
    - pre-stage file-list ledger:
      - generate a concrete include/defer/exclude ledger from the dirty-tree
        package candidate set
      - keep archive/generated artifacts separated from release package content
      - do not stage or commit

45. Goal 457
    - manual review path resolution:
      - resolve ambiguous paths from the pre-stage ledger
      - keep explicit include/defer/exclude decisions auditable
      - preserve no-stage/no-release status

46. Goal 458
    - pre-stage validation gate:
      - mechanically validate the current v0.7 package evidence before any
        staging action
      - record pass/fail/skip evidence without staging

47. Goal 459
    - dry-run staging command plan:
      - generate the safe staging command plan only
      - do not execute staging

48. Goal 460
    - ready-to-stage final hold:
      - record that the package is prepared for explicit user staging approval
      - keep branch hold active

49. Goal 461
    - v0.7 DB app demo:
      - add app-level demo code showing how bounded DB kernels are used from an
        application
      - test and review without widening RTDL into a DBMS claim

50. Goal 462
    - v0.7 DB kernel-form app demo:
      - add kernel-form demo code showing the language-facing DB feature shape
      - test and review alongside the app-level demo

51. Goal 463
    - post-demo pre-stage refresh:
      - refresh file-list, validation, and dry-run staging evidence after the
        demo additions
      - maintain no-stage/no-release status

52. Goal 464
    - Linux fresh-checkout validation:
      - sync the current branch to Linux
      - build/probe missing backends as needed
      - validate import, PostgreSQL, focused tests, performance artifacts, and
        app/kernel demos

53. Goal 465
    - post-Linux-fresh pre-stage refresh:
      - refresh package evidence after Goal 464
      - keep advisory status and no-stage hold

54. Goal 466
    - release reports refresh after Linux fresh-checkout validation:
      - update v0.7 release statement, support matrix, audit report, and tag
        hold after Goal 464

55. Goal 467
    - external test report response:
      - triage the newer macOS correctness and Windows audit reports
      - fix stale Embree DLL/API blocker handling in the current branch
      - retest the bounded graph/API/Embree deployment surface on Windows
      - record 2-AI consensus

56. Goal 468
    - release reports refresh after external report response:
      - update v0.7 release statement, support matrix, audit report, tag hold,
        and goal ladder after Goal 467
      - preserve Linux as the canonical v0.7 DB correctness/performance
        validation platform
      - keep no-stage/no-tag/no-merge status

57. Goal 469
    - v0.7 DB attack-report intake and local gap closure:
      - preserve the 105-test external DB attack report and test artifact
      - close local non-platform gaps for empty DB inputs, float `between`,
        alternate integer `grouped_sum` fields, large boundary row counts, and
        repeated kernel compilation cleanup
      - map live PostgreSQL and native backend coverage back to the prior
        Linux-only gates instead of reclassifying them as macOS blockers
      - keep no-stage/no-tag/no-merge status

58. Goal 470
    - v0.7 pre-release full test, doc refresh, and audit checkpoint:
      - run full local unittest discovery and fix release-blocking harness
      failures
      - run focused Linux v0.7 DB/PostgreSQL/native backend validation from a
      synced current worktree
      - refresh release-facing docs through the current Goal 470 state
      - produce a mechanical doc/audit validation artifact
      - keep no-stage/no-tag/no-merge status

59. Goal 471
    - external v0.6.1 expert attack-suite intake:
      - preserve the newer Windows Embree v0.6.1 attack-suite report
      - accept its positive graph/geometry stress evidence as supporting
        external evidence
      - explicitly avoid treating its "Certified for deployment" wording as
        v0.7 staging, tag, merge, or release authorization

60. Goal 472
    - release reports refresh after Goal 471:
      - update release-facing v0.7 docs to include the Goal 471 evidence and
        boundary
      - keep the branch in no-stage/no-tag/no-merge/no-release hold

61. Goal 473
    - post-Goal472 release evidence audit:
      - mechanically validate Goal 471 and Goal 472 artifacts, release-doc
        boundary language, external ledger entries, and preserved report
        workload evidence
      - keep no-stage/no-tag/no-merge/no-release status

62. Goal 474
    - post-Goal473 pre-stage refresh:
      - refresh the advisory dirty-tree filelist and dry-run staging command
        plan through Goal 473
      - verify closed-goal evidence coverage and preserve Goal 439 as the open
        external-tester intake ledger
      - exclude archive artifacts and keep no-stage/no-tag/no-merge/no-release
        status

63. Goal 475
    - external input manifest:
      - index current v0.7 source-paper PDFs, preserved external tester
        reports, AI reviews, and test/performance/audit result artifacts
      - verify the external tester intake ledger contains T439-001 through
        T439-012
      - keep no-stage/no-tag/no-merge/no-release status

64. Goal 477
    - broad unittest discovery repair:
      - run the broader project test discovery pattern that includes
        `goal*_test.py`
      - repair narrow test-harness portability issues found by that sweep
      - preserve the final local test result as v0.7 pre-release evidence
      - keep no-stage/no-tag/no-merge/no-release status

65. Goal 478
    - release reports refresh after Goal477:
      - update v0.7 release-facing reports to mention the newer broad local
        unittest discovery evidence
      - preserve that Goal477 has Claude and Gemini external-review acceptance
        but is not release authorization
      - keep no-stage/no-tag/no-merge/no-release status

66. Goal 479
    - release-candidate audit after Goal478:
      - verify Goal477 and Goal478 Codex/Claude/Gemini review evidence
      - verify invalid Gemini Flash placeholder attempts are marked invalid
      - verify release-facing reports preserve hold and no-release boundaries
      - verify no active retired non-release metrics task references remain in
        the current v0.7 release path
      - keep no-stage/no-tag/no-merge/no-release status

67. Goal 480
    - release reports refresh after Goal479:
      - update v0.7 release-facing reports to mention the Goal479
        release-candidate audit
      - preserve hold/no-release/no-tag/no-merge boundaries
      - keep no-stage/no-tag/no-merge/no-release status

68. Goal 481
    - post-Goal480 pre-stage hold ledger:
      - enumerate and classify the current dirty worktree
      - verify closed-goal evidence coverage through Goal480
      - keep Goal439 open as external-tester intake infrastructure
      - exclude only archive artifacts by default
      - keep no-stage/no-tag/no-merge/no-release status

69. Goal 482
    - post-Goal481 dry-run staging plan:
      - enumerate the current dirty worktree after Goal481
      - include prior release-package evidence, including Goal481 artifacts
      - generate grouped advisory `git add -- ...` command strings
      - exclude only archive artifacts by default
      - keep no-stage/no-tag/no-merge/no-release status

70. Goal 483
    - release reports refresh after Goal482:
      - update v0.7 release-facing reports with the Goal482 dry-run staging
        plan evidence
      - preserve Claude/Gemini review evidence and no-stage/no-release
        boundaries
      - keep no-stage/no-tag/no-merge/no-release status

71. Goal 484
    - post-Goal483 release hold audit:
      - verify current dirty-tree package classification
      - verify closed-goal evidence coverage through Goal483
      - verify release-report hold language and Goal482/Goal483 references
      - verify current release-audit scripts remain valid
      - keep no-stage/no-tag/no-merge/no-release status

72. Goal 485
    - ready for user staging decision hold:
      - record Goal484 as the latest accepted non-mutating release-hold audit
      - state that the package is ready for an explicit user staging decision
      - preserve no-stage/no-tag/no-merge/no-release status

73. Goal 486
    - post-disk-cleanup artifact integrity audit:
      - verify report JSON artifacts parse after the disk-full event
      - verify report text artifacts are non-empty
      - verify home Git temp garbage cleanup is complete
      - verify disk-space safety and current release-hold audits remain valid
      - keep no-stage/no-tag/no-merge/no-release status

74. Goal 487
    - post-Goal486 release-hold stability audit:
      - verify Goal486 is accepted by Codex, Claude, and Gemini
      - verify the accidental home-directory Git repository remains disabled
      - verify no runaway home-level Git add/list process is active
      - verify the release package remains held with no stage/commit/tag/push/merge/release action
      - keep no-stage/no-tag/no-merge/no-release status

## Discipline

Each goal must stay bounded, preserve RTDL as a workload-kernel/runtime system,
and avoid turning `v0.7` into a DBMS claim.

Every completed goal in this line requires at least 2-AI consensus before it is
called closed.
