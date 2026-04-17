# Goal 471: v0.7 External v0.6.1 Expert Attack Suite Intake

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Input Report

External report preserved at:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md`

Original path:

- `/Users/rl2025/antigravity-working/rtdl-4-16/docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md`

The preserved repo copy is byte-identical to the original path at intake time.

## Evidence Accepted

This is useful positive external evidence for the bounded v0.6.1 Windows Embree
graph/geometry surface:

| Workload | Reported Scale | Reported Result |
|---|---:|---:|
| BFS Galaxy Attack | 500,000 vertices | 250,000 edges in 2.4065 s |
| Triangle Clique Attack | K150, 11,175 edges | 551,300 triangles in 105.7947 s |
| PIP Cloud Attack | 1,000,000 points vs 1,000 polygons | 4.0971 s |
| LSI Cross Attack | 100,000 segments vs 500 polygons | 2.1265 s |
| Resource Pressure Test | 200 prepare/bind/run cycles | 0.0933 s |
| Parity Attack | randomized graph expansion | bit-exact CPU oracle parity |

The report states 100% parity and no failures across the tested Windows host
configuration:

- host: `lestat@192.168.1.8`
- backend: Embree CPU ray tracing
- Python: 3.11.9
- Visual Studio 2022 BuildTools
- RTDL v0.6.1 commit: `babb4fb`

## Boundary Applied

This report is not treated as a v0.7 release gate by itself because:

- it validates v0.6.1 graph and audit workloads, not the v0.7 DB/PostgreSQL
  feature line;
- it validates Windows Embree CPU ray tracing, not the Linux PostgreSQL/native
  DB performance gates used for v0.7;
- it does not cover v0.7 DB workloads such as `conjunctive_scan`,
  `grouped_count`, or `grouped_sum`;
- it does not replace Goal 470 full local discovery or Linux focused
  PostgreSQL/native backend validation.

The external report's conclusion uses the phrase "Certified for deployment" and
"No further remediation is required." Goal 471 records that wording as external
tester language only. It is not adopted as project release authorization.

## Ledger Updates

The Goal 439 external tester intake ledger was updated with:

- `T439-010`: positive Windows v0.6.1 Embree graph/geometry stress evidence;
- `T439-011`: wording boundary for "Certified for deployment" / "No further
  remediation";
- `T439-012`: performance-claim boundary for the long Triangle Clique attack.

## Code Impact

No runtime or test code changed for Goal 471. The report identifies no defect
requiring remediation in the current branch.

## Verification

Mechanical checks performed:

```text
cmp -s /Users/rl2025/antigravity-working/rtdl-4-16/docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md
```

Result:

```text
cmp=0
```

No code test was required because this goal is an external-report intake and
claim-boundary response with no implementation diff.

## Verdict

`ACCEPT` with 2-AI consensus:

- Codex intake/claim-boundary review:
  `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal471-v0_7-external-v0_6_1-expert-attack-suite-intake.md`
- Claude external review:
  `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal471_external_review_2026-04-16.md`

Goal 471 accepts the report as supporting external Windows Embree v0.6.1 stress
evidence.

`DO NOT USE` as standalone authorization for v0.7 staging, tagging, merging, or
release.
