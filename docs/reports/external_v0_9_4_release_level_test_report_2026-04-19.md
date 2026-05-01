# External Release-Level Test Report: RTDL v0.9.4

## 1. Verdict
**`BLOCK`**

## 2. Environment
- **OS:** macOS (Apple Silicon)
- **Compiler:** Apple clang version 15.0.0 (clang-1500.1.0.2.5) / `xcrun clang++`
- **Native Context:** Apple Metal / Apple MPS
- **Skipped Environments:** Linux (NVIDIA GPU), OptiX, Vulkan, HIP RT, PostgreSQL (Platform limitations during this specific audit sweep).

## 3. Checkout
- **Repository Path:** `/Users/rl2025/rtdl_python_only`
- **Commit Hash:** `a64ced4b` (Latest `main` after second fix attempt)
- **Tag Status:** `main` tracking `v0.9.4` context
- **Status:** Clean

## 4. Commands Run

### Portable Tests (macOS)
| Command | Status | Notes |
| :--- | :--- | :--- |
| `python3 -m unittest discover -s tests -p '*_test.py' -v` | 🔴 **FAILED** | 1178 tests run. 0 Failures, 1 Error, 175 Skipped. |
| `python3 scripts/goal497_public_entry_smoke_check.py` | 🟢 **PASSED** | Exit Code: 0 |
| `python3 scripts/goal515_public_command_truth_audit.py` | 🟢 **PASSED** | Exit Code: 0 |

### Apple Native Tests (macOS)
| Command | Status | Notes |
| :--- | :--- | :--- |
| `make build-apple-rt` | 🟢 **PASSED** | Clean `dylib` compilation. |
| `python3 examples/rtdl_apple_rt_closest_hit.py` | 🟢 **PASSED** | Correct parity matches with Python CPU reference. |
| `python3 -m unittest tests.goal582_apple_rt_full_surface_dispatch_test -v` | 🟢 **PASSED** | 4/4 passed. All 18 predicates mapped safely. |
| `python3 -m unittest tests.goal617...` (DB/Graph tests) | 🟢 **PASSED** | 26/26 passed. Metal compute DB queries match reference. |

## 5. Correctness Findings
- **Apple RT Capabilities:** The Apple RT execution slice is surprisingly immaculate. The full 18-surface dispatch, bounding DB workloads through compute, and closest-hit verifications demonstrate robust correctness natively on Apple Silicon.
- **Failures:** The latest commit (`a64ced4b`) successfully fixed the `goal207` floating-point precision mismatch and properly skipped native compilation blockers in `goal17`, `goal19`, and `report_smoke`. However, a solitary compilation exception `CalledProcessError` remains inside `tests.goal15_compare_test.py`, crashing the required base test sweep.

## 6. Documentation Findings
- **Honesty Constraints:** The documentation complies perfectly with the strict formatting requirements.
    - `docs/backend_maturity.md` correctly segregates Apple VPS vs. Metal compute acceleration paths explicitly.
    - `capability_boundaries.md` makes no falsely advertised claims about RTDL existing as a full DBMS or renderer.
- **Stale Docs/Code:** The `goal532_v0_8_release_authorization_test` fails specifically because it asserts the public docs identify `v0.9.1` as the current release. The test suite was not properly version-bumped to `v0.9.4`.

## 7. Performance Findings
No detailed multi-node performance profiling was authorized or run requested within this minimum suite on macOS.

## 8. Release-Flow Findings
The tag preparation and overarching documentation flows correctly identify `v0.9.4` as having absorbed the internal `v0.9.2` and `v0.9.3` features without pushing them publicly.

## 9. Blockers

1. **C++ Compilation Error Trailing Exception**
   - **File:** `tests/goal15_compare_test.py` -> `test_native_compare_matches_rtdl_on_small_uniform_cases`
   - **Reproduction:** Run `python3 -m unittest discover`
   - **Expected:** C++ helper modules compile correctly or the test gracefully skips if Native dependencies (`-lgeos_c`) are missing (as successfully implemented in `goal17`, `goal19`, etc.).
   - **Actual:** 1 explicit `ERROR`. Throws `subprocess.CalledProcessError: Command '['c++', '-std=c++17', ... '-lgeos_c' ... ] returned non-zero exit status 1`.
   - **Severity:** Critical (Crashes minimum portable verification suite pipeline).

*(Note: The stale `goal532` version assertion, external baseline float mismatch, and the other 4 compilation `ERROR`s were successfully patched by commit `a64ced4b`... but this final `ERROR` block persists).*

## 10. Non-Blocking Notes
- The separation of native backends under `src/native/` works cleanly for `rtdl_apple_rt.mm`. The module imports natively without polluting the python tree.
