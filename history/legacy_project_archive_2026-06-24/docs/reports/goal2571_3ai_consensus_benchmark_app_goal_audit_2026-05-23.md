# Goal2571 3-AI Consensus: Benchmark-App Goal Audit

Date: 2026-05-23

## Decision

Final verdict: `ACCEPT-WITH-BOUNDARY`.

Codex, Claude, and Gemini agree that no unresolved review or consensus debt
blocks the current internal benchmark-app snapshot covering the benchmark-app
development sequence from RT-DBSCAN Goal2392 through Goal2570 cleanup.

This consensus is narrow. It does not authorize a public release, public
speedup wording, authors-code parity, paper reproduction, SQL/DBMS claims,
robot-solver claims, RT-BarnesHut reproduction claims, true zero-copy claims,
or external ABI stability claims.

## Review Inputs

| Reviewer | Artifact | Verdict |
| --- | --- | --- |
| Codex | `docs/reports/goal2571_benchmark_app_goal_audit_2026-05-23.md` | `ACCEPT-WITH-BOUNDARY` |
| Claude | `docs/reports/goal2571_claude_benchmark_app_goal_audit_review_2026-05-23.md` | `ACCEPT-WITH-BOUNDARY` |
| Gemini | `docs/reports/goal2571_gemini_benchmark_app_goal_audit_review_2026-05-23.md` | `ACCEPT` |

Claude accepted with explicit boundaries and noted that Gemini review was
pending at the time of its review. Gemini review was then completed and saved
as a repository artifact with an `ACCEPT` verdict.

## Consensus Findings

### 1. App Closeout Review Debts Are Covered

RT-DBSCAN, robot collision, RayDB-style, and Barnes-Hut each have closeout
reports with explicit non-claims. The robot-collision closeout's 2-AI
consensus requirement is closed by Goal2529's 3-AI consensus. Barnes-Hut is
covered by Goal2551's 3-AI benchmark-wave rethinking because it started after
Goal2529.

### 2. Goal2551 Debt Was Addressed Enough For Internal Snapshot Closure

The Goal2551 external reviews found real issues. The current status is:

| Finding | Consensus status |
| --- | --- |
| Missing grouped `_with_capacity` overflow signal | Addressed by Goal2552 with `overflowed_out` and fail-closed behavior |
| Active native DBSCAN/DB-shaped implementation names | Addressed for active implementation names by Goals2553-2555 and guarded by Goal2564 |
| App-specific robot and Barnes-Hut adapters in shared partner core | Addressed by Goals2562-2563 |
| RayDB-shaped shared columnar wording | Addressed by Goal2561 |
| Fragmented device-column descriptor metadata | Partially addressed by Goal2565; output descriptors remain future work |
| Fragmented grouped-reduction semantics | Partially addressed by Goals2567-2569; full native migration remains future work |
| Missing evidence manifest | Addressed by Goal2566 and refreshed by Goal2570 |

The partially addressed items are not blockers because the current claim is
only an internal snapshot and not an externally stable ABI.

### 3. Compatibility Debt Is Not Open Review Debt

Remaining DB-shaped names are compatibility surfaces, not unreviewed app logic:

- `RtdlDb*` native prelude aliases remain compatibility aliases to generic
  columnar names.
- Python DB-shaped compatibility names and ctypes class definitions remain for
  older wrappers and tests.
- Native C compatibility symbols have not been renamed.

These compatibility surfaces must not be used to claim external ABI stability
or total app-name-free historical compatibility coverage.

### 4. Public Claim Boundaries Remain Locked

All reviewers agree that the current work remains internal. In particular:

- Barnes-Hut `0.502848 ms` RTDL diagnostic timing versus authors `5.405 ms`
  `new`-mode timing is orientation-only, not a same-contract speedup ratio.
- Goal2552 overflow ABI hardening needs native GPU validation before it is
  described as externally consumable.
- `DeviceColumnDescriptor` and `rtdl.grouped_reduction.v1` are internal
  contract layers, not stable external ABI claims.
- No benchmark app authorizes broad performance wording.

## Final Constraints

These constraints apply to future docs, handoffs, and reviews unless a later
goal supersedes them with fresh evidence and external review:

- Use `internal-benchmark-apps-2026-05-23` only as an internal snapshot label.
- Describe the apps as research benchmarks or reconstruction instruments, not
  products, solvers, DBMS implementations, or paper reproductions.
- Do not publish broad speedup claims, authors-code parity claims, or paper
  reproduction claims from this audit.
- Do not claim external ABI stability while compatibility aliases and partial
  substrate migrations remain.
- Treat Barnes-Hut authors-code timing as orientation-only until same-input
  reload is fixed and reviewed.
- Treat grouped-reduction overflow ABI changes as internal until native GPU
  validation is recorded.

## Consensus Conclusion

The benchmark-app goal sequence has no unresolved review/consensus debt that
blocks the current internal snapshot. The remaining items are correctly tracked
as future engineering work or compatibility debt, not as missing review closure.
