I now have all the information needed to write the review.

---

## Verdict

**ACCEPT** — for the measured `COLLECT_K_BOUNDED` native parity scope on the three recorded environments. The package is suitable as bounded parity evidence for the v1.5.1 `COLLECT_K_BOUNDED` promotion track. No public promotion, speedup, or zero-copy authorization is granted.

---

## Accepted Evidence

**Scope.** Four deterministic parity cases covering the full capacity spectrum: `empty_zero_capacity`, `exact_fit_two_rows`, `one_short_fail_closed_overflow`, `zero_capacity_positive_fail_closed_overflow`. Row width 2 (left/right polygon-id pairs) on all runs.

**Contract integrity.**
- `stable_promotion_authorized=False` is machine-enforced in `validate_v1_5_1_collect_k_bounded_contract` (`src/rtdsl/v1_5_1_collect_k_bounded.py:97`); it cannot be silently flipped.
- `truncation_allowed`, `partial_result_on_overflow_allowed`, and `score_or_reduction_after_overflow_allowed` are all validated False by the same function.
- `complete_candidate_coverage_required=True` is also machine-enforced and then re-checked by `validate_collect_k_bounded_result` on every native call.

**Fail-closed overflow.** Both `embree_runtime.py` (~line 872) and `optix_runtime.py` (~line 3067) raise `RuntimeError` with the literal tag `failure_mode=fail_closed_overflow` when the native overflow flag is non-zero, before any partial result is returned. The Python reference (`collect_k_bounded_rows`) raises before materializing any return dict. The parity harness catches these on the first `except RuntimeError` branch and requires the tag string to be present; a plain RuntimeError without the tag is recorded as `fail`.

**Canonical ordering and metadata.** Both wrappers `sorted()` the candidate pair list before passing it to `collect_k_bounded_rows`, and the reference normalizes and deduplicates before the capacity check. `validate_collect_k_bounded_result` re-canonicalizes the rows and cross-checks `valid_count`, `emitted_count`, and `candidate_id_rows` in the final result, so metadata consistency is structurally enforced, not assumed.

**Environment outcomes.**
| Environment | Backend | Required | pass/fail/skip |
|---|---|---|---|
| Windows 10 `9813a0b7` | embree | no | 4/0/0 |
| Windows 10 `9813a0b7` | optix | no | 0/0/4 (no driver — expected) |
| Linux 6.17 `9813a0b7` | embree | **yes** | 4/0/0 — ACCEPTED |
| NVIDIA pod RTX A4500 driver 550.127.05 `9813a0b7` | optix | **yes** | 4/0/0 — ACCEPTED |

All three runs are on the same git HEAD (`9813a0b7`). OptiX is correctly skipped on Windows (optional, not required) and correctly exercised as a required backend on the NVIDIA pod. No required-backend skips in the authoritative runs.

**Claim boundary.** All three generated reports, the contract file, and the harness's `claim_boundary` field consistently state: not a public primitive promotion, not a performance claim, not a zero-copy claim.

---

## Blockers

None.

---

## Notes

1. **Linux/NVIDIA artifact "Files" section points to Windows paths.** The "Files" section in `goal1416_v1_5_1_collect_k_native_parity_linux_embree_2026-05-06.md` and the NVIDIA pod report both list the generic Windows-generated artifact paths (`goal1416_v1_5_1_collect_k_native_parity_2026-05-06.json`). The multi-environment summary (`multi_env_2026-05-06.md`) correctly enumerates all three platform-specific artifacts, so this is cosmetic and does not affect evidentiary validity.

2. **`_is_backend_unavailable` includes broad fragments.** The terms `"optix"` and `"cuda"` in `_is_backend_unavailable` could theoretically match a non-unavailability exception message. However, the `except RuntimeError` branch fires first and the availability check only runs on `Exception` (non-RuntimeError) paths, so overflow signals cannot be misclassified as skips.

3. **Double capacity check in wrappers.** After confirming the native overflow flag is clear, each wrapper calls `collect_k_bounded_rows(..., k=capacity)` — this re-validates capacity a second time in Python. This is redundant but harmless, and it ensures the Python reference contract is always traversed even on the native path.

4. **Windows OptiX skip is non-authoritative by design.** The Windows run was correctly invoked without `--require-backend optix`, so the four OptiX skips did not affect its `accepted=True` status. OptiX parity evidence comes solely from the NVIDIA pod run, which carried the required-backend flag.
