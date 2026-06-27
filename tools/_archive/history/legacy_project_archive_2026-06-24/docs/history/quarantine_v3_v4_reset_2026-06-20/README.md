# Quarantined Old V3/V4 Release Surface

Status: audit-only quarantine created on 2026-06-20.

This directory preserves old user-facing V3/V4 material that must not appear in
the current learner path. The material is kept for audit and reconstruction
only. It is not current documentation, not a tutorial track, and not a release
promise.

## Contents

| Quarantine path | Original source |
| --- | --- |
| `tutorials__current/` | `tutorials/current/` |
| `tutorials__v4_0/` | `tutorials/v4_0/` |
| `examples__v4_0/` | `examples/v4_0/` |
| `docs__release_reports__v3_0_2/` | `docs/release_reports/v3_0_2/` |
| `docs__release_reports__v4_0_0/` | `docs/release_reports/v4_0_0/` |
| `docs__engineering/` | Depublished later-version engineering notes. |
| `docs__reports/` | Depublished mixed/later-version reports and artifacts. |
| `docs__reviews/` | Depublished later-version reviews and old V2/V3 comparison review packet. |
| `src__v4/` | `src/v4/` |
| `src__rtdsl/v4_0_device_array_operator.py` | `src/rtdsl/v4_0_device_array_operator.py` |
| `scripts__v4_0/` | `scripts/v4_0_*.py` |
| `tests__v4_0/` | `tests/v4_0_*.py` |
| `docs__learn__benchmark_evidence_index.md` | `docs/learn/benchmark_evidence_index.md` |
| `docs__learn__source_tree_doctor.md` | `docs/learn/source_tree_doctor.md` |
| `docs__learn__v3_0_app_author_implementation_strategy.md` | `docs/learn/v3_0_app_author_implementation_strategy.md` |
| `docs__application_catalog.md` | `docs/application_catalog.md` |
| `docs__performance_model.md` | `docs/performance_model.md` |
| `docs__backend_maturity.md` | `docs/backend_maturity.md` |
| `docs__capability_boundaries.md` | `docs/capability_boundaries.md` |

## Rule

Do not link this material from the beginner path except to explain that it is
historical. Any useful V3 content must be copied back only after it passes the
new V3 rebuild gate in [V3 Rebuild Control](../../../rebuild/v3/README.md).
