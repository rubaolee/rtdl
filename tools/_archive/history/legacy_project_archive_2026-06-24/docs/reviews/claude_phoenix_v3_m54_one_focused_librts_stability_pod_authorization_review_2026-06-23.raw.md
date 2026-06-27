---

# Phoenix V3 M54 One Focused LibRTS Stability POD Authorization — External Claude Review

**Date:** 2026-06-23
**Reviewer:** Claude (claude-sonnet-4-6, external seat)
**Scope:** Bounded authorization review for exactly one focused LibRTS stability POD run using the M47/M48/M51 suite. Does not re-audit M43–M52 debt (already paid by M53 2-AI consensus).

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

- **V3 release** — blocked
- **All-app benchmark run** — blocked
- **Broad paid POD campaign** — blocked
- **Public speedup wording** — blocked
- **Broad V3-over-V2 claims** — blocked
- **V4 work** — blocked
- **Embedding** — blocked
- **C ABI** — blocked
- **True zero-copy claims** — blocked

Even a green result does not close a watch row. Green is a closure **candidate** only and requires a separate external review of the copied evidence.

---

## Answers to All Six Review Questions

### 1. Is the M47/M48/M51 suite ready for exactly one focused LibRTS stability POD run once real roots and Linux/POD Python paths are supplied?

**Yes**, with conditions met at execution time.

Code audit of `scripts/v3_phoenix_m47_librts_stability_protocol.py` confirms:

- Default dry-run path enforced: `if not bool(args.execute): return build_payload(..., status=STATUS_DRY_RUN)` — no benchmark subprocess is reachable.
- Token gate: `if str(args.authorization_token) != AUTHORIZATION_TOKEN: raise SystemExit(...)` precedes `execute_preflight` and `execute_schedule`, so no benchmark can be reached without the exact string `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`.
- `validate_args` enforces `--v2-root` at execute time.
- `CLAIM_BOUNDARY` is a module-level dict hardcoded all-False, never mutated at runtime. No run outcome can set any authorization flag to True.
- Alternating order (odd sample: v2_14 first; even sample: current first) produces all 32 schedule rows correctly across both scenarios.
- Tree-specific PYTHONPATH isolation (`<root>/src:<root>`) from M48 prevents cross-tree import bleed.
- Current metadata failures force `red_failure_watch_row_open`, not a spurious performance interpretation.

Green/Yellow/Red thresholds in `classify_ratios` match the M47 protocol document exactly. M51 dry-run evidence confirms `schedule_row_count=32, failed_check_count=0`. The suite is operationally complete.

### 2. Are the two M53 P1 items fully captured as pre-execution requirements?

**Yes**, captured in three overlapping places.

**P1-1 (real V2.14 root):** Stated in M54 call-for-review ("A real V2.14 root must be supplied"), in M51 runbook ("If a separate V2.14 tree is not present, stop and record blocked setup"), and enforced at code level by `validate_args`.

**P1-2 (Linux/POD Python paths):** Stated in M54 call-for-review ("Explicit Linux/POD Python paths must be supplied"), in M51 runbook (executor must identify Python paths before execution), and enforced by preflight required checks (`current_python_version` and `v2_python_version` both `"required": true`).

One nuance worth flagging: the M51 dry-run summary.json shows `"v2_root": "C:\\rtdl_v2_14_placeholder"` — a Windows placeholder used to exercise the preflight plan locally. The M51 runbook's requirement to run a fresh dry-run on the target machine before authorized execution correctly handles this. The executor must not copy the M51 dry-run commands literally.

### 3. Does the M51 runbook require full evidence copy-back before interpretation?

**Yes**, explicitly.

M51 states: "Copy the entire output directory back... The directory must include: summary.json; README.md; preflight_*.stdout.txt; preflight_*.stderr.txt; one stdout JSON and stderr text file for each measured command." And: "Do not copy back only the summary. Missing per-command evidence makes the run unreviewable." And: "If all scenarios are green closure candidates, still do not call the watch row closed until external review accepts the copied evidence."

Full copy-back is a hard gate before interpretation, not a recommendation.

### 4. Does the M52 authorization-surface audit confirm that only M47 token-gated execution is in scope for this request?

**Yes**.

M52's fixed-string scan over 126 files found `AUTHORIZATION_TOKEN` in exactly two active scripts: M47 (`M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`, in scope for this request) and M50 (`M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED`, not in scope and not authorized). All other `v3_phoenix_*pod*` scripts are correctly classified as historical evidence tooling.

Standing P2 carry-forward: the scan is keyword-based; future scripts with non-matching filenames must still add explicit token gates per the standing rule.

### 5. If authorization is granted, is it limited to exactly one focused LibRTS stability run and no broader spend?

**Yes**.

The M54 call-for-review specifies exact run scope: M47/M48 protocol, two scenarios, eight paired samples each, alternating order, full preflight, separate roots, explicit Linux/POD Python paths, full copy-back. Resource estimate ($0.13–$0.38) is narrow. `CLAIM_BOUNDARY` is hardcoded all-False, preventing the output packet from asserting any broader claim regardless of performance results. The M51 runbook gates execution on the exact external verdict string. Re-running, changing parameters, or running any other script is not covered by this authorization.

### 6. Are there any P0/P1 findings that must be fixed before the one focused run?

**No P0 or P1 implementation findings.** Two pre-execution executor requirements (not code bugs) must be met:

- **Req-1:** Supply a real V2.14 tree on the target machine via `--v2-root`. Run M51 dry-run on target machine first to confirm `failed_check_count=0`.
- **Req-2:** Supply `--current-python` and `--v2-python` pointing to valid Linux/POD Python executables. Do not use the `C:\Python311\python.exe` default. Preflight enforces these as required checks.

Non-blocking observations only: `--samples` cosmetic no-op (M53 P2-3); M52 keyword-scan limitation (M53 P2-2); `validate_args` does not pre-validate Python paths (mitigated by preflight required checks).

---

## Code Audit Table

| Check | Result |
|---|---|
| Default dry-run path enforced | Pass |
| Token gate before any execution | Pass |
| `--v2-root` enforced at execute time | Pass |
| `CLAIM_BOUNDARY` hardcoded all-False | Pass |
| Alternating order (odd: v2_14 first) | Pass |
| Tree-specific PYTHONPATH isolation | Pass |
| Metadata failure forces red | Pass |
| Green requires all 7 conditions | Pass |
| Green label is closure-candidate only | Pass |
| M47 dry-run test suite (5 tests OK) | Pass |
| Full V3 rebuild (638 tests OK) | Pass |
| M54 gate test (3 assertions) | Pass |

---

## Authorization Scope

**In scope:** One execution of `scripts/v3_phoenix_m47_librts_stability_protocol.py` with `--execute --authorization-token M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`, two scenarios, eight paired samples, alternating order, full preflight, full copy-back, intake rules applied, external review required before any watch-row status change.

**Out of scope:** Any second run, parameter changes, all-app run, V3 release, public speedup wording, broad V3-over-V2 claims, V4/embedding/C ABI/true zero-copy work, watch-row closure without further external review.

---

Review recorded to `docs/reviews/claude_phoenix_v3_m54_one_focused_librts_stability_pod_authorization_recorded_review_2026-06-23.md`.
