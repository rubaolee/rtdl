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
- **Commit Hash:** `b99d6eac0e69dcac4f4c492a4a6221d29d64d092`
- **Tag Status:** `v0.9.4` (detached HEAD)
- **Status:** Clean

## 4. Commands Run

### Portable Tests (macOS)
| Command | Status | Notes |
| :--- | :--- | :--- |
| `python3 -m unittest discover -s tests -p '*_test.py' -v` | 🔴 **FAILED** | 1178 tests run. 2 Failures, 5 Errors, 171 Skipped. (See Blockers section). |
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
- **Failures:** The `v0.9.4` tagged pipeline is fundamentally broken on a fresh checkout due to hardcoded C++ compilation commands in the tests omitting required `-I`/`-L` dependency paths (specifically `geos_c`) on the standard macOS rollout, resulting in 5 cascading compilation `CalledProcessError` exceptions.

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

1. **Stale Release Assertion Test**
   - **File:** `tests/goal532_v0_8_release_authorization_test.py`
   - **Reproduction:** Run `python3 -m unittest discover`
   - **Expected:** Test gracefully understands `v0.9.4` is the new release boundary.
   - **Actual:** `FAIL: test_public_docs_identify_v091_as_current_release_and_v08_as_released_layer`. Test asserts `v0.9.1` is still current.
   - **Severity:** High (Release state paradox).

2. **C++ Compilation Errors in Compare Tests**
   - **File:** `tests/goal15_compare_test.py`, `goal17_prepared_runtime_test.py`, `goal19_compare_test.py`, `report_smoke_test.py`
   - **Reproduction:** Run `python3 -m unittest discover`
   - **Expected:** C++ helper modules compile correctly against Embree/GEOS on standard macOS.
   - **Actual:** 5 explicit `ERROR`s throwing `subprocess.CalledProcessError: Command '['c++', '-std=c++17', ... '-lgeos_c' ... returned non-zero exit status 1`.
   - **Severity:** Critical (Breaks base validation pipeline entirely).

3. **External Baseline Failure**
   - **File:** `tests/goal207_knn_rows_external_baselines_test.py`
   - **Actual:** `FAIL: test_natural_earth_case_runs_through_fake_scipy_baseline`. Yields a 652-character diff error.
   - **Severity:** High.

## 10. Non-Blocking Notes
- The separation of native backends under `src/native/` works cleanly for `rtdl_apple_rt.mm`. The module imports natively without polluting the python tree.
