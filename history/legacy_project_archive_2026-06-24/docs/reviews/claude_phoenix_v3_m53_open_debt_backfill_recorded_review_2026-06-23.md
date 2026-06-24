I now have all required materials. Here is the complete M53 review.

---

# Phoenix V3 M53 Open Claude Debt Backfill ΓÇö External Claude Review

**Date:** 2026-06-23  
**Reviewer:** Claude (claude-sonnet-4-6, external seat)  
**Scope:** Bounded debt-backfill review only. This review covers M43ΓÇôM52 discrete milestone debt. It does not re-audit the M44 goal-completion audit (already paid by saved 3-AI consensus).

---

## Overall Verdict

```
accept_m53_open_debt_backfill_no_authorization_continue_m54
```

All ten open debt items are technically sound, correctly non-authorizing, internally consistent with the prior evidence trail, and supported by adequate documentation. The engineering work M43ΓÇôM52 represents disciplined bounded runtime-trunk progress with no POD spend, no release moves, two new fail-closed execution gates, and a hardened LibRTS protocol ready for external authorization in a separate future packet.

---

## Per-Debt Verdicts

```
M43: accept
M44-scorecard: accept
M45: accept
M46: accept
M47: accept
M48: accept
M49: accept
M50: accept
M51: accept
M52: accept
```

---

## Findings by Severity

### P1 ΓÇö Must resolve before any LibRTS focused POD run proceeds

**P1-1: M47 dry-run was generated without a V2.14 root.**

The saved `summary.json` shows `"v2_root": null`. V2.14 tree command entries in the schedule contain the placeholder path `<v2-root-required-on-execute>` rather than a real path. This is correct behavior for a dry-run (no V2.14 repo is needed to plan the schedule), but it means the saved schedule cannot be used as a literal copy-paste command list for execution. Code enforces this correctly at `validate_args` (`raise SystemExit("--v2-root is required for execution")`), but the executor must supply a real V2.14 root when invoking with `--execute`. The M51 runbook already states this requirement. **Before any authorized run: verify a real V2.14 tree is present on the target machine and confirm `--v2-root` points to it. Do not execute from the dry-run schedule literally.**

**P1-2: M47 `--current-python` defaults to the Windows path `C:\Python311\python.exe`.**

The dry-run evidence captures the local Windows Python as the default. When executing on a Linux/RTX cloud POD, this path will not exist and will cause an immediate failure if not overridden. The M51 runbook requires the executor to identify both Python paths on the target machine before execution, which covers this. **Before any authorized run: pass explicit `--current-python` and `--v2-python` paths matched to the POD environment.**

These are pre-execution checklist items, not implementation bugs. They do not block the M53 backfill verdict, but they must be resolved before the M47 token is authorized.

### P2 ΓÇö Minor observations

**P2-1: M43 wall regression on original CuPy run (0.879x vs legacy wall) is correctly attributed to validate-at-prepare overhead, but the `--trust-row-offsets` mode is tested only on generated/pre-validated data in this local run.**

The explanation is technically sound and the explicit flag prevents silent bypass. However, the claim that the trusted-offsets mode will be safe in production needs to be re-verified when real benchmark app data is used. This is a carry-forward note, not a blocker for M43's bounded local-run classification.

**P2-2: M52 surface scan uses filter `pod|remote|runner|stability_protocol` over 126 files.**

This is a keyword-based scan, not a semantic authorization audit. If a future script that can launch POD workloads is given a name outside this filter, it would not appear in the whitelist. The standing rule that "historical scripts without explicit token gates are not current authorization" provides the necessary backstop, but M54 should keep this limitation in mind when naming new execution surfaces.

**P2-3: M47 `--samples` argument is parsed but immediately rejected if not exactly 8.**

The argument is accepted by the parser (`default=8`) but `validate_args` raises `SystemExit` if `int(args.samples) != 8`. This makes the argument a no-op for any value other than 8. It creates slight interface confusion. This is cosmetic and does not affect safety.

### Informational

- M47/M48 test counts are internally consistent: M47 dry-run produced 5 tests, M48 reached 15 tests, M51 reached 14 tests (different focused subsets), all full V3 rebuild counts grow monotonically (120 ΓåÆ 622 ΓåÆ 627 ΓåÆ 632 ΓåÆ 636 ΓåÆ 638 ΓåÆ 641 tests) across M43ΓÇôM52. No regression indicated.
- M43 alternate-order schedule (odd sample: v2_14 first; even sample: current first) correctly implements drift control for first-sample cold-start effects.
- M52 correctly preserves historical POD scripts rather than deleting them, because test contracts may still inspect their payload schemas.

---

## Answers to All Eleven Review Questions

**1. Does M43 remain accepted as bounded grouped-reduction Step-2 technical closure without broad release/performance claims?**

Yes. M43 clears the original blocked 262144├ù1024 CPU-hot gate with the productized CuPy RawKernel prepared-session route (3.454x vs CPU hot; 6.671x vs legacy hot). The trusted-offsets follow-up correctly traces the original wall regression (0.879x vs legacy wall) to prepare-time row-offset validation overhead and eliminates it with an explicit caller-controlled flag (15.41x vs legacy wall after). The CuPy route is genuinely generic: it is routed through the prepared-session runner with explicit partner selection, records standard launch-shape metadata, and is not hardcoded to any app shape. All non-authorization flags are explicitly false in both reports and evidence JSON. The Antigravity verdict `accept_m43_original_shape_hot_gate_cleared_continue_step2` was substantive and correctly addressed all six required questions. This review confirms that verdict. M43 stands as accepted bounded Step-2 grouped-reduction technical closure.

**2. Does M44 Step-2 scorecard sync remain accurate after M43 and M44 completion?**

Yes. M44 accurately records: (a) the frozen all-app Set-A/B scorecard as the controlling release gate (Set-A geomean 1.013x, 1/5 app wins, Barnes-Hut 0.844x severe regression, LibRTS Set-B below 0.95x); (b) the M43 evidence class as free local lx1, not paid POD; (c) what M43 changes (grouped reduction: performance-blocked ΓåÆ bounded technical closure) and what it does not change (frozen all-app gate, all-app blocks, open Claude debt). The M44 recommendation to next audit Barnes-Hut was validated correct by M45. The scorecard numbers are internally consistent with the prior frozen gate. M44-scorecard is accepted.

**3. Is M45 correct that Barnes-Hut is focused-fix-covered for planning, pending validation, and should not be a new route-tuning target?**

Yes. M45 correctly reads the prior evidence trail. The frozen all-app severe regression (app geomean 0.844x) is concentrated in OptiX node-coverage rows where Python point-packing contaminated the timing metric. M24 diagnosed and fixed this with a generic prepared fixed-radius query-payload surface. M7 projects the post-fix Barnes-Hut app geomean to approximately 1.009x. M28/M29 are runtime-trunk capability additions (Numba CUDA fused route, productized runner), not same-contract V3-over-V2.14 speedup proofs ΓÇö M45 correctly separates these. The read-only classification `focused-fix-covered for planning, pending next reviewed full-suite validation` is accurate. Beginning another Barnes-Hut coding round before full-suite validation would repeat the prior leaf-first error. M45 is accepted.

**4. Is M46 correct that LibRTS watch rows remain open and need stability protocol evidence before interpretation?**

Yes. M46 correctly identifies two distinct open surfaces: OptiX cold (`geomean 0.973x, median 1.045x, 6/8 samples passing`, labeled `improved_not_closed`) and Embree 32768 (`geomean 0.975x, median 0.911x, 1/3 samples passing`, labeled `stability_watch_blocker`). The Embree 32768 numbers in particular are not interpretable without order-controlled stability evidence ΓÇö median and 2/3 samples fail the 0.950x threshold even though geomean barely passes. The M27 retain fix (`query_repeat==1 ΓåÆ retain_repeat_outputs=False`) is generic and correct; M46 rightly keeps it without reverting. Recommending M47 as a focused protocol design step rather than a code rewrite or ad hoc POD run is sound. M46 is accepted.

**5. Is M47 protocol/harness safe as dry-run-only by default?**

Yes. Code verified at `scripts/v3_phoenix_m47_librts_stability_protocol.py`:
- Default path: `if not bool(args.execute): return build_payload(..., status=STATUS_DRY_RUN)` ΓÇö runs without touching any benchmark
- Token gate: `if str(args.authorization_token) != AUTHORIZATION_TOKEN: raise SystemExit(...)` ΓÇö required for real execution before any benchmark subprocess is launched
- `validate_args` enforces `--v2-root` at execute time
- `CLAIM_BOUNDARY` dict hardcodes all authorization flags to `False`
- Dry-run `summary.json` confirms `execute=false, failed_check_count=0, scenario_count=2, schedule_row_count=32`
- Alternating order (odd: v2_14 first, even: current first) correctly controls cold-start drift
- Green/Yellow/Red thresholds are well-defined with explicit stop conditions

Subject to P1 items (v2_root placeholder, Windows Python path) that apply at execution time. Protocol is accepted.

**6. Is M48 harness-safety hardening sufficient and still non-authorizing?**

Yes. M48 adds: preflight capture (nvidia-smi, Python versions, git revisions, unittest pre-run); tree-specific PYTHONPATH containing `<root>/src` and `<root>` so current and V2.14 environments don't bleed; fixture/contract mismatch detection recorded in pair analysis; current metadata failure forces scenario to `red` (not interpretable as performance evidence). These additions are appropriate for a cloud CUDA execution context where environment isolation and provenance matter. None of them authorize a run. The M48 dry-run evidence (`execute=false, failed_check_count=0`) and the focused 15-test gate plus full 122-module/632-test rebuild confirm no regressions from the hardening. M48 is accepted.

**7. Is M49 correct that stale Spatial/RayJoin route tuning remains blocked except as generic topology-stream residency/full-M3 accounting work?**

Yes. M49 correctly applies M35's reframing: the RayJoin LSI topology-stream runner provides structural route coverage (the productized runner path is visible) but no material performance gain over the existing scalar-count executor. The largest remaining row loss (0.888x for the RayJoin stress row) persists, but addressing it through app-specific route tuning repeats the M10/M11/M12/M13 pattern that already ran two POD runs without producing material Set-A evidence. Only a generic topology-stream prepared-handle/residency/full-M3 phase-accounting task would be justified. M49's queue table is clear and the ruling on M8's stale next-target recommendation is correct. M49 is accepted.

**8. Is M50's runner fail-closed gate sufficient to prevent accidental execution?**

Yes. Code verified at `scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py`:
- `if not bool(args.execute): payload = build_dry_run_packet(args)` ΓÇö default path does not call RayJoin workload
- `if str(args.authorization_token) != AUTHORIZATION_TOKEN: raise SystemExit(...)` before `run_packet(args)` is ever called
- `AUTHORIZATION_TOKEN = "M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED"` ΓÇö no default argument matches this string
- Historical CLI invocations that pass only `--output` now produce a dry-run planning packet instead of spending POD

The code correctly enforces the M49 boundary. Old commands are safe by default. M50 is accepted.

**9. Is M51's runbook non-authorizing and operationally precise enough for a future separately authorized focused run?**

Yes. M51 requires: (a) exact external verdict string `authorize_m47_one_focused_librts_stability_pod_run` (not interpretable or paraphrasable); (b) explicit identification of both current and V2.14 repo roots before execution starts; (c) dry-run first with specific output checks before authorized execution; (d) full copy-back requirements (summary.json + README.md + per-command stdout/stderr + preflight artifacts); (e) explicit intake rules with stop conditions before any performance interpretation. The runbook dry-run evidence confirms the command structure produces the expected output (`execute=false, schedule_row_count=32, failed_check_count=0`). The 14-test focused gate and 124-module/638-test rebuild confirm no drift from M48. M51 is accepted.

**10. Is M52's authorization-surface audit correct about current vs historical runner authorization?**

Yes. M52 correctly identifies exactly two currently active fail-closed/token-gated surfaces (M47 LibRTS stability harness, M50 Spatial topology-stream runner). Both require `--execute` plus their respective authorization tokens. Neither token has been supplied by any review. All other `v3_phoenix_*pod*` scripts are correctly classified as historical evidence tooling without current execution authorization. The fixed-string scan of 126 files confirmed `AUTHORIZATION_TOKEN` appears only in M47 and M50 active scripts. The standing rule for future scripts (add M50-style token gate or M51-style runbook before any paid run) is clear. M52 is accepted.

**11. Which single next bounded runtime-trunk work item should M54 take?**

**M54 recommended next item: prepare and submit a bounded external review packet requesting authorization for exactly one focused LibRTS stability POD run (M47/M48/M51 suite).**

Rationale: The LibRTS Embree 32768 row is the current primary Set-B/control blocker and is the only remaining open item for which the protocol, harness hardening, and execution runbook are all already designed and locally validated. The authorization surface is audited. No further local engineering is needed before requesting authorization ΓÇö only an external review packet that explicitly names the one-run scope, the token string, and the non-authorization list. This is the shortest path to closing the Set-B watch rows with controlled stability evidence.

If the LibRTS authorization review is not the user's preferred next item, the alternative is: prepare a generic topology-stream residency gap analysis for the Spatial/RayJoin M3 phase table as a read-only audit (not route tuning, not POD), per M49's permission boundary.

---

## Explicit Non-Authorization Block

This review explicitly does **NOT** authorize:

- **V3 release** ΓÇö blocked; `redo_required`; serious all-app paired evidence failed release bar
- **All-app benchmark run** ΓÇö blocked; frozen Set-A/B gate still controls; no all-app POD packet reviewed
- **Paid POD spend** ΓÇö blocked; no POD spend is authorized by any item in this backfill
- **Focused POD spend** ΓÇö blocked; M47 token `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED` is not granted by this review; a separate bounded review packet must be submitted and accepted before that token may be used
- **Public speedup wording** ΓÇö blocked
- **Broad V3-over-V2 claims** ΓÇö blocked; current all-app geomean 1.012x, far below release bar
- **V4 work** ΓÇö blocked
- **Embedding** ΓÇö blocked
- **C ABI** ΓÇö blocked
- **True-zero-copy claims** ΓÇö blocked

If a focused LibRTS POD run should be considered in M54, it must be presented as a **separate bounded review packet** naming the exact token, one-run scope, and full non-authorization list. It is not authorized by this review.
