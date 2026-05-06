I have all the material I need. Here is the independent review:

---

## Verdict

**ACCEPT**

The Goal1417 v1.5.1 `COLLECT_K_BOUNDED` benchmark package is suitable as bounded collection benchmark evidence for the measured scope. No public primitive promotion, speedup wording, or zero-copy claims are made anywhere in the package.

---

## Accepted Evidence

**Harness correctness**
- `scripts/goal1417_v1_5_1_collect_k_benchmark.py` drives `polygon_pair_overlap_area_rows_cpu` as the ground truth for expected candidate rows and sets capacity to exactly `len(expected_rows)` per scale — consistent with the declared `capacity_policy`.
- Parity checks (`candidate_id_rows`, `valid_count`, `capacity`, `overflowed is False`, `complete_candidate_coverage is True`) are applied to the last result after each timing loop; no timing path bypasses contract validation.
- The `claim_boundary` field is injected into both the JSON artifact and rendered Markdown by `run_benchmark_package`, and the test `test_markdown_keeps_no_claim_boundary` asserts "not a speedup claim" is present in all rendered output.

**Contract integrity**
- `src/rtdsl/v1_5_1_collect_k_bounded.py` holds `stable_promotion_authorized = False` and `claim_boundary` containing "not yet public promotion, not a Jaccard-specific or polygon-specific engine path, and not a performance or zero-copy claim." `validate_v1_5_1_collect_k_bounded_contract` enforces these fields on every call.
- The benchmark's test suite covers: fake-backend acceptance, required-backend skip rejection, row-mismatch rejection, and Markdown claim-boundary preservation.

**Environment coverage**
- **Windows** (`8b8332dd`, Python 3.11.9): python_reference pass=3, embree pass=3, optix skipped=3 (no `librtdl_optix`). Correctly labeled `skipped`; no OptiX claim is drawn from Windows.
- **Linux Embree** (`8b8332dd`, Python 3.12.3, `--require-backend embree`): embree pass=3, package accepted.
- **NVIDIA pod OptiX** (`8b8332dd`, Python 3.11.10, `--require-backend optix`): optix pass=3, package accepted.
- All three runs share the same git HEAD; no version skew.
- Timing figures are reported as raw same-contract timing observations only. The multi-env summary makes no relative speedup claim between backends.

**Prior parity baseline**
- The three-AI Goal1416 consensus (`ACCEPT`, no blockers) establishes that the native Embree and OptiX paths produce parity-correct `COLLECT_K_BOUNDED` results. Goal1417 builds on that settled baseline and adds timing measurement without weakening the parity checks.

---

## Blockers

None.

---

## Notes

- **Cosmetic file-name issue (non-blocking):** The `Files` sections in the Linux Embree artifact (`goal1417_v1_5_1_collect_k_benchmark_linux_embree_2026-05-06.md`) and NVIDIA pod artifact (`goal1417_v1_5_1_collect_k_benchmark_nvidia_pod_optix_2026-05-06.md`) list the generic Windows artifact file names rather than their own environment-specific paths. The multi-environment summary correctly records the actual saved paths, so the evidence is not invalidated. This is the same pattern noted in the Goal1416 consensus.
- **Embree scaling on Linux:** At `copies=64`, Embree median (0.009635 s) is within ~0.3 % of python_reference (0.009666 s). This is an honest observation with no speedup framing; nothing to correct.
- **OptiX at small scale:** OptiX median at `copies=1` (0.000731 s) is slower than python_reference (0.000185 s) on the NVIDIA pod, likely due to GPU dispatch overhead at small work sizes. The report does not misrepresent this; both values are recorded accurately.
- This review does not authorize public promotion of `COLLECT_K_BOUNDED`, speedup wording, or zero-copy wording.
