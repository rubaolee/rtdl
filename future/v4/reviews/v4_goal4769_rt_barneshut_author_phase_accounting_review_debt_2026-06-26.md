# Review Debt: Goal4769 RT-BarnesHut Author Phase Accounting

Date: 2026-06-26

Status: **open review debt**

Goal4769 temporarily rebuilt the authors' RT-BarnesHut binary with
`PRINT_ARTIFACT=false`, exposed the full 10M phase table, restored the source
and binary to artifact mode, and compared the authors' full internal phase
table against RTDL V4 Goal4768 profile evidence.

## Artifact Under Review

- `future/v4/v4_goal4769_rt_barneshut_author_phase_accounting_2026-06-26.md`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stdout.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stderr.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_benchmark_ready_10m_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_10m_phase_profile_pod_2026-06-26.jsonl`

## Key Facts

Author full phase output on 10M:

- sort: `6.87096s`;
- tree build: `1.71362s`;
- tree to DFS: `0.043701s`;
- install autoropes: `0.015301s`;
- intersections setup: `0.484204s`;
- RT-force: `1.12905s`;
- iterative step: `1.76213s`;
- total program: `10.4391s`.

RTDL Goal4768 warm 10M:

- sort: `6.16351s`;
- warm RT-force: `0.886653679s`;
- warm execution: `7.432850354s`;
- input download: `0.0804588s`;
- checksum relative error vs author RT checksum: `9.051486889720442e-7`;
- checksum tolerance pass: true.

Main conclusion:

- The previous comparison against author artifact-mode `Execution time` was not
  apples-to-apples because artifact mode excludes sort/tree build.
- With full phase accounting, RTDL V4 is not slower in z-order sort and is
  faster on the comparable internal-program basis for this 10M input.

## Questions For Reviewer

1. Is the temporary `PRINT_ARTIFACT=false` author rebuild an acceptable way to
   establish apples-to-apples phase accounting?
2. Is the report correct that author artifact-mode `Execution time` must not be
   used as the full-workflow denominator?
3. Is the comparison between author `Total Program time=10.4391s` and RTDL
   warm execution plus input download `~7.51s` fair enough for internal
   engineering classification?
4. Should Barnes-Hut be reclassified from "full-workflow author loss" to
   "10M checksum-valid internal-program win, public wording still blocked"?
5. What additional evidence is required before paper-facing RT-BarnesHut
   wording is allowed?

## Requested Verdict Labels

Use one:

- `accept_goal4769_complete_reclassify_barnes_hut_internal_program_win`
- `accept_with_required_amendments`
- `reject_requires_rework`
- `blocked_need_more_evidence`

## Non-Authorization

This review debt does not authorize:

- V4 release;
- public RT-BarnesHut paper-reproduction wording;
- public broad speedup claims;
- V2/V3/V4 RT-BarnesHut public speed tables;
- no-copy/device-resident tree-build claims;
- broad V4 high-performance release claims.

