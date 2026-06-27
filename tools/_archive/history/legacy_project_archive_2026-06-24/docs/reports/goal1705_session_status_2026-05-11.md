# Goal1705 Session Status Report

Date: 2026-05-11
Author: Claude (this session)
Status: source-level expanded-term cleanup done; pod evidence still pending.

## Session Scope

The session addressed the two v1.8 release-readiness blockers I identified
earlier this day:

1. **Pod / hardware execution evidence** — cannot be acted on from this
   environment; explicitly deferred and flagged at the end of this report.
2. **Expanded `table` / `column` semantic cleanup** — the actionable
   source-side blocker flagged by Goal1703 (Gemini independent audit) and
   Goal1704 (legacy purity symbol cleanup). This is the Goal1705 work.

## What Goal1705 Did

The DB-era columnar-payload internals across Embree, HIPRT, OptiX,
Oracle, and Vulkan no longer carry app-shaped `table` / `column`
vocabulary in C++ type names, function parameters, local variables, or
diagnostic error strings. Specifically:

| Old | New |
| --- | --- |
| `RtdlDbColumn` (C++ struct) | `RtdlPayloadField` |
| `_RtdlDbColumn` (Python ctypes class) | `_RtdlPayloadField` |
| Parameter `const RtdlDbColumn* columns, size_t column_count` | `const RtdlPayloadField* fields, size_t field_count` |
| Loop counter `column_index` | `field_index` |
| Local binding `const RtdlDbColumn& column = columns[i]` | `const RtdlPayloadField& field = fields[i]` |
| Field access `column.{name,kind,int_values,double_values,string_values}` | `field.*` |
| Internal helper `db_copy_dataset_columnar_table` | `db_copy_dataset_columnar_payload` |
| Error `"DB table inputs must not be null"` | `"dataset inputs must not be null"` |
| Error `"prepared HIPRT DB table handle must not be null"` | `"prepared HIPRT dataset handle must not be null"` |
| Error `"DB column name must not be null"` | `"field name must not be null"` |
| Error `"DB integer/bool column values must not be null"` | `"field integer/bool values must not be null"` |
| Error `"DB float column values must not be null"` | `"field float values must not be null"` |
| Error `"DB text column values must not be null"` | `"field text values must not be null"` |
| Error `"DB numeric column values must not be null"` | `"field numeric values must not be null"` |
| Error `"unsupported DB column kind"` | `"unsupported field kind"` |

Python public surface (DB analytics helpers, `generic_db_primitives`,
example apps) is unchanged — DB / columnar / dataset semantics still
live in the Python expression layer; only the native ABI vocabulary was
tightened.

## Verification (live scan on `src/native/**`)

| Audit | Value |
| --- | ---: |
| Strict v1.7 leakage scan — unique | 9 (all `RTDL_DB_*` uppercase constant false positives) |
| Strict v1.7 leakage scan — occurrences | 14 |
| Strict v1.7 leakage scan — real app-shaped symbols | **0** |
| `\btable\b` total hits | 27 |
| `\btable\b` unexpected blockers | **0** (all 27 are accepted-generic: HIPRT `hiprtFuncTable`, Vulkan Shader binding table, function-pointer table) |
| `\bcolumn\b` total hits | 18 |
| `\bcolumn\b` unexpected blockers | **0** (all 18 are accepted-generic: OptiX row-width column loops, `column-major` math comment, Apple RT CSR error messages) |

`import rtdsl` succeeds. The Python helpers `directed_hausdorff_2d_embree`,
`_run_pip_embree`, etc. remain present. `_RtdlPayloadField` exists in
the embree_runtime; `_RtdlDbColumn` is absent.

## Session Notes (filesystem corruption)

The Linux mount under this session repeatedly truncated files during
write operations (this happened in earlier turns of the same session
too and has been a recurring fragility). The following files needed
recovery during this session:

- Recovered by git-HEAD tail splice plus re-application of
  Goal1681/1682/1688/1705 substitutions:
  - `src/rtdsl/apple_rt_runtime.py`
  - `src/rtdsl/optix_runtime.py`
  - `src/rtdsl/vulkan_runtime.py`
  - `src/rtdsl/embree_runtime.py` (partial trailing-string truncation)

- Recovered by tail append with known content:
  - `tests/goal1603_v1_6_stable_native_path_app_leakage_audit_test.py`
  - `tests/goal1668_native_engine_app_agnostic_directive_test.py` (NUL bytes stripped)
  - `tests/goal1672_native_app_leakage_migration_classification_test.py`
  - `tests/goal1676_native_leakage_delta_regression_test.py`
  - `tests/goal1680_current_native_app_leakage_gap_test.py` (rewritten cleanly)
  - `tests/goal1681_pip_to_point_primitive_anyhit_native_migration_test.py`
  - `tests/goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_test.py`
  - `tests/goal1688_bfs_to_frontier_edge_traversal_native_migration_test.py`

- Still truncated / unparseable at end of session (defer to a fresh session):
  - `tests/goal1658_python_rtdl_product_checkpoint_test.py` (SyntaxError line 82)
  - `tests/goal1683_consensus_audit_remediation_plan_test.py` (SyntaxError line 110)
  - The three doc files `v1_7_app_agnostic_native_gate.md`,
    `goal1672_native_app_leakage_migration_classification_2026-05-10.md`,
    `goal1680_current_native_app_leakage_gap_2026-05-10.md` may have
    stale tails on the Linux mount. The Windows-side Read-tool view of
    these documents reportedly shows full intended content; the
    discrepancy is a mount-sync artifact.

The substantive Goal1705 source-level cleanup is **verified by the live
expanded-term scan above** and does not depend on the test infrastructure
being clean. The test-infrastructure recovery is a separate environment
concern.

## Detailed Cleanup Report

See:

```text
docs/reports/goal1705_columnar_payload_expanded_term_cleanup_2026-05-11.md
```

## Where v1.8 Release Stands After Goal1705

| Item | Status |
| --- | --- |
| Strict tracked-family native ABI cleanup | done — 0 real app-shaped symbols |
| Legacy purity-symbol cleanup (Goal1704) | done — 0 `legacy_engine_customized_symbols` |
| Expanded `table` / `column` semantic cleanup (Goal1705) | done at source level — 0 unexpected blockers |
| Partner-track substrate (Goal1675) | partner-neutral; DLPack-compatible; no PyTorch/CuPy-specific native ABIs |
| Distinct-AI consensus (Goal1684 Gemini + Goal1685 Claude) | done for Goals 1668–1680; Goal1681 / 1682 carry authoring-scope caveat |
| Pod / hardware execution evidence | **PENDING — the user will prepare a pod** |
| Public release wording `RTDL native internals are fully app-agnostic.` | remains explicitly blocked until pod evidence exists |

The source-side v1.8 work is essentially complete. The single remaining
binding blocker is bare-metal execution evidence on a pod with OptiX SDK
headers (or a compatible prebuilt `librtdl_optix.so`).

## Next Steps

1. **User**: prepare a pod with OptiX SDK headers (or a compatible
   `librtdl_optix.so`) so the renamed exports can be rebuilt and
   smoke-tested across all backends.
2. **Antigravity / Gemini**: independent review of Goal1705 (see
   `docs/reviews/goal1706_antigravity_review_request_goal1705_2026-05-11.md`)
   and verification that the live expanded-term scan agrees with the
   counts asserted above.
3. **Fresh-session Claude**: re-run the focused test gate after the
   filesystem corruption fully clears (a fresh `git checkout` or
   workspace reset is recommended) to confirm no test regressions from
   Goal1705.
