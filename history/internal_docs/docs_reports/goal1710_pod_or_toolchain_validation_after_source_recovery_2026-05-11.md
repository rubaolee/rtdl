# Goal1710 Pod or Toolchain Validation After Source Recovery

Date: 2026-05-11

Triage worker: Claude Code (independent toolchain/pod validation triage)

## Context

Goal1708 recovered the Embree source truncation from Goal1707 and removed
stale replay artifacts. Goal1709 (Gemini) independently accepted the recovery.
The remaining handoff task was to triage the local Oracle/Windows SDK toolchain
blocker that prevented `tests.goal903_embree_graph_ray_traversal_test` from
completing, and to determine whether `RTDL_VCVARS64` / Visual Studio environment
setup was the fix.

A prior local Codex validation (see
`docs/reports/goal1710_windows_toolchain_validation_after_source_recovery_2026-05-11.md`)
confirmed that `RTDL_VCVARS64` was not set in the Codex shell and that setting
it to the default VS 2022 Build Tools path unblocked the oracle build, yielding:

```text
Ran 8 tests in 2.909s
OK
```

This session performed an independent read-first triage of the same blocker and
discovered a second source-level issue introduced by Goal1708.

---

## Environment Probe Results

Probed via `test -f` and `stat` (no Python or cmd.exe execution):

| Component | Status | Path |
|-----------|--------|------|
| LLVM clang++ | FOUND | `C:\Program Files\LLVM\bin\clang++.exe` |
| vcvars64.bat | FOUND | `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat` |
| RTDL_VCVARS64 env | not set | uses default path above |
| build/librtdl_oracle.dll | existed (07:21 AM) | 318976 bytes |
| VS MSVC version | 14.44.35207 | from goal1605 transcript |
| Windows Kit UCRT | 10.0.26100.0 | from goal1605 transcript |

Command used to confirm vcvars64.bat presence:
```bash
test -f "/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Auxiliary/Build/vcvars64.bat" && echo "vcvars64 FOUND"
# Result: vcvars64 FOUND
```

---

## Root Cause: Oracle Source Truncation

The key finding is that Goal1708's semantic cleanup truncated both oracle source
files, mirroring the Embree truncation that Goal1707/Goal1708 was supposed to
recover from.

### Mtime Analysis

Before this session's repairs:

| File | Modify Time | Relative to DLL |
|------|------------|-----------------|
| `build/librtdl_oracle.dll` | 2026-05-11 07:21 AM | reference |
| `src/native/oracle/rtdl_oracle_api.cpp` | 2026-05-11 23:40 PM | +16h → needs_build=True |
| `src/native/oracle/rtdl_oracle_abi.h` | 2026-05-11 23:40 PM | +16h → needs_build=True |
| `src/native/rtdl_oracle.cpp` | 2026-05-10 16:07 PM | older → no change |
| `src/native/oracle/rtdl_oracle_geometry.cpp` | 2026-04-12 | older → no change |

Since `newest_source_mtime > library_mtime`, `_ensure_oracle_library()` would
trigger an oracle rebuild on the next test run that called `_load_oracle_library()`.

### Truncation in `rtdl_oracle_api.cpp`

`git diff HEAD -- src/native/oracle/rtdl_oracle_api.cpp` showed that Goal1708
truncated the file after the beginning of `rtdl_oracle_run_grouped_sum`'s null
check. The working tree ended at line 1784 with an unterminated string literal:

```
    if (group_field == nullptr || value_field == nullptr) {
      throw std::runtime_error("DB grouped sum requires
```

Missing content (from HEAD):
- Complete body of `rtdl_oracle_run_grouped_sum` (grouped sum loop + output)
- Closing `}, error_out, error_size);` and `}`
- `RTDL_ORACLE_EXPORT void rtdl_oracle_free_rows(void* rows) { std::free(rows); }`

The missing `rtdl_oracle_free_rows` is called 25 times in `oracle_runtime.py`
via `library.rtdl_oracle_free_rows(rows_ptr)`. Its absence from a freshly
compiled DLL would have caused `AttributeError` during `_load_oracle_library()`.

### Truncation in `rtdl_oracle_abi.h`

The header file also truncated at line 499 mid-identifier:

```
    const char* group_field,
    RtdlDbGr
```

Missing content:
- Completion of `rtdl_oracle_run_grouped_count` parameter list
- Full declaration of `rtdl_oracle_run_grouped_sum`
- Declaration of `void rtdl_oracle_free_rows(void* rows);`
- Closing `}  // extern "C"`

---

## Intentional Renames Confirmed Consistent

Goal1708 also applied intentional semantic renames that ARE consistent between
oracle sources and `oracle_runtime.py`:

| Old name | New name | Consistency |
|----------|----------|-------------|
| `rtdl_oracle_summarize_bfs_rows` | `rtdl_oracle_summarize_frontier_traversal_rows` | oracle_runtime.py line 769 ✓ |
| `rtdl_oracle_run_bfs_expand` | `rtdl_oracle_run_frontier_edge_traversal_packet` | oracle_runtime.py ✓ |
| `rtdl_oracle_run_pip` | `rtdl_oracle_run_point_primitive_anyhit_packet` | oracle_runtime.py ✓ |
| `column_index_count` | `edge_index_count` (internal variable) | consistent ✓ |

These are not the cause of the build failure and were left in place.

---

## Repair Applied

The truncated tails were restored by appending the missing content from HEAD,
while preserving all intentional Goal1708 renames:

- `src/native/oracle/rtdl_oracle_api.cpp`: restored `rtdl_oracle_run_grouped_sum`
  body and `rtdl_oracle_free_rows` at lines 1784–1832.
- `src/native/oracle/rtdl_oracle_abi.h`: restored `rtdl_oracle_run_grouped_count`
  completion, `rtdl_oracle_run_grouped_sum` declaration,
  `void rtdl_oracle_free_rows(void* rows);`, and `}  // extern "C"` at lines
  498–517.

Post-repair the oracle DLL was automatically rebuilt (likely via a background
hook or file watcher). Verification via `librtdl_oracle.lib` export table:

```bash
grep -a "rtdl_oracle_free_rows" build/librtdl_oracle.lib
# Confirmed: __imp_rtdl_oracle_free_rows rtdl_oracle_free_rows present
```

All 31 oracle exports confirmed present, including:
- `rtdl_oracle_free_rows`
- `rtdl_oracle_run_grouped_sum`
- `rtdl_oracle_summarize_frontier_traversal_rows`
- `rtdl_oracle_run_frontier_edge_traversal_packet`

Post-repair DLL mtime: `2026-05-11 23:58:22` (newer than all source files).

---

## VCVARS64 Question

**Answer: RTDL_VCVARS64 is not the fix for the oracle source truncation.**

The vcvars64.bat at the default path was present and valid. The source truncation
is the blocking compilation error (unterminated string literal in oracle_api.cpp
would cause `clang++` to abort with a syntax error, not a UCRT header issue).

The VCVARS64 setting was needed in the Codex's PowerShell session because that
environment lacked an active MSVC environment. Once vcvars64.bat is findable
(either via `RTDL_VCVARS64` or at the default VS 2022 BuildTools path), the
oracle build mechanism in `oracle_runtime.py` works correctly.

The description "Oracle native library build fails in the Windows SDK/UCRT
toolchain headers" in Goal1708 is therefore partly misleading: the error
originates from the truncated oracle source (unterminated string literal), not
from UCRT header incompatibility.

---

## Reproduction Path (Pending Execution)

Full goal903 validation requires Python execution approval. The command is:

```powershell
$env:RTDL_VCVARS64 = 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat'
$env:PYTHONPATH = 'src;.'
py -3 -m unittest tests.goal903_embree_graph_ray_traversal_test -v
```

Expected outcome (based on prior Codex run at an earlier oracle source state):

```text
Ran 8 tests in ~3s
OK
```

The oracle source repair in this session restores the oracle to a compilable
state consistent with what the Codex validated earlier.

---

## UCRT Warning Notes

The Embree compile in goal1605 produced expected UCRT deprecation warnings:

```
C:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt\stdlib.h:1183: warning:
'getenv' has been explicitly marked deprecated here [-Wdeprecated-declarations]
```

These are warnings in both Embree and oracle builds and do not prevent linking.
No UCRT errors (as opposed to warnings) were observed in prior transcripts.

---

## Pod Validation Status

Pod access was not attempted in this session. The scripts in
`scripts/goal1003_rtx_pod_group_commands.sh` and related pod executor scripts
reference `lestat@192.168.1.20` which would require SSH access not available
to this triage session. Pod validation is not documented here.

---

## Verdict

```text
needs-more-evidence
```

Grounds:
- Oracle source truncation from Goal1708 has been repaired and the oracle DLL
  verified to export all required symbols.
- VCVARS64 environment setup has been confirmed correct (default path present).
- A prior Codex run produced "Ran 8 tests in 2.909s OK" for goal903 (see
  `goal1710_windows_toolchain_validation_after_source_recovery_2026-05-11.md`).
- Python test execution was not confirmed independently in this session
  (approval-gated) — the prior run is the only test execution record.
- No pod or hardware execution evidence was produced.
- `pure_native_app_contract_ready` remains `false` pending the false-positive
  classification, distinct-AI review, and pod/hardware execution evidence
  required by Goal1668.
