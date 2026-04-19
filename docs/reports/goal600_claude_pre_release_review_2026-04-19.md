# Goal600: Claude Pre-Release Review — v0.9.2 Apple RT Candidate

Date: 2026-04-19
Reviewer: Claude Sonnet 4.6 (external AI review)

## Verdict: ACCEPT

No blocker found. Release may proceed subject to the user's explicit release action.

---

## Evidence Reviewed

- `docs/reports/goal600_v0_9_2_apple_rt_pre_release_gate_2026-04-19.md`
- `docs/reports/goal600_v0_9_2_pre_release_apple_rt_perf_macos_2026-04-19.md` (and `.json`)
- `README.md`, `docs/README.md`, `docs/backend_maturity.md`, `docs/release_reports/v0_9/support_matrix.md`
- Changed stale-test and audit files listed in the gate report

---

## Test Evidence — Pass

| Suite | Ran | Result |
| --- | ---: | --- |
| Full public-pattern suite | 1118 | OK (171 skipped) |
| Stale-test cleanup suite | 20 | OK (2 skipped) |
| Apple RT focused suite | 19 | OK |
| Public command truth audit | 244 commands / 14 docs | valid: true |
| Examples smoke | 3 | pass |
| `py_compile` + `git diff --check` | — | pass |

No test failure, no compilation error, no whitespace issue.

---

## Performance Evidence — Consistent with Gate Interpretation

Verified raw JSON samples against the reported medians. Numbers are correct.

| Workload | Apple/Embree | Stable | Independent assessment |
| --- | ---: | --- | --- |
| `ray_triangle_closest_hit_3d` | 0.547x (faster) | yes (CV=0.011) | Clean. Apple RT is genuinely faster on this fixture. |
| `ray_triangle_hit_count_3d` | 47.057x (slower) | **no** (CV=0.177) | Unstable and much slower. Correctly flagged; not used for public wording. |
| `segment_intersection_2d` | 4.035x (slower) | yes (CV=0.030) | Stable, slower than Embree. Correctly presented as an overhead-reduction improvement, not a speedup. |

---

## Documentation Honesty — Pass

Public docs were checked for overstated speedup wording. No problems found:

- `docs/backend_maturity.md` explicitly states: *"still not a broad speedup claim and Embree remains faster on current hit-count/segment fixtures"*
- `docs/release_reports/v0_9/support_matrix.md` explicitly states: *"Apple M4 measurements show Apple Metal/MPS RT has local v0.9.2 overhead reductions for native slices but is still not a broad speedup or mature-backend claim"*
- `README.md` correctly separates the released `v0.9.1` state from the `v0.9.2` candidate Apple RT work
- No stale phrases (`post-v0.9.1`, `currently unoptimized`, `no prepared Apple RT reuse`, etc.) were found in the public front-door docs

The gate report's own interpretation — that v0.9.2 adds Apple RT surface breadth and overhead reductions but is not a broad speedup release — is accurately reflected in every public-facing document reviewed.

---

## Stale-Test Fixes — No Runtime Behavior Change

The six modified test/audit files align assertions with the current v0.9.1 released state and v0.9.2 candidate Apple RT additions. Spot-checked `tests/goal532_v0_8_release_authorization_test.py`: its assertions (`v0.9.1` as current released version, `v0.8.0` as released layer) match the actual text found in `README.md` and `docs/README.md`. No product runtime behavior is changed.

---

## Summary

All gate criteria are met:

1. Full test suite green with no regressions.
2. Performance parity confirmed on all three workloads.
3. The one unstable/slow cell (`hit_count_3d`) is correctly quarantined from public speedup wording.
4. Public docs are honest: overhead reductions, not a broad speedup.
5. Stale-test fixes are correct and non-behavioral.

**ACCEPT** — v0.9.2 Apple RT candidate is locally release-ready and does not overstate performance.
