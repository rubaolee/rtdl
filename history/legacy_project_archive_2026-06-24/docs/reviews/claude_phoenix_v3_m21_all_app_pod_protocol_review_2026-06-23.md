---

## External Critical Review: Phoenix V3 M21 All-App POD Protocol

**Reviewer:** Claude (external), 2026-06-23
**Files reviewed:** all six listed, in full

---

### 1. Does the protocol satisfy every M20 required item?

**Yes**, with one minor gap to disclose.

All M20 required items are present and cross-consistent across the JSON, MD, and gate script:

| Required item | Status |
|---|---|
| Non-release header | Present in JSON field, MD section, gate output hardcoding |
| Fail-closed bars (4) | Present, correctly stated, gate enforces them programmatically |
| Frozen case-ID whitelist | 10 apps / per-app case lists, sourced from pre-run frozen file |
| Same RTX 4000 Ada hardware gate | Present; preflight confirmed pass |
| Project venv / sys.executable preflight | Runner exits 65/66 before any benchmark |
| LibRTS OptiX AABB watch row | Correctly labeled non-blocking, alert-if-<0.95x |
| Correctness/oracle gate | Three suites × two trees, failure invalidates rows and fails protocol |
| Post-run interpretation | Explicit in JSON, MD, and gate output; clearance ≠ release |
| Resource estimate and hard cap | 5.5–7.0 h, 8.0 h hard cap, USD 2.00 cost cap |

**Minor gap (disclosed, not blocking):** The protocol document lists "cupy import succeeds under the same interpreter" as a required prelaunch check, but the runner's cupy/numba import block runs inside a `|| true` guard — it logs but does not exit on failure. Functionally equivalent: if cupy or numba is broken, all three suites fail, the correctness gate fires, and the protocol fails. There is no silent-pass pathway from a broken cupy install. The gap is terminology versus implementation, not a safety hole.

---

### 2. Are runner preflight and M21 protocol gate sufficient for one run?

**Yes**, with two minor points noted.

**Runner:**
- Authorization guard (exit 64): both `PHOENIX_V3_ALLOW_ALL_APP_RUN=1` and `PHOENIX_V3_RUNTIME_TRUNK_EXECUTED=1` required. Correct.
- Interpreter check (exit 65 / 66): explicit `os.path.realpath` comparison, not bypassed by `set +e` because they use explicit `exit` calls. Correct.
- All suites launched through `$python_bin`. Correct.
- `set +e` is intentional for keep-going collection of all suite exit codes into `status.tsv`; fail-closed evaluation is in the gate layer, not the runner. Acceptable design.
- `bash -n` remote syntax check passed without running benchmarks.

**Minor gap — hardware auto-verification:** The runner logs `nvidia-smi` output but does not programmatically exit if the GPU name or driver differs from the required values. The JSON says `fail_if_gpu_or_driver_differs_without_new_review: true`, but this is enforced by discipline (same-POD execution), not by code. Mitigated by the confirmed preflight and the fact that the run command is specific to the identified POD (`213.173.108.14:11592`). Not a blocker, but a known enforcement gap.

**Protocol gate (`v3_phoenix_m21_all_app_protocol_gate.py`):**
- Reads bars and whitelist from the frozen protocol JSON, not from run output.
- Validates every row against the frozen case whitelist before scoring.
- Checks correctness fields before accepting performance data.
- Evaluates all four fail-closed bars programmatically.
- Hardcodes `release_authorized: False`, etc. — not conditional on results.
- Returns exit 0 only when status ends with `_not_release` and no failures. Exit 2 otherwise.
- Confirmed: old 1.012x summary returns exit 2 / `protocol_fail_invalid_or_out_of_scope`. The gate correctly rejects the old baseline.

**Cosmetic note:** The gate's `post_run_interpretation` key lookup always falls to the fallback chain because the computed status strings (`protocol_fail_*`, `blocking_bars_cleared_*`) never match the protocol JSON's `if_*` keys. The fallback chain is correct and produces the right text. Not a safety issue.

---

### 3. Is the non-release boundary strong enough?

**Yes. It is structurally overdetermined.**

The boundary appears at five independent layers:
1. Protocol JSON `authorizations` block: all four false at write time.
2. Protocol MD "Non-Release Header" section, explicitly leading the document.
3. Gate script output JSON: `release_authorized`, `public_speedup_claim_authorized`, `broad_v3_faster_than_v2_claim_authorized` hardcoded `False` — not derived from results.
4. `post_run_interpretation.if_all_fail_closed_bars_clear`: even full clearance text says "release remains not authorized."
5. Gate exit code 0 only for `_not_release` statuses — the name embeds the boundary.

No result pathway from this run can produce a release authorization or public speedup claim. The boundary is strong.

---

### 4. Is one all-app POD run authorized now?

**Yes.**

Preconditions met:
- M20 verdict authorized protocol preparation; that scope is closed.
- Three focused productized material probes closed (exceeds required 2).
- All M20 required protocol items present.
- Hardware confirmed: RTX 4000 Ada, driver 550.127.05, compute 8.9.
- Interpreter gate enforced in runner (exit 65/66).
- Frozen case-ID whitelist in place with out-of-scope policy.
- Correctness gate precedes performance data.
- Four fail-closed bars correctly stated and implemented in the gate.
- Non-release boundary reinforced at every layer.
- Old baseline correctly fails the M21 gate.
- No benchmark started during preflight or protocol preparation.
- Two minor gaps identified above do not create silent-pass pathways.

---

### 5. Concrete blocker if not authorized

N/A — the run is authorized.

---

```
one_all_app_pod_run_authorized: true
max_run_count: 1
expected_resource_window_hours: 5.5-7.0
hard_cap_hours_before_new_review: 8.0

release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
release_based_on_all_app_run_outcome: false
```
