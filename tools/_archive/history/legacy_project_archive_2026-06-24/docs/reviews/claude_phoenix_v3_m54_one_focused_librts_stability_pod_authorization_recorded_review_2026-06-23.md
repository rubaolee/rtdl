# Phoenix V3 M54 One Focused LibRTS Stability POD Authorization — External Claude Review

**Date:** 2026-06-23
**Reviewer:** Claude (claude-sonnet-4-6, external seat)
**Scope:** Bounded authorization review for exactly one focused LibRTS stability POD run using the M47/M48/M51 suite. This review does not re-audit M43–M52 debt (already paid by M53 2-AI consensus). It addresses only the M54 authorization question.

---

## Verdict

```
authorize_m47_one_focused_librts_stability_pod_run
```

Authorization token, valid for exactly one focused LibRTS stability run only:

```
M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED
```

---

## Explicit Non-Authorization Block

This authorization does **NOT** cover:

- **V3 release** — blocked; all-app Set-A/B gate still controls; release bar not cleared
- **All-app benchmark run** — blocked; no all-app POD packet reviewed
- **Broad paid POD campaign** — blocked; only one focused M47 run is authorized
- **Public speedup wording** — blocked
- **Broad V3-over-V2 claims** — blocked
- **V4 work** — blocked
- **Embedding** — blocked
- **C ABI** — blocked
- **True zero-copy claims** — blocked

Even a green result from the authorized run does not close a watch row. Green is a closure **candidate** only and requires a separate external review of the copied evidence before any watch row may be called closed.

---

## Answers to All Six Review Questions

### 1. Is the M47/M48/M51 suite ready for exactly one focused LibRTS stability POD run once real roots and Linux/POD Python paths are supplied?

**Yes**, with conditions met at execution time.

Code review of `scripts/v3_phoenix_m47_librts_stability_protocol.py` confirms:

- Default path: `if not bool(args.execute): return build_payload(..., status=STATUS_DRY_RUN)` — no benchmark subprocess is ever called in dry-run mode.
- Token gate: `if str(args.authorization_token) != AUTHORIZATION_TOKEN: raise SystemExit(...)` — this check precedes `execute_preflight` and `execute_schedule`, so no benchmark can be reached without the exact token string `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`.
- `validate_args` enforces `--v2-root` at execute time (`raise SystemExit("--v2-root is required for execution")`).
- `CLAIM_BOUNDARY` is a module-level dict with all values hardcoded to `False`. It is never modified at runtime. The output payload copies it literally, so no run outcome can set any authorization flag to True.
- Alternating order (`odd sample: v2_14 first; even sample: current first`) correctly controls cold-start drift for all 32 schedule rows (2 scenarios × 8 samples × 2 trees).
- Tree-specific PYTHONPATH isolation (`<root>/src:<root>`) added in M48 prevents cross-tree import bleed.
- Preflight failures on required checks propagate to the `run_errors` dict and force `STATUS_FAILED`; current OptiX metadata failures force the scenario to `red_failure_watch_row_open` through `classify_ratios`, not a spurious performance interpretation.

Green/Yellow/Red thresholds in `classify_ratios` are well-specified and match the M47 protocol document exactly. The M51 runbook dry-run evidence (`schedule_row_count=32, failed_check_count=0`) confirms the schedule structure is correct.

The two preconditions that must be met by the executor before any run starts are pre-execution runtime requirements, not implementation gaps. The code enforces them at execution time (`validate_args`, preflight required checks). The suite is otherwise complete.

### 2. Are the two M53 P1 items fully captured as pre-execution requirements?

**Yes**, and they are captured in three overlapping places.

**P1-1 (real V2.14 root):** The M54 call-for-review states "A real V2.14 root must be supplied; do not execute dry-run placeholder command lines containing `<v2-root-required-on-execute>`." The M51 runbook states "Do not infer V2.14 from the current tree. If a separate V2.14 tree is not present, stop and record blocked setup." The code enforces `--v2-root` as required for execution via `validate_args`.

**P1-2 (Linux/POD Python paths):** The M54 call-for-review states "Explicit Linux/POD Python paths must be supplied for both current and V2.14; do not use the local Windows `C:\Python311\python.exe` dry-run default." The M51 runbook states the executor must identify Python executables on the target machine before execution starts. The preflight runs `--current-python --version` and `--v2-python --version` as required checks (`"required": true`), so a missing or wrong Python path causes immediate preflight failure and halts the run before any benchmark is reached.

One nuance worth flagging: the M51 dry-run evidence (`summary.json` in `phoenix_v3_m51_librts_authorized_runbook_dry_run_20260623`) shows `"v2_root": "C:\\rtdl_v2_14_placeholder"` — a non-existent Windows placeholder path intentionally supplied to exercise the preflight plan. The preflight `cwd` fields contain Windows absolute paths from the local development machine. The M51 runbook correctly addresses this by requiring a fresh dry-run on the target machine before authorized execution, which regenerates all paths for the POD environment. The executor must not copy the M51 dry-run commands literally — they must re-run dry-run on the Linux/POD machine with real paths.

This is correctly specified in the M51 runbook ("Run this first on the target machine without `--execute`") and does not require any code change.

### 3. Does the M51 runbook require full evidence copy-back before interpretation?

**Yes**, explicitly and unambiguously.

M51 states:

> "Copy the entire output directory back into the current repo at the same relative path. The directory must include: `summary.json`; `README.md`; `preflight_*.stdout.txt`; `preflight_*.stderr.txt`; one stdout JSON and stderr text file for each measured command."

> "Do not copy back only the summary. Missing per-command evidence makes the run unreviewable."

> "If all scenarios are green closure candidates, still do not call the watch row closed until external review accepts the copied evidence."

The intake rules also require reading `summary.json` first and stopping before interpreting speed if any stop condition is present (`failed_check_count != 0`, wrong status, preflight failures, red scenarios, fixture/contract mismatches, missing current runner metadata, or any claim-boundary flag true).

Full copy-back is a hard gate before interpretation, not a recommendation.

### 4. Does the M52 authorization-surface audit confirm that only M47 token-gated execution is in scope for this request?

**Yes**.

M52's fixed-string scan over 126 files found `AUTHORIZATION_TOKEN` in exactly two active scripts:

- `scripts/v3_phoenix_m47_librts_stability_protocol.py` — token `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`; in scope for this request.
- `scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py` — token `M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED`; not in scope for this request and not authorized by any current review.

All other `v3_phoenix_*pod*` scripts are correctly classified as historical evidence tooling that may not be re-invoked as current execution authorization.

One standing limitation noted in M53 P2-2 and carried forward: the M52 scan is keyword-based (`pod|remote|runner|stability_protocol`). Future scripts with non-matching names would not appear in the scan. This is handled by the standing rule requiring new execution surfaces to add explicit token gates or runbooks before any paid run — not by the scan itself. This is not a P1 item for the current authorization.

### 5. If authorization is granted, is it limited to exactly one focused LibRTS stability run and no broader spend?

**Yes**.

The M54 call-for-review specifies the exact run scope:

- M47/M48 LibRTS stability protocol
- two scenarios (OptiX strict cold single-shot, Embree 32768 stress)
- eight paired samples each
- alternating V2.14/current order
- full preflight capture
- separate current and V2.14 roots
- explicit Linux/POD Python paths
- full copy-back of summary, README, per-command stdout/stderr, and preflight artifacts

The M54 call-for-review resource estimate (`0.5–1.5 hours, $0.13–$0.38`) is narrow and confirms this is a focused single run, not a campaign.

The code's `CLAIM_BOUNDARY` dict prevents the output packet from asserting any broader authorization regardless of what performance numbers are produced. The M51 runbook gates execution on the exact external verdict string. The intake rules require stopping before interpreting performance if any boundary is violated.

This authorization grants the token for one run only. Re-running, running with different scenarios or samples, or running any other script is not covered by this authorization.

### 6. Are there any P0/P1 findings that must be fixed before the one focused run?

**No P0 or P1 implementation findings. Two pre-execution executor requirements must be met (carried forward from M53).**

**Pre-execution requirements (not code bugs — must be met by executor):**

- **Req-1 (V2.14 root):** A real V2.14 tree must be present on the target Linux/POD machine. Run the M51 dry-run command on the target machine with the real `--v2-root` path. Confirm `failed_check_count=0` before proceeding to `--execute`.
- **Req-2 (Linux/POD Python paths):** Supply `--current-python` and `--v2-python` pointing to valid Python executables on the POD, not the Windows `C:\Python311\python.exe` default. The preflight will enforce these as required checks, so a wrong path fails loudly before any benchmark measurement.

**Observations that do not block authorization:**

- **Obs-1 (M51 dry-run paths):** The M51 dry-run summary.json contains Windows paths from the local development machine. The executor must not use these paths literally. A fresh dry-run on the target machine is required first, per M51 runbook.
- **Obs-2 (`--samples` cosmetic):** `validate_args` raises `SystemExit` if `--samples` is not 8, making the argument effectively non-configurable despite being parsed. This is safe (P2 carry-forward from M53).
- **Obs-3 (M52 scan keyword-based):** Standing rule for future scripts is adequate backstop (P2 carry-forward from M53).
- **Obs-4 (`validate_args` does not validate Python paths):** The code does not verify that `--current-python` and `--v2-python` exist or are Linux executables. However, the preflight step catches this immediately as a required check, halting the run before any benchmark is reached. Acceptable.

None of these observations are P0 or P1. The code is correct as implemented. The pre-execution requirements are operational, not engineering, gaps.

---

## Code Audit Summary

| Check | Result |
| --- | --- |
| Default dry-run path enforced | Pass — `if not bool(args.execute): return build_payload(... status=STATUS_DRY_RUN)` |
| Token gate before any execution | Pass — `if str(args.authorization_token) != AUTHORIZATION_TOKEN: raise SystemExit(...)` precedes preflight and schedule |
| `--v2-root` enforced at execute time | Pass — `validate_args` raises `SystemExit("--v2-root is required for execution")` |
| `CLAIM_BOUNDARY` hardcoded false | Pass — module-level dict, never mutated at runtime |
| Alternating order (odd: v2_14 first) | Pass — `order = ("v2_14", "current") if sample % 2 == 1 else ("current", "v2_14")` |
| Tree-specific PYTHONPATH isolation | Pass — `env_for_root(root)` prefixes `<root>/src:<root>` |
| Metadata failure forces red | Pass — `current_metadata_failures` non-empty → `"red_failure_watch_row_open"` |
| Green requires all 7 conditions | Pass — `classify_ratios` checks all-geo ≥0.95, median ≥0.95, pass_count ≥7, min ≥0.90, stripped-geo ≥0.98, stderr empty, metadata ok |
| Green still requires external review | Pass — label is `"green_closure_candidate_requires_external_review"`, not a closed verdict |
| Dry-run test suite 5/5 pass | Pass — M47 (5 tests), M48 (15 tests), M51 (14 tests) all OK per evidence |
| Full V3 rebuild 638 tests OK | Pass — 124 modules, 638 tests per M51 evidence |
| M54 gate test 3/3 assertions pass | Pass — all required input files exist; packet text contains all required phrases |

---

## Authorization Scope Boundaries

This authorization covers:

- One execution of `scripts/v3_phoenix_m47_librts_stability_protocol.py` with `--execute --authorization-token M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`
- Two scenarios: `optix_cold_single_shot` and `embree_32768_stress`
- Eight paired samples per scenario, alternating order
- Full preflight capture on the target machine
- Full copy-back of all evidence before interpretation
- External review of the copied evidence required before any watch-row status change

This authorization explicitly does **not** cover:

- A second or subsequent run of M47
- Any modification of scenario parameters, sample count, or seed
- All-app benchmark run
- V3 release
- Public speedup wording
- Broad V3-over-V2 claims
- V4 work, embedding, C ABI, or true zero-copy claims
- Interpretation of results without full copy-back and intake rules
- Calling any watch row closed without a further external review of the copied evidence
