# Goal2793 - v2.5 Partner Role Reconciliation

Date: 2026-05-31

## Purpose

Claude's Goal2773 review correctly warned that v2.5 planning must not blur two
different ideas:

- **Numba** is the declared generic fallback partner for v2.5 continuation
  kernels.
- **CuPy** is the conformance/interoperability partner, and may also be an
  explicit app-chosen phase in apps such as DBSCAN.

Goal2793 tightens the DBSCAN migration wording so that CuPy is no longer
described like the generic fallback slot.

## What Changed

Updated:

- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2793_v2_5_partner_role_reconciliation_test.py`

The RT-DBSCAN row now says:

- current hot path partner:
  `app_chosen_cupy_component_phase_with_numba_as_generic_fallback_partner`
- v2.5 status:
  `app_chosen_cupy_phase_allowed_generic_fallback_partner_remains_numba`
- first port action:
  wire generic Triton compaction/finalize where they fit, and keep any CuPy
  component/union-find phase as an explicit app-chosen phase;
- notes:
  the declared v2.5 fallback partner is Numba, while CuPy remains
  conformance/interoperability or an explicit app-chosen phase.

## Boundary

This goal does not remove CuPy from RTDL. It prevents one specific
misclassification:

| Role | v2.5 meaning |
| --- | --- |
| primary partner | Triton |
| generic fallback partner | Numba |
| conformance/interoperability partner | CuPy |
| app-chosen DBSCAN phase | CuPy is allowed if the app chooses it explicitly |

This goal does not authorize:

- hidden partner selection;
- public speedup claims;
- whole-app speedup claims;
- release readiness;
- replacing RT traversal with partner code.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2793_v2_5_partner_role_reconciliation_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test

Ran 15 tests in 0.042s
OK

py_compile with PYTHONPYCACHEPREFIX=scratch\pycache_goal2793_local

OK
```

## Decision

`accept-with-boundary`

Consensus:

`docs/reports/goal2793_v2_5_partner_role_reconciliation_consensus_2026-05-31.md`
