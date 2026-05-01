# Goal1031 Claude Review

Date: 2026-04-26
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

Files reviewed:
- `scripts/goal1031_local_baseline_smoke_runner.py`
- `tests/goal1031_local_baseline_smoke_runner_test.py`
- `docs/reports/goal1031_local_baseline_smoke_2026-04-26.md`
- `docs/reports/goal1031_local_baseline_smoke_2026-04-26.json`

---

## Criterion 1: Smoke-scale vs. same-scale baseline evidence

**Result: Honest and correct.**

The runner draws the distinction at every level of the stack:

- The `boundary` field is written into both the JSON root and rendered as the first body paragraph of the markdown, before any table or result. It reads: _"Smoke mode intentionally scales --copies down and only checks local command health. It is not same-scale baseline evidence and does not authorize speedup claims."_ The full-mode variant carries an analogous disclaimer.
- `SMOKE_COPIES = "50"` is the single source of truth for the downscale factor. `_scaled_command()` rewrites only `--copies`, leaving all other flags intact, so the command shape is representative even if the scale is not.
- Both the JSON and the markdown record `"mode": "smoke"` at the top level and on every row. `copies: 50` is confirmed in each `json_summary`.
- No elapsed-time comparisons across entries or backends appear in either artifact.

One inconsequential redundancy: `_scaled_command` iterates searching for `"--copies"` only, which is correct for the current manifest but would silently ignore other hypothetical scale flags. Not a problem today.

---

## Criterion 2: Optional SciPy gaps

**Result: Handled correctly, non-blocking, and fully surfaced.**

Detection logic (`_command_status`, line 63–68):

```python
if "--backend" in command and "scipy" in command and "SciPy is not installed" in stderr:
    return "optional_dependency_unavailable"
```

- Requires all three conditions — wrong backend, non-zero exit, and the canonical error string — so the gap cannot be masked by an unrelated scipy failure.
- The `"scipy" in command` list-membership check is a coarse string scan; if a flag value ever contained the substring `scipy` for a non-scipy backend it could false-positive. The current manifest makes this impossible, but a comment noting the intent (match backend value `"scipy"`) would help future editors.

Classification chain is correct:
- Failed commands that are `optional_dependency_unavailable` are separated from `failed` at both the per-entry level (line 113–115) and the report level (line 136–138).
- Exit code path (line 212): `return 0 if payload["status"] in {"ok", "ok_with_optional_dependency_gaps"} else 1` — SciPy gaps do not fail the runner.

Evidence in the JSON:
- `service_coverage_gaps` and `event_hotspot_screening` both show `"status": "optional_dependency_unavailable"` for their scipy commands, `returncode: 1`, `stderr_tail` with the real `RuntimeError`, and `json_parse_status: "not_json"`. Consistent and self-auditable.
- `outlier_detection` and `dbscan_clustering` ran their scipy commands cleanly (returncode 0). The runner captures the real environment state without hiding the inconsistency or flattening it into a single pass/fail.

Test coverage: `test_scipy_missing_is_optional_dependency_gap` covers both the positive case (scipy unavailable → `optional_dependency_unavailable`) and the negative case (non-scipy failure → `"failed"`). Complete.

---

## Criterion 3: Speedup claims

**Result: No speedup claims. No timing comparisons. Boundary language is unambiguous.**

- The `boundary` string contains the literal phrase "does not authorize speedup claims" in both smoke and full mode variants.
- `elapsed_sec` is recorded per command but the markdown table only shows "Elapsed total (s)" per entry — no per-backend breakdown and no ratio computation anywhere.
- No language in the markdown or JSON uses "faster", "speedup", "Nx", or any comparative performance framing.
- The JSON `optix_performance` note inside the `service_coverage_gaps` embree stdout says: _"rows mode is not the RT-core claim path"_ — further reinforcing that the smoke run makes no acceleration claims.

---

## Minor issues (non-blocking)

**1. `env` strips PATH (line 84).**

```python
env={**dict(), **{"PYTHONPATH": "src:."}}
```

`dict()` is an empty dict, so the subprocess receives only `PYTHONPATH` — no `PATH`, `HOME`, `TMPDIR`, or any inherited variable. `subprocess.run` with an explicit `env` completely replaces the process environment. The commands run successfully because macOS uses a POSIX default PATH (`/usr/bin:/bin`) when `PATH` is unset, and `python3` lives in `/usr/bin`. This is fragile: a virtualenv, Homebrew, or pyenv install of Python would not be found. The safe fix is `env={**os.environ, "PYTHONPATH": "src:."}`.

**2. `test_report_selects_only_ready_entries_by_default` tests the manifest, not the report (lines 46–50).**

```python
manifest = module.build_manifest()
ready = [entry for entry in manifest["entries"] if entry["local_status"] == "baseline_ready"]
self.assertEqual(len(ready), 4)
```

This verifies the manifest count, not that `build_report(include_partial=False)` excludes partial entries. The `include_partial` default path is untested through `build_report`. The test name is misleading. Should call `build_report` or be renamed.

**3. Hardcoded output paths in `main()` (lines 204–205).**

`--output-json` and `--output-md` default to the 2026-04-26 filenames. Running the script without `--output-json` on a future date will overwrite the archived evidence. Not a correctness issue for this run but worth noting.

---

## Summary

| Criterion | Result |
|---|---|
| Smoke-scale vs. baseline evidence honestly distinguished | Pass |
| Optional SciPy gaps handled correctly and non-blocking | Pass |
| No speedup claims | Pass |
| Minor issues | 3 (non-blocking) |

**ACCEPT.** The runner is honest about what smoke mode can and cannot claim, correctly quarantines SciPy unavailability without failing the run, and makes no performance claims. The `env`/PATH fragility is the most actionable follow-up item.
