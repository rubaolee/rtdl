# Goal 222 Windows/Harness Portability Closure Review

## Verdict
The Windows harness and portability mechanisms are mostly well-structured and properly use cross-platform abstractions (like `pathlib` and conditional `.lib`/`.dll` handling). However, there is a critical environment-variable shadowing bug on Windows that can silently break subprocess DLL loading. Furthermore, several documentation snippets assume a Unix-like shell, which creates unnecessary friction for first-time Windows users.

## Findings
- **Environment Variable Case Shadowing**: In `scripts/goal15_compare_embree.py`, `_native_runtime_env` uses `env = os.environ.copy()` and then updates `env["PATH"]`. On Windows, `os.environ.copy()` returns a standard case-sensitive dictionary that preserves the original case of the system variables (often `"Path"`). Assigning to `"PATH"` creates a second key rather than overriding the existing one, resulting in both `"Path"` and `"PATH"` being passed to `subprocess.run`. This is known to cause undefined behavior in the Windows environment block and can silently drop the original system path, breaking DLL loading.
- **Similar Environment Issue in Smoke Tests**: The same dictionary casing issue occurs for the `PYTHONPATH` variable in `tests/report_smoke_test.py`, `scripts/run_full_verification.py`, and `scripts/run_test_matrix.py`. If a user's environment contains `"PythonPath"`, it will be shadowed.
- **Documentation Portability**: `README.md` and `docs/v0_4_application_examples.md` rely on inline environment variable syntax (e.g., `PYTHONPATH=src:. python ...`). This syntax is natively invalid in standard Windows `cmd.exe` and PowerShell, which will cause first-run execution failures for Windows users following the copy-paste instructions.
- **Missing Build Directory in Integration Test**: `tests/baseline_integration_test.py` writes output to `Path("build/test_embree_baseline_benchmark.json")` without explicitly ensuring the `build` directory exists, which may cause a `FileNotFoundError` if the directory hasn't been created by another test or script prior to execution.

## Recommended Fixes
- Fix the environment dictionary mutation in `scripts/goal15_compare_embree.py`, `tests/report_smoke_test.py`, `scripts/run_full_verification.py`, and `scripts/run_test_matrix.py` to resolve the existing keys case-insensitively before updating them. For example: `path_key = next((k for k in env if k.upper() == "PATH"), "PATH")`.
- Add a brief Windows-specific note or command variant in the `README.md` and `v0_4_application_examples.md` (e.g., showing the `set PYTHONPATH=src;. && python ...` or PowerShell equivalent) to prevent user friction.
- Add `output_path.parent.mkdir(parents=True, exist_ok=True)` in `tests/baseline_integration_test.py` before writing the JSON benchmark file.

## Residual Risks
- The Windows native compilation hardcodes the LLVM `clang++.exe` path and relies on a specific `vcvars64.bat` path (`BuildTools`). While configurable via the `RTDL_VCVARS64` and `CXX` environment variables, users without this exact setup will encounter immediate build failures and have to manually specify these paths in their environment, which may increase adoption friction.
