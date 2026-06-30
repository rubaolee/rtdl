# Goal685: Engine Feature Support Contract

Date: 2026-04-21

Status: implemented; accepted by Codex, Claude, and Gemini Flash.

## Goal

Make explicit the policy that every public RTDL feature a developer can choose
has a defined behavior on every RTDL engine.

The allowed support states are:

- `native`
- `native_assisted`
- `compatibility_fallback`
- `unsupported_explicit`

This prevents blank support-matrix cells and prevents silent CPU fallback from
being mistaken for RT engine support.

## Changes

- Added machine-readable support contract:
  `/Users/rl2025/rtdl_python_only/src/rtdsl/engine_feature_matrix.py`
- Exported query helpers from `rtdsl`:
  - `rtdsl.engine_feature_support_matrix()`
  - `rtdsl.engine_feature_support(feature, engine)`
  - `rtdsl.assert_engine_feature_supported(feature, engine)`
  - `rtdsl.public_engine_features()`
  - `rtdsl.RTDL_ENGINES`
  - `rtdsl.ENGINE_SUPPORT_STATUSES`
- Added public documentation:
  `/Users/rl2025/rtdl_python_only/docs/features/engine_support_matrix.md`
- Linked the new contract from:
  - `/Users/rl2025/rtdl_python_only/README.md`
  - `/Users/rl2025/rtdl_python_only/docs/features/README.md`
  - `/Users/rl2025/rtdl_python_only/docs/current_main_support_matrix.md`
  - `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
  - `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/support_matrix.md`
- Added regression test:
  `/Users/rl2025/rtdl_python_only/tests/goal685_engine_feature_support_contract_test.py`

## Boundary

The matrix is a support-status contract, not a performance claim.

- `native` means direct backend implementation.
- `native_assisted` means real engine work plus bounded host-side refinement.
- `compatibility_fallback` means correct documented execution, but not an
  acceleration claim.
- `unsupported_explicit` means clear rejection before execution.

Important preserved non-claims:

- no broad speedup claim;
- no silent CPU fallback as RT engine support;
- no AMD GPU validation claim from HIPRT/Orochi/NVIDIA evidence;
- no Apple MPS RT traversal claim for DB or graph workloads;
- no native backend reduction claim for `reduce_rows`.

## Verification

Focused verification passed:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal685_engine_feature_support_contract_test \
  tests.goal654_current_main_support_matrix_test \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal684_v0_9_6_release_level_flow_audit_test
```

Result:

```text
Ran 15 tests in 0.008s
OK
```

## Codex Verdict

ACCEPT.

The feature-by-engine support rule is now machine-readable, documented, and
tested. The implementation preserves the release honesty boundaries by treating
compatibility paths and native-assisted paths as explicit states rather than
silently calling them fully native acceleration.

## External Review

- Claude: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal685_external_review_claude_2026-04-21.md`.
- Gemini Flash: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal685_external_review_gemini_flash_2026-04-21.md`.
- Consensus: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal685_consensus_2026-04-21.md`.
