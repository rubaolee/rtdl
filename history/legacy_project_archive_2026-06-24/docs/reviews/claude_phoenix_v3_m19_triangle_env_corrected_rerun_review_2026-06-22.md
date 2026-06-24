I have read and verified all packet documents and the raw attempt 1 `summary.json`. Here is the review.

---

## Phoenix V3 M19 Triangle Environment-Corrected Replacement Run — External Review

**Date:** 2026-06-22
**Reviewer role:** External critical reviewer (not Bernoulli)

---

## Verdict

```
authorize_m19_one_env_corrected_triangle_replacement_pod
```

Subject to one required zero-cost pre-launch check described below. If that check fails, the run must not proceed without a revision verdict.

---

## Explicit Authorization Answers

| Item | Answer |
|---|---|
| Release authorization | **No** |
| Public speedup authorization | **No** |
| Broad V3-over-V2 authorization | **No** |
| Focused replacement POD authorization now | **Yes — one run only** |
| All-app POD authorization | **No** |
| **Is attempt 1 performance evidence?** | **No** |
| **Does Triangle count as the third strict Set-A material probe now?** | **No** |

---

## Facts Verified Against Raw Evidence

I read `summary.json` from the attempt 1 evidence directory directly and confirmed every claim in the packet. The packet is accurate and self-consistent.

**What passed in attempt 1:**

- Edge file preflight: PASS (sha256 `8bc1bd3f…` matched, 480,000 edges, 3,840,000 bytes, `checksum_matches_expected=true`)
- RT hardware gate: PASS (NVIDIA RTX 4000 Ada Generation, compute_cap=8.9, driver=550.127.05, `optix_capable_gpu_present=true`)
- Embree same-contract control: PASS (`oracle_triangle_count=320000`, `observed_triangle_count=320000`, `query_median_ms=543.299`, `wrapper_wall_sec=11.217s`, returncode=0)

**What failed:**

- `legacy_app_front_door_optix`: returncode=1, `ModuleNotFoundError: No module named 'cupy'`, no payload, `wrapper_wall_sec=0.802s` (exited almost immediately)
- `productized_prepared_execution_runner`: `ModuleNotFoundError("No module named 'cupy'")`, no payload recorded at all
- `comparisons: {}` — no ratio evidence of any kind
- `failed_check_count: 6`

The subprocess command arrays recorded in `summary.json` confirm the driver used `/usr/bin/python3` (Python 3.12.3) for all variants. This is the sole cause of both OptiX/CuPy failures. No GPU hardware error, no harness logic error, no correctness gate error.

---

## On Attempt 1 As Performance Evidence

**Attempt 1 is not performance evidence.** The Embree control produced a number (query_median_ms=543.299), but `comparisons` is empty. The productized runner produced no payload. The legacy OptiX arm produced no payload. There is no speedup, no ratio, and no productized execution path result. The attempt is an environment/intake failure, full stop.

The Embree control result from attempt 1 may be cited only as:

- confirmation that the K4 80,000-clique input identity is valid;
- confirmation that RT hardware is present and functional;
- confirmation that the Embree oracle is correct on the serious row;
- the Embree baseline value that the replacement run's results will be compared against (if the replacement run succeeds).

It is not a Triangle performance conclusion and does not advance any Set-A status.

---

## On Triangle As The Third Strict Set-A Material Probe

**Triangle does not count as the third strict Set-A material probe.** The third probe requires: all three variants match the oracle, runner metadata shows `runtime_trunk_executes_end_to_end=true`, and the runner beats Embree by ≥1.20x on both hot query median and runner-inclusive wall. None of that was obtained. Probe status is unchanged from before attempt 1 ran.

```
third_strict_set_a_material_probe_closed: false
```

---

## Why The Failure Mode Supports Replacement Authorization

The failure is cleanly diagnosed, minimal, and verified:

1. The failing interpreter (`/usr/bin/python3`) lacks CuPy — confirmed from subprocess command arrays in `summary.json`.
2. The project venv (`/root/rtdl_v3_rebuild_20260620/.venv/bin/python`) has CuPy and Numba — confirmed by read-only post-failure diagnosis, recorded in the harness JSON.
3. The M18 harness passed two blocking review rounds and was authorized with no remaining P1 blockers. That review is not invalidated — the harness did not change.
4. The proposed replacement command changes exactly one variable: the interpreter path. Everything else — script, row, flags, success bars, hard cap, output format — is preserved.
5. There is no cheaper local substitute. The intended measurements require CuPy/OptiX on the POD GPU. The local environment cannot replicate this.

The consumed M18 authorization cannot be extended. This is a fresh M19 authorization for one replacement run, and that is correct framing.

---

## Required Pre-Launch Check: Subprocess Interpreter

**This is a blocking pre-condition.** Do not skip it.

The attempt 1 `summary.json` shows that the `legacy_app_front_door_optix` subprocess command array was built with `/usr/bin/python3` at runtime. The productized runner runs in-process, so fixing the driver interpreter fixes it directly. But if the harness hardcodes `/usr/bin/python3` for subprocess invocations rather than using `sys.executable`, the `legacy_app_front_door_optix` subprocess would still import the wrong environment even with the venv driver — and the run would fail closed on that arm.

**Required before launch:** Read or grep `scripts/v3_phoenix_triangle_runner_m18_pod_ab.py` locally to confirm that subprocess command construction uses `sys.executable` (or equivalent derived from the driver interpreter) rather than a literal `/usr/bin/python3` or bare `python3`.

- **If confirmed `sys.executable`:** proceed to launch with the proposed venv command.
- **If hardcoded path is found:** do not run. Return for a revision verdict. The command or the script must be updated to pass the venv interpreter through to subprocess invocations, and this review must be re-requested on the revised packet before spending POD.

This check costs nothing and eliminates the one remaining uncertainty.

---

## Authorized Command

If and only if the subprocess interpreter check passes:

```
cd /root/rtdl_v3_rebuild_20260620/current &&
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python scripts/v3_phoenix_triangle_runner_m18_pod_ab.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_venv_20260622 \
  --edge-file build/phoenix_v3_m18_triangle/k4_cliques_80000.edge \
  --cliques 80000 \
  --partner cupy \
  --warmup 1 \
  --repeat 5 \
  --require-rt-hardware \
  --generate-edge-file
```

Run exactly once. New output directory only. Do not overwrite attempt 1 artifacts.

---

## Success Bars — Unchanged From M17/M18

No bar is relaxed. All must hold:

- All three variants match `oracle_triangle_count=320000`
- Runner metadata: `runtime_executed=true`, `productized_execution_path=prepared_execution_session_runner`, `runtime_trunk_executes_end_to_end=true`
- Runner OptiX beats Embree same-contract control by ≥1.20x on hot query median AND runner-inclusive wall — both required
- Runner-inclusive wall ≥0.98x of legacy app-front-door OptiX route
- All release/public/broad V3-over-V2/all-app/V4/zero-copy flags remain false

---

## Stop Conditions

- **Subprocess interpreter check fails** (hardcoded path found): stop before launch, return for revision
- **`failed_check_count > 0`** in the replacement run: stop immediately, copy evidence back, do not re-run
- **Hard cap reached** (2h / $0.50): stop regardless of progress
- **Any result, pass or fail:** do not re-run seeking a better outcome; do not expand scope

---

## Hard Cap

**2 h / $0.50** — unchanged from M18. No revision.

---

## Claim Boundary Confirmed

```
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
third_strict_set_a_material_probe_closed: false
```

These remain false regardless of whether the replacement run passes or fails. A passing replacement run closes the Triangle Set-A candidacy question (if bars are met), but it does not authorize release, public speedup wording, broad V3-over-V2 wording, or all-app spend. A separate review would be required for any of those.
