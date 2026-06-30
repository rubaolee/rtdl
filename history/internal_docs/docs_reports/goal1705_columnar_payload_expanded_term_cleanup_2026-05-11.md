# Goal1705 Columnar-Payload Expanded-Term Cleanup

Date: 2026-05-11

Status: source-level cleanup of the `table`/`column` expanded-term release
blockers flagged by Goal1703 / Goal1704. No pod evidence; not a release-
readiness claim.

## Verdict

The columnar-payload internals across Embree, HIPRT, OptiX, Oracle, and
Vulkan no longer carry DB-era `table`/`column` vocabulary in C++ type
names, function parameters, local variables, or runtime error message
strings. The remaining `table`/`column` occurrences are all in
Goal1704-accepted-generic patterns (HIPRT `hiprtFuncTable` SDK
terminology, Vulkan "Shader binding table" / "extension function-pointer
table", OptiX row-width column loops, Apple RT CSR error messages,
"column-major" math comments).

## Source-Level Changes

| Old | New |
| --- | --- |
| C++ struct `RtdlDbColumn` | `RtdlPayloadField` |
| Python ctypes class `_RtdlDbColumn` | `_RtdlPayloadField` |
| Parameter `const RtdlDbColumn* columns` | `const RtdlPayloadField* fields` |
| Parameter `size_t column_count` | `size_t field_count` |
| Loop counter `column_index` | `field_index` |
| Local binding `const RtdlDbColumn& column = columns[i]` | `const RtdlPayloadField& field = fields[i]` |
| Member access `column.name/.kind/.int_values/.double_values/.string_values` | `field.*` |
| Internal helper `db_copy_dataset_columnar_table` | `db_copy_dataset_columnar_payload` |
| Error string `"DB table inputs must not be null"` | `"dataset inputs must not be null"` |
| Error string `"prepared HIPRT DB table handle must not be null"` | `"prepared HIPRT dataset handle must not be null"` |
| Error string `"DB column name must not be null"` | `"field name must not be null"` |
| Error string `"DB integer/bool column values must not be null"` | `"field integer/bool values must not be null"` |
| Error string `"DB float column values must not be null"` | `"field float values must not be null"` |
| Error string `"DB text column values must not be null"` | `"field text values must not be null"` |
| Error string `"DB numeric column values must not be null"` | `"field numeric values must not be null"` |
| Error string `"unsupported DB column kind"` | `"unsupported field kind"` |

The Python public DSL surface — DB analytics helpers, the
`generic_db_primitives` Python layer, the example apps — is unchanged.
DB / columnar / table semantics still live in the Python expression
layer; only the native ABI vocabulary was tightened.

## Expanded-Term Audit Result

Independent live scan over `src/native/**`:

| Term | Total hits | Accepted-generic | Unexpected blockers |
| --- | ---: | ---: | ---: |
| `\btable\b` | 27 | 27 | 0 |
| `\bcolumn\b` | 18 | 18 | 0 |

Accepted-generic patterns (per Goal1704):

- `hiprtFuncTable`, `hiprtCreateFuncTable`, `hiprtSetFuncTable`,
  `hiprtDestroyFuncTable`, the local `table` parameter inside HIPRT
  custom-traversal templates;
- Vulkan "Shader binding table" / "extension function-pointer table"
  SDK comments;
- OptiX row-width loops `for (size_t column = 0; column < row_width; ++column)`
  in `rtdl_optix_core.cpp`;
- Apple RT CSR adjacency error messages
  ("Apple RT BFS column index is out of range" and the equivalent
  triangle_match check);
- `column-major` math-layout comment in `rtdl_vulkan_core.cpp`.

## Strict Scan

The strict v1.7 leakage scan is unchanged at `9 / 14 / 9 / 14 / 0` — the
strict tracked-family cleanup remained complete throughout this
expanded-term cleanup.

## Release Boundary

This is source and Python-binding evidence only. No pod or hardware
validation was run.

The absolute release claim remains blocked:

```text
RTDL native internals are fully app-agnostic.
```

Allowed wording after Goal1705:

```text
RTDL has eliminated the DB-era `RtdlDbColumn`, `column_count`,
`column_index`, and "DB table" / "DB column" diagnostic-string
vocabulary from the native columnar-payload internals; the remaining
`table` and `column` occurrences in `src/native/**` are all SDK
structural (HIPRT `hiprtFuncTable`, Vulkan Shader binding table),
generic row-width indexing (OptiX), generic math layout, or CSR
adjacency error messages. The strict tracked-family ABI cleanup remains
9/14/0. Release readiness still requires distinct-AI consensus and
pod/hardware validation.
```

## Session Notes

This session also experienced filesystem-level mount-sync corruption that
truncated several test files (goal1658, goal1672, goal1676, goal1680,
goal1681, goal1682, goal1683, goal1688) and three Python runtime files
(apple_rt_runtime.py, optix_runtime.py, vulkan_runtime.py, plus a partial
truncation in embree_runtime.py). All four runtime files were recovered
in-session via git-HEAD tail splicing followed by re-application of the
Goal1681 / 1682 / 1688 / 1705 substitutions. The test files were
partially recovered but a clean fresh-session re-verification of the
focused test gate is recommended before treating Goal1705 as confirmed
on test infrastructure.

The substantive source-level cleanup is verified by the live
`src/native/**` expanded-term scan reported above.
