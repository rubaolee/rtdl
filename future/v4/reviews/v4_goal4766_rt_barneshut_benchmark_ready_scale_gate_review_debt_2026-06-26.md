# Review Debt: Goal4766 RT-BarnesHut Benchmark-Ready Scale Gate

Date: 2026-06-26

Status: **open review debt**

Goal4766 has local tests, POD tests, 32768 evidence, and 1M same-POD evidence
against the authors' binary. It has **not** yet received the required external
3-AI completion audit.

## Artifact Under Review

- `future/v4/v4_goal4766_rt_barneshut_benchmark_ready_scale_gate_2026-06-26.md`
- `scripts/v4_rt_barneshut_native_benchmark_ready_probe.py`
- `tests/v4_goal4766_rt_barneshut_benchmark_ready_probe_test.py`

## Evidence

- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4766_benchmark_ready_32768_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4766_benchmark_ready_1m_pod_2026-06-26.json`

## Key Facts To Review

32768:

- native warm RT-force median: `0.006929028s`;
- authors' binary RT-force: `0.05993s`;
- checksum relative error vs author RT checksum:
  `6.440149235295914e-10`.

1M:

- native warm RT-force median: `0.090850561s`;
- authors' binary RT-force: `0.094797s`;
- checksum relative error vs author RT checksum:
  `1.2294599449624855e-7`.

All native runs:

- `implementation_status_code=3`;
- `rt_core_execution=true`;
- `host_fallback_used=false`;
- `input_columns_downloaded_for_tree_build=true`.

## Questions For Reviewer

1. Does Goal4766 correctly separate cold initialization from warm execution?
2. Is the new probe appropriate for 1M scale because it avoids the CPU oracle
   while still comparing against the authors' RT checksum?
3. Are the 32768 and 1M results sufficient to call the route
   benchmark-ready, while still withholding public paper-reproduction wording?
4. Is the 1M native-vs-author timing interpretation honest, especially the
   distinction between RT-force and full execution/preprocessing?
5. Does the report correctly avoid V2/V3/V4 speed-table claims?
6. Should the next gate be 10M Treelogy, literal triangle geometry, or external
   review of the current custom-primitive geometry first?

## Requested Verdict Labels

Use one:

- `accept_goal4766_complete_pending_final_review`
- `accept_with_required_amendments`
- `reject_requires_rework`
- `blocked_need_more_evidence`

## Non-Authorization

This review debt does not authorize:

- V4 release;
- public RT-BarnesHut paper-reproduction wording;
- public speedup claims;
- V2.14/V3/V4 RT-BarnesHut speed tables;
- no-copy/device-resident tree-build claims;
- broad V4 high-performance release claims.
