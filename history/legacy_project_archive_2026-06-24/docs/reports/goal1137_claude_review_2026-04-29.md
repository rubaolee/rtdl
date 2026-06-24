# Goal1137 Cloud GEOS Bootstrap Preflight — Claude Review

Date: 2026-04-29
Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

---

## What Was Reviewed

- `scripts/goal763_rtx_cloud_bootstrap_check.py`
- `docs/rtx_cloud_single_session_runbook.md`
- `tests/goal763_rtx_cloud_bootstrap_check_test.py`
- `tests/goal829_rtx_cloud_single_session_runbook_test.py`
- `docs/reports/goal1137_cloud_geos_bootstrap_preflight_2026-04-29.md`

---

## Findings

### Correctness

**`_geos_preflight()`** (script lines 101–125) probes three independent conditions:

1. `shutil.which("pkg-config")` — confirms the binary exists
2. `pkg-config --libs geos` / `pkg-config --libs geos_c` — confirms usable package metadata exists
3. `ctypes.util.find_library("geos_c")` — confirms the dynamic library is on the loader path

All three are checked as preflight blockers only in non-dry-run mode (script lines 199–209). The dry-run path still calls `_geos_preflight()` for metadata emission but suppresses blocker injection, so `status: ok` is correctly returned in dry-run even when GEOS is absent locally.

The blocker-to-fix mapping is correct: `apt-get install -y libgeos-dev pkg-config` resolves all three conditions simultaneously. The install hint is embedded in the GEOS preflight data structure so it appears in the output JSON alongside the blockers.

**Runbook placement** is correct: the `apt-get` install step (runbook lines 130–133) appears *before* the `goal763_rtx_cloud_bootstrap_check.py` invocation (lines 136–141), so an operator who follows the runbook in order will not hit the GEOS gate. If they skip the install step, the bootstrap check will still catch it and report `needs_attention`.

### Test Coverage

`test_missing_geos_is_preflight_blocker` monkey-patches `_geos_preflight` to return fully-absent GEOS state, calls `run_check(dry_run=False, ...)`, and asserts all three blockers appear plus `status == "needs_attention"`. This directly covers the primary failure scenario.

`test_runbook_uses_bootstrap_and_artifact_audit` asserts the exact error string (`cannot find -lgeos_c`), the explanation (`native CPU/oracle reference path`), and the package names (`libgeos-dev`, `pkg-config`) all appear in the runbook. This guards against the runbook drifting away from the documented fix.

### Overclaiming Assessment

No overclaiming detected:

- The script output includes an explicit `boundary` field: *"does not run performance benchmarks and does not authorize RTX speedup claims."*
- The runbook "Claim Boundary" section (lines 488–491) is unchanged and still reads: *"This runbook collects evidence. It does not authorize public RTX speedup claims."*
- The Goal1137 report (the input document) is correctly scoped: *"bootstrap reliability fix … does not run benchmarks … does not authorize release or public RTX speedup claims."*
- No new benchmark results, speedup ratios, or public wording changes are introduced anywhere in the diff.

### Minor Observations (Non-Blocking)

**Triple-blocker redundancy**: When `pkg-config` is absent, all three GEOS blockers fire simultaneously. The second blocker ("missing GEOS pkg-config package geos or geos_c") is technically redundant when `pkg-config` itself is missing — no packages can be probed. This is factually accurate but slightly noisy. The unified install command fixes all three, so operators are not misled. This is a UX observation, not a defect.

**`pkg-config --libs` vs `--exists`**: Using `--libs` as the probe is stricter than `--exists` (it also validates that linker flags resolve), which is slightly more conservative than needed for a pure existence check. This is harmless and defensible.

---

## Summary

The implementation is narrowly scoped to pod bootstrap reliability. It adds GEOS/pkg-config preflight checks that correctly surface the `cannot find -lgeos_c` class of failures before paid workload execution begins, gates all blockers on non-dry-run mode, documents the install step in the correct runbook position, and does not introduce any benchmark claims or release assertions. Tests cover the primary failure path at the unit level and the runbook at the text-assertion level.
