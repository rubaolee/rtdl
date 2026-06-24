# Goal 431 Report: v0.7 RT DB Release Gates

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_431_v0_7_rt_db_release_gates.md`

## Purpose

This goal defines the release-gated branch state for the bounded `v0.7` DB
line after the backend, correctness, and performance goals through Goal 430 are
closed.

The intended outcome here is:

- branch-level code/test review closure
- branch-level documentation review closure
- branch-level public-surface audit closure
- branch-level hold decision packaging

It is not a merge-to-`main` or tag decision.

## Current technical readiness view

The bounded `v0.7` DB line now has:

- DB kernel surface and lowering contract closure:
  - Goals `413-416`
- bounded truth-path and native/oracle closure:
  - Goals `417-422`
- PostgreSQL-backed correctness closure:
  - Goals `423-424`
- first public DB example/tutorial introduction:
  - Goal `425` in spirit through the delivered public DB examples and tutorial
- RT backend closure for:
  - Embree
  - OptiX
  - Vulkan
  via Goals `426-428`
- cross-engine PostgreSQL correctness gate:
  - Goal `429`
- bounded Linux performance gate with PostgreSQL included:
  - Goal `430`

## Public-surface audit and fixes in this gate

The first Goal 431 pass found one real branch-surface gap:

- the public DB example CLIs still exposed only:
  - `cpu_python_reference`
  - `cpu`

That was stale relative to the now-closed DB RT backends.

The following public files were corrected:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/rtdl_db_conjunctive_scan.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/rtdl_db_grouped_count.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/rtdl_db_grouped_sum.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/rtdl_sales_risk_screening.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/tutorials/db_workloads.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_facing_examples.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/README.md`

New branch package docs were added:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/release_statement.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/support_matrix.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/audit_report.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/tag_preparation.md`

## Validation evidence used in this gate

### Prior bounded technical closure

This gate relies on already-closed bounded evidence from:

- Goal `426` Embree DB backend closure
- Goal `427` OptiX DB backend closure
- Goal `428` Vulkan DB backend closure
- Goal `429` cross-engine PostgreSQL correctness gate
- Goal `430` bounded Linux performance gate

### Local public-surface checks

Syntax check:

- `python3 -m py_compile`
  - `examples/rtdl_db_conjunctive_scan.py`
  - `examples/rtdl_db_grouped_count.py`
  - `examples/rtdl_db_grouped_sum.py`
  - `examples/rtdl_sales_risk_screening.py`

Local smoke checks on the current branch:

- `PYTHONPATH=src:. python3 examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference`
- `PYTHONPATH=src:. python3 examples/rtdl_db_grouped_count.py --backend cpu`
- `PYTHONPATH=src:. python3 examples/rtdl_sales_risk_screening.py --backend cpu_python_reference`

Observed local app summary:

- `highest_risk_region = west`

### Linux public RT example checks

Linux authoritative example smoke on `lestat-lx1` after syncing the updated
example files into the validation checkout:

- `PYTHONPATH=src:. python3 examples/rtdl_db_conjunctive_scan.py --backend embree`
- `PYTHONPATH=src:. python3 examples/rtdl_db_grouped_count.py --backend optix`
- `PYTHONPATH=src:. python3 examples/rtdl_db_grouped_sum.py --backend vulkan`
- `PYTHONPATH=src:. python3 examples/rtdl_sales_risk_screening.py --backend optix`

Observed outputs:

- Embree scan rows:
  - `[{\"row_id\": 3}, {\"row_id\": 4}]`
- OptiX grouped-count rows:
  - `[{\"count\": 1, \"region\": \"east\"}, {\"count\": 2, \"region\": \"west\"}]`
- Vulkan grouped-sum rows:
  - `[{\"region\": \"east\", \"sum\": 6}, {\"region\": \"west\", \"sum\": 20}]`
- OptiX app summary:
  - `highest_risk_region = west`

## Branch package decision

The current correct decision is:

- branch package: ready
- merge to `main`: no
- tag/release act: no
- hold state: yes

Why:

- the bounded `v0.7` DB line is technically coherent through Goal 430
- the public branch docs/examples are now aligned with the actual backend
  closure
- the user has explicitly said additional goals are still coming

So the right status is:

- release-gated branch package
- further-goal hold
- no mainline promotion yet

## Honest boundary to carry forward

The branch package should preserve these caveats explicitly:

- `v0.7` is a bounded DB workload-family line, not a DBMS claim
- PostgreSQL is an external correctness/performance baseline, not an RTDL
  backend
- no current RT backend beats warm-query PostgreSQL
- the branch package is review-ready and coherent, but still not the
  repository's newest tagged mainline release

## Conclusion

Goal 431 supports the bounded conclusion that:

- the `codex/v0_7_rt_db` branch is internally coherent through Goal 430
- the branch public surface is now aligned with the actual backend closure
- the correct next state is hold on the branch while further goals are executed
