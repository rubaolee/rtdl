Please perform a final total code review of the clean RTDL `v0.4` release-prep
branch at:

- `[REPO_ROOT]`

Important context:

- This is a pre-release code review for `v0.4.0`.
- The nearest-neighbor line is expected to be closed across:
  - CPU/oracle
  - Embree
  - OptiX
  - Vulkan
- Goal 229 fixed the last known heavy-case accelerated
  `fixed_radius_neighbors` correctness blocker.
- Goal 235 established that full RTNN paper reproduction belongs to `v0.5`,
  not to the `v0.4` release gate.

Review focus:

- bugs
- behavioural regressions
- backend-claim mismatches
- release-critical test gaps
- stale code paths that could invalidate `v0.4` claims

Start from these anchor files:

- `[REPO_ROOT]/src/rtdsl/`
- `[REPO_ROOT]/src/native/`
- `[REPO_ROOT]/tests/`
- `[REPO_ROOT]/docs/release_reports/v0_4/`
- `[REPO_ROOT]/docs/reports/goal228_v0_4_heavy_nearest_neighbor_perf_2026-04-10.md`
- `[REPO_ROOT]/docs/reports/goal229_fixed_radius_neighbors_accelerated_boundary_fix_2026-04-10.md`
- `[REPO_ROOT]/docs/reports/goal232_final_pre_release_verification_2026-04-10.md`

Write the review to:

- `[REPO_ROOT]/docs/reports/gemini_v0_4_total_code_review_2026-04-11.md`

Use these sections only:

- Verdict
- Findings
- Risks
- Conclusion

If there are no blocking findings, say so explicitly.
