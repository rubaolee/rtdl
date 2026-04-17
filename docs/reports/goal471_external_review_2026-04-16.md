# Goal 471 External Review

Date: 2026-04-16
Reviewer: Claude (external review)
Verdict: **ACCEPT**

## Scope

This review judges whether the Goal 471 intake correctly:

1. Preserves the positive Windows v0.6.1 Embree expert attack suite evidence.
2. Avoids overclaiming that evidence as v0.7 release authorization.

## Evidence Preservation: PASS

The intake preserves the external report byte-identically. The `cmp -s` check
returned zero, confirming the file at
`docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md`
is identical to the original at the Antigravity working path.

All six workload results are accurately transcribed in the intake summary table.
Numbers match the source report exactly:

| Workload | Source Report | Intake Table |
|---|---|---|
| BFS Galaxy | 250,000 edges / 2.4065 s | 250,000 edges in 2.4065 s |
| Triangle Clique | 551,300 triangles / 105.7947 s | 551,300 triangles in 105.7947 s |
| PIP Cloud | 4.0971 s | 4.0971 s |
| LSI Cross | 2.1265 s | 2.1265 s |
| Resource Pressure | 0.0933 s / 200 cycles | 0.0933 s |
| Parity | 100% bit-exact | bit-exact CPU oracle parity |

The host configuration (commit `babb4fb`, Python 3.11.9, Visual Studio 2022
BuildTools, Windows Embree) is faithfully recorded.

## Boundary Correctness: PASS

The intake applies four concrete, well-reasoned scope limits explaining why this
report does not constitute a v0.7 release gate:

1. **Feature line mismatch**: the report tests v0.6.1 graph and geometry
   workloads, not the v0.7 DB/PostgreSQL feature line.
2. **Platform mismatch**: the report covers Windows Embree CPU; v0.7 gates
   target Linux PostgreSQL and native backend performance.
3. **Missing v0.7 DB workloads**: `conjunctive_scan`, `grouped_count`, and
   `grouped_sum` are entirely absent from the external suite.
4. **No substitution for Goal 470**: the intake explicitly states it does not
   replace the full local discovery or Linux-focused validation.

The "Certified for deployment" and "No further remediation is required" phrases
from the external report conclusion are flagged as external tester language
(T439-011, severity S2 follow-up) and are not adopted as project release
authorization. That distinction is stated unambiguously in both the intake body
and its final verdict.

The Triangle Clique timing (105.7947 s for K150) is correctly bounded as
correctness/stress evidence rather than a broad performance claim (T439-012,
S3 note). The exact number is recorded; no overgeneralized throughput conclusion
is drawn.

## Ledger Integrity: PASS

The three ledger entries added by Goal 471 are present in the Goal 439 intake
ledger and accurately reflect the intake document's claims:

- **T439-010** (`S3 note`): positive Windows v0.6.1 Embree graph/geometry stress
  evidence — correctly classified as supporting evidence rather than a gate.
- **T439-011** (`S2 follow-up`): release wording boundary for "Certified" /
  "No further remediation" — correctly flagged as external tester language only.
- **T439-012** (`S3 note`): performance wording boundary for the Triangle Clique
  timing — correctly scoped to stress evidence with exact numbers only.

Severity assignments are appropriate. No ledger entry elevates this report to a
release blocker or a release authorization.

## Code Impact: PASS

No runtime or test code changed. The intake document correctly states that no
defect requiring remediation was identified, so no code fix was expected or
required.

## Conclusion

Goal 471 accurately preserves the positive external Windows v0.6.1 Embree
evidence, applies precise and well-supported boundaries against overclaiming v0.7
release authorization, records the correct ledger entries, and makes no
unauthorized code changes.

**Verdict: ACCEPT**

The intake is correct and appropriately scoped. It may be used as supporting
Windows v0.6.1 Embree stress evidence in the v0.7 release record. It must not be
used as standalone authorization for v0.7 staging, tagging, merging, or release.
