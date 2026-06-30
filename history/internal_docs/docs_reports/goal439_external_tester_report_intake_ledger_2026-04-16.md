# Goal 439 External Tester Report Intake Ledger

Date opened: 2026-04-16

## Policy

External tester reports are release-gating evidence for the continuing bounded
`v0.7` DB line.

Each report must be preserved, read, triaged, and either resolved, mapped to a
follow-up goal, or explicitly waived with consensus. Do not tag or merge `v0.7`
while unresolved release blockers remain.

## Severity

| Severity | Meaning | Required Action |
|---|---|---|
| `S0 blocker` | correctness failure, crash, data corruption, impossible install path, or dishonest release claim | stop release movement; create fix goal |
| `S1 required` | real issue that should be fixed before tag but does not invalidate current evidence | map to fix/doc goal |
| `S2 follow-up` | valid improvement or risk that can be deferred with explicit boundary language | record follow-up |
| `S3 note` | observation only, no action required | record and monitor |
| `invalid` | cannot reproduce, out of scope, or contradicted by evidence | document rationale |

## Intake Ledger

| ID | Date Received | Report Path | Source | Affected Area | Severity | Summary | Decision | Follow-Up |
|---|---|---|---|---|---|---|---|---|
| T439-001 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_user_correctness_test_report_2026-04-16.md` | user-perspective AI | public workload correctness | `S3 note` | Independent macOS user-perspective correctness suite reports 179/179 PASS across `cpu_python_reference`, `cpu`, and `embree` where applicable. | accepted as positive evidence | record in Goal 467 response |
| T439-002 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_user_correctness_test_report_2026-04-16.md` | user-perspective AI | public workload semantics | `S2 follow-up` | Report documents non-obvious but coherent user-visible contracts: count predicates emit zero-hit rows, row predicates omit zero-hit rows, KNN always emits `k`, Jaccard can emit zero-similarity candidate rows, and BFS dedupe chooses one source. | no code fix; documentation/response note | record in Goal 467 response |
| T439-003 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_comprehensive_test_report_dev_handoff.md` and `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_windows_audit_report_2026-04-16.md` | Gemini-Antigravity | Windows Embree binary deployment | `S0 blocker` | Older Windows snapshot failed because `librtdl_embree.dll` was missing or stale and did not export required symbols such as `rtdl_embree_run_fixed_radius_neighbors`. | fixed in Goal 467 by explicit required-symbol gate, `make build-embree` front door, Windows docs, and fresh current-branch Windows retest showing `build/librtdl_embree.dll` with 22/22 required exports | Goal 467 |
| T439-004 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_comprehensive_test_report_dev_handoff.md` and `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_windows_audit_report_2026-04-16.md` | Gemini-Antigravity | Python public API export | `S0 blocker` | Older Windows snapshot lacked public `rt.csr_graph`, breaking graph tutorials. | resolved in current branch; regression added in Goal 467 to require `csr_graph` and `validate_csr_graph` in `rtdsl.__all__` | Goal 467 |
| T439-005 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_comprehensive_test_report_dev_handoff.md` | Gemini-Antigravity | PostGIS driver logic | `S2 follow-up` | External PostGIS benchmark driver required explicit `ST_SetSRID` around `ST_MakeLine` for TIGER SRID 4269. This is external-driver logic, not RTDL runtime behavior. | recorded; no RTDL code fix in Goal 467 | future PostGIS script hygiene if those Windows driver scripts enter repo |
| T439-006 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_comprehensive_test_report_dev_handoff.md` and `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_windows_audit_report_2026-04-16.md` | Gemini-Antigravity | PostgreSQL/PostGIS baseline evidence | `S3 note` | Windows PostgreSQL/PostGIS baseline is functional and fast for indexed BFS/PIP point queries, but it is baseline evidence rather than an RTDL backend pass. | accepted as external baseline evidence | record in Goal 467 response |
| T439-007 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/test_v07_db_attack_report_2026-04-16.md` | Claude external tester | v0.7 DB reference/API attack coverage | `S3 note` | Independent attack suite reports 105/105 PASS across DB IR, normalization, Python reference, native CPU oracle, SQL generation, fake PostgreSQL, cross-backend agreement, and error contracts. | accepted as positive evidence and preserved with `tests/test_v07_db_attack.py` | Goal 469 |
| T439-008 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/test_v07_db_attack_report_2026-04-16.md` | Claude external tester | local DB edge-case coverage | `S1 required` | Report lists local coverage gaps for large-table boundaries, float-bound `between`, alternate `grouped_sum` value fields, and repeated/re-entrant kernel compilation. | fixed by Goal 469 local gap-closure suite and native CPU empty-table fast path | Goal 469 |
| T439-009 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/test_v07_db_attack_report_2026-04-16.md` | Claude external tester | Linux-only PostgreSQL/native backend coverage | `S3 note` | Report lists live PostgreSQL and native Embree/OptiX/Vulkan coverage as not covered by that local suite. | mapped to prior Linux gates: Goals 423/424/429/450/464 for live PostgreSQL and cross-engine native evidence; not a macOS release blocker | Goal 469 |
| T439-010 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md` | Antigravity external tester | Windows v0.6.1 Embree graph/geometry stress | `S3 note` | Expert attack suite reports successful BFS Galaxy, Triangle Clique, PIP Cloud, LSI Cross, resource-pressure, and randomized parity workloads on Windows Embree. | accepted as positive external Windows v0.6.1 graph/geometry stress evidence | Goal 471 |
| T439-011 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md` | Antigravity external tester | release wording boundary | `S2 follow-up` | Report conclusion says RTDL v0.6.1 is "Certified" for deployment and no further remediation is required. That is external tester language, not project release authorization for v0.7. | recorded boundary; do not use as v0.7 stage/tag/merge/release approval | Goal 471 |
| T439-012 | 2026-04-16 | `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md` | Antigravity external tester | performance wording boundary | `S3 note` | Triangle Clique attack is correctness/stress evidence but took 105.7947 s for K150; useful as stress evidence, not a broad performance-win claim. | record exact numbers only; avoid overgeneralized performance claims | Goal 471 |

## Intake Procedure

1. Copy or record the external report under `docs/reports/` or `docs/external/`.
2. Add one ledger row per independent finding.
3. If the finding is `S0 blocker` or `S1 required`, create a numbered v0.7 goal
   before implementation work starts.
4. Resolve with evidence: code/doc diff, tests, platform notes, and 2-AI
   consensus.
5. Update this ledger after resolution.
