# Goal4287: Claude Review — Goal4285 + Goal4286 Pod Driver Hardening

Date: 2026-06-11
Reviewer: Claude (external read-only)
Verdict: **accept-with-boundary**

---

## Scope

- Goal4285: replaced hard-coded `/home/lestat/vendor/optix-dev` with
  `Path.home() / "vendor" / "optix-dev"` in `rtdl_pod_bootstrap_probe.py`.
- Goal4286: added `rtdl_remote_pod_validation_driver.py`, a dry-run-by-default
  SSH driver for the v2.10 pod validation flow.

---

## Q1 — Does Goal4285 close the machine-specific OptiX path concern?

**Yes, completely.**

`_optix_prefix_candidates()` (lines 20–40 of `rtdl_pod_bootstrap_probe.py`) now
builds its list via `Path.home() / "vendor" / "optix-dev"` rather than the
literal `/home/lestat/vendor/optix-dev`. The function also de-duplicates the
candidate list via a `seen` set before returning, so adding `$HOME` alongside
the `/root/*` and `/workspace/*` pod candidates cannot produce a duplicate probe
if `HOME=/root` on a pod.

The candidate set after the change is:

| Priority | Path | When useful |
|---|---|---|
| 1 | `$OPTIX_PREFIX` | any environment |
| 2 | `/root/vendor/optix-sdk` | root-user pod |
| 3 | `/root/vendor/optix-dev` | root-user pod |
| 4 | `/workspace/vendor/optix-sdk` | workspace-style pod |
| 5 | `/workspace/vendor/optix-dev` | workspace-style pod |
| 6 | `/workspace/vendor/optix-dev-8.0.0` | versioned workspace |
| 7 | `Path.home() / "vendor" / "optix-dev"` | any developer machine |

The addition of entries 4 and 5 (`/workspace/vendor/optix-sdk` and
`/workspace/vendor/optix-dev`) is new and sensible—they cover the common
workspace-style pod layout. The probe is not less useful on local Linux: entry 7
resolves to the developer's `$HOME` regardless of username.

The runbook (`v2_10_pod_bootstrap_probe.md`) now documents `$HOME/vendor/optix-dev`
and omits any user-specific path. Both Goal4281 and Goal4285 tests assert the
source code and runbook are free of `/home/lestat/vendor/optix-dev`.

**Finding: none. Goal4285 closes the concern cleanly.**

---

## Q2 — Is the Goal4286 remote driver safe by default?

**Largely yes, with one practical limitation that must be fixed before real use.**

### What is safe

- **Dry-run default**: `--execute` is required to open an SSH connection.
  Without it the tool prints the generated script and exits 0 (lines 126–136).
  The `plan()` payload records `"mode": "dry_run"` in JSON.
- **Fresh mktemp checkout**: the remote script creates
  `mktemp -d /root/rtdl_v2_10_validation.XXXXXX`, clones into it, and never
  touches any pre-existing directory on the pod. `destructive_checkout` is
  explicitly `False` in the plan payload.
- **No destructive shell commands**: the remote script contains no `rm -rf`,
  no `git reset --hard`, no `git checkout --`, and no package installs. The test
  `test_remote_script_has_progress_and_no_destructive_checkout` verifies this
  with explicit `assertNotIn` checks.
- **`set -euo pipefail`**: the remote script exits on the first failing command,
  preventing silent partial runs.
- **Progress markers**: every major step emits a `[rtdl-remote-pod]` line with
  a timestamp, workdir path, git HEAD, and step name.
- **SSH keepalive**: `ServerAliveInterval=30` and `ServerAliveCountMax=4` keep
  the connection alive for normal pod durations. If the network is lost for more
  than 120 s the SSH client will exit, but the remote script continues server-side
  (no orphan risk beyond the mktemp directory).

### Practical limitation — output is fully buffered in execute mode

`subprocess.run(..., stdout=subprocess.PIPE, ...)` (line 139) buffers all remote
stdout until the subprocess exits. Because the driver collects output this way,
the `[rtdl-remote-pod]` progress markers are invisible to the operator during
the run. A pod session that takes 60–90 minutes will show nothing until it
completes or the `--timeout-sec` (default 7200 s) expires. This defeats the
stated design intent of "visible progress."

Additionally, `stdout_tail` in the JSON summary captures only the last 8000
characters (line 151). A run that fails early after producing substantial output
may not include the root-cause error in the captured tail.

**This must be fixed before the first real pod use.** See Q5.

### Default `--optix-prefix` path

The default is `/root/vendor/optix-sdk` (line 117), which is a pod path.  If
`--build-optix` is passed without a pre-installed OptiX SDK there, `make
build-optix` will fail and `set -e` will abort cleanly. Acceptable.

---

## Q3 — Claim boundary integrity

All three non-authorizing flags are set and machine-verified:

| Flag | Value | Where asserted |
|---|---|---|
| `release_authorized` | `False` | probe L182, driver L104, Goal4281 test L42, Goal4286 test L47 |
| `public_speedup_claim_authorized` | `False` | probe L183, driver L105, Goal4281 test L43, Goal4286 test L48 |
| `broad_rt_core_claim_authorized` | `False` | probe L184, driver L106, Goal4281 test L44, Goal4286 test L49 |

The runbooks for both the bootstrap probe and the remote driver contain explicit
boundary paragraphs. The Goal4285 and Goal4286 reports each include a `## Boundary`
section. No package-install claim, no speedup claim, and no release authorization
appears anywhere in the reviewed files.

**Finding: claim boundaries are intact.**

---

## Q4 — Test adequacy for this tooling layer

**Adequate for the pre-hardware layer, with minor gaps noted.**

### What is covered

| Test file | Coverage |
|---|---|
| `goal4281_pod_bootstrap_probe_test.py` | JSON contract, text output, strict-mode exit code, runbook wiring, absence of developer path |
| `goal4285_pod_probe_generic_optix_candidate_test.py` | source and runbook free of `/home/lestat/`, generic path present, workspace candidates present, report boundary text |
| `goal4286_remote_pod_validation_driver_test.py` | default dry-run mode, plan payload flags, script content (presence/absence), runbook and report boundary text |

The tests run entirely locally without network access or real hardware, which is
correct for a dry-run tooling layer. The Goal4281 strict-mode test
(`test_strict_mode_matches_readiness_status`) correctly validates the probe's
exit code against the runtime readiness status on whatever machine runs the suite.

### Gaps (non-blocking)

1. `build_ssh_command()` is not tested directly; its output is only observable
   through the dry-run JSON payload's `"command"` key, which the test does not
   inspect explicitly. A single assertion like `assertIn("ServerAliveInterval=30",
   " ".join(payload["command"]))` would close this.
2. No test exercises the `--run-partner-comparison` flag in isolation to confirm
   `--run-partner-comparison` appears in the generated script but
   `--run-front-door` does not when `--run-hardware` is omitted. This is a
   corner case, not a blocker.
3. The `--timeout-sec` parameter is accepted but not reflected in the dry-run
   JSON payload, making it untestable without a real SSH connection.

These gaps are acceptable for a dry-run tooling layer.

---

## Q5 — What must be fixed before using the driver on the next pod

### Must fix

**1. Stream output in execute mode** (`scripts/rtdl_remote_pod_validation_driver.py`, lines 139–146)

The current implementation:
```python
completed = subprocess.run(
    payload["command"],
    input=payload["remote_script"],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    timeout=args.timeout_sec,
    check=False,
)
```

Replace with `subprocess.Popen` and line-by-line streaming (or drop
`stdout=subprocess.PIPE` when `--json` is not requested), so progress markers
appear in real time. The JSON summary mode can still capture output by
accumulating lines into a buffer. Without this change, the operator has no
feedback for the duration of the pod run, which is the primary failure mode
for long hardware sessions.

### Should verify before use

**2. Confirm the public repo is at the expected HEAD.** The remote script clones
`https://github.com/rubaolee/rtdl.git` at `--depth 1`. Whatever commit is at
the tip of `main` at clone time is what runs on the pod. Ensure the pod run
is scheduled only after all v2.10 validation-hardening commits have been pushed,
or add a `--ref` argument to pin a specific commit or tag.

**3. Manually review the dry-run script before `--execute`.** The runbook already
says to inspect the `remote_script` field. Do this: run the driver with `--json`
and confirm the script contains the expected flags before the real run.

**4. Check `/root/vendor/optix-sdk` exists on the target pod before passing
`--build-optix`.** If OptiX headers are absent, `make build-optix` fails and
`set -e` aborts the run after the bootstrap probe. The bootstrap-probe output
(`bootstrap_probe_before_build.json`) will show OptiX headers as unavailable,
and the operator must intervene manually.

### Nice to have (not blocking)

- A `--repo-url` flag to override `REPO_URL` without editing the script.
- A `--ref` flag to clone a specific branch or tag.
- Capture and emit the full (not tail-only) stdout on failure in the JSON summary.

---

## Summary

| Goal | Finding | Verdict |
|---|---|---|
| Goal4285 | Machine-specific path replaced cleanly; candidates, runbook, and tests all updated; no regressions to probe usefulness | accept |
| Goal4286 | Driver is safe by default, boundaries are intact, tests are adequate, but output buffering in execute mode hides progress during a real pod run | accept-with-boundary |

**Overall verdict: accept-with-boundary.** The output-buffering issue in Goal4286's
execute mode must be resolved before the first live pod run. Goal4285 is
unconditionally ready. Neither goal authorizes any performance claim, installs
packages, or moves a release tag.
