# Goal4282 Claude Review: Goal4277-4281 v2.10 Release Hardening

Reviewer: Claude (claude-sonnet-4-6)
Review date: 2026-06-11
Subject: Goal4277-4281 — v2.10 source-tree release-hardening chain
Verdict: **accept**

---

## Scope

This review covers five goals that form a post-tag documentation and tooling
hardening chain:

- **Goal4277** — v2.10 release artifact alignment (VERSION, release package,
  partner boundary report paths)
- **Goal4278** — Source-tree doctor script and learner-facing onboarding page
- **Goal4279** — Benchmark evidence index script and evidence map doc
- **Goal4280** — v2.10 pod validation bundle script and runbook
- **Goal4281** — Pod bootstrap probe script and runbook

This is not a performance rerun, tag movement, or new release authorization.
The scope is entirely documentation consistency, onboarding tooling, and
pod-preflight infrastructure.

---

## Question-by-Question Findings

### 1. Does Goal4277 correctly align artifacts without moving the v2.10 tag?

**Yes.** Three stale artifacts were updated:

- `VERSION` updated from `v2.6` to `v2.10`. Correct — the entire v2.x learner
  surface, release consensus (Goal4270), and all tutorial/example paths already
  named `v2.10` as the active surface.
- `docs/release_reports/v2_10/README.md` was created as a stable one-page
  summary of the v2.10 scope, smoke commands, evidence links, and non-claims.
- `docs/partner_acceleration_boundaries.md` had three stale report path
  references replaced with correct existing filenames.

The tag position is explicitly recorded in the Goal4277 report
(`v2.10` → commit `2888b5ba`, `main` HEAD before cleanup → `1b66bddf`).
The report states and the release package README repeats: "Do not move the
existing tag without explicit maintainer authorization." The Goal4277 test
asserts the tag still exists and the report contains both commit references,
closing any ambiguity. No tag movement occurred and none is implied.

**Minor note:** The test at `tests/goal4277_v2_10_release_artifact_alignment_test.py:61`
runs `git rev-parse --verify v2.10` and asserts the tag exists. This is the
correct check — it verifies the tag was not moved or deleted, not that it
points to any particular commit.

### 2. Do Goals4278-4281 improve onboarding without making unauthorized claims?

**Yes.** Each tool is scoped to navigation or preflight:

- The source-tree doctor (Goal4278) checks version marker, required paths,
  core module imports, and optional partner/library hints. It produces no timing
  data. Optional warnings are non-blocking unless `--strict` is passed. The
  doctor page explicitly states: "The doctor is not a benchmark and does not
  authorize performance claims."
- The benchmark evidence index (Goal4279) produces a compact map of the ten
  current rows, their evidence report references, pod requirements, and user
  reading notes. Every field in the JSON output has `release_authorized`,
  `public_speedup_claim_authorized`, `broad_rt_core_claim_authorized`, and
  `paper_reproduction_claim_authorized` hardcoded to `false`. The index's own
  `status` field is `"current_v2_10_evidence_index_not_release_authorization"`.
- The pod validation bundle (Goal4280) runs only local preflight by default.
  Hardware packets require explicit `--run-front-door`, `--run-scale-profile`,
  or `--run-partner-comparison` flags. The summary JSON has the same full set of
  non-authorizing flags hardcoded to `false`, and the bundle script actively
  scans for any forbidden-true flags in subprocess JSON output
  (`FORBIDDEN_TRUE_FLAGS` at `scripts/rtdl_v2_10_pod_validation_bundle.py:17`).
- The pod bootstrap probe (Goal4281) checks toolchain and library availability
  only. It does not run benchmark commands or install packages.

No package-install, broad RT-core speedup, whole-app speedup, automatic
partner selection, zero-copy, or paper-reproduction wording appears anywhere in
the new scripts or docs.

### 3. Are the scripts safe by default?

**Yes, with one small observation.**

- **Doctor** (`rtdl_source_tree_doctor.py`): no subprocess calls at all in the
  default path; the `--run-smoke` subprocess runs a single read-only example
  with a 20 s timeout. Safe.
- **Evidence index** (`rtdl_benchmark_evidence_index.py`): no subprocess calls;
  reads from the front-door registry via import and checks file existence. Safe.
- **Pod validation bundle** (`rtdl_v2_10_pod_validation_bundle.py`): default
  path runs four non-hardware subprocess steps (doctor, evidence index,
  front-door dry-run, scale-profile dry-run). All four are read-only or dry-run.
  Hardware subcommands require explicit flags. Safe by default.
- **Bootstrap probe** (`rtdl_pod_bootstrap_probe.py`): runs `nvidia-smi` and
  `nvcc --version` with a 10–20 s timeout when those tools are on PATH. Both
  are standard query commands with no side effects. Safe.

**Observation (non-blocking):** The bootstrap probe's `OPTIX_PREFIX_CANDIDATES`
tuple at line 26 includes a hardcoded local path
`/home/lestat/vendor/optix-dev`. This is a developer workstation path that will
always produce a `WARN` miss on any pod and is mildly distracting in probe
output. It is not unsafe, but it could be cleaned up or moved to an environment
variable in a later pass.

### 4. Are docs and current paths clean?

**Yes.** All new and modified documentation pages reference `examples/current/`,
`tutorials/current/`, and `docs/release_reports/v2_10/`. The tests for
Goals4278 and 4279 both assert `assertNotIn("examples/v2_0", ...)` and
`assertNotIn("v2.6", ...)` across the relevant doc files. The release package
README, the partner boundaries page, the benchmark evidence index page, the
source-tree doctor page, and both pod runbooks are all internally consistent
with the v2.10 surface.

The v2.10 release report at `docs/release_reports/v2_10/README.md` clearly
links to the evidence chain (Goal4266, Goal4267, Goal4268, Goal4269, Goal4270,
Goal4271, Goal4274, Goal4276) and explicitly states what v2.10 does not claim.
No stale v2.6 or v2_0 learner paths were found in the files reviewed.

### 5. Are the tests sufficient?

**Yes, for this cleanup scope.** The 37-test suite (per Goal4281 expanded local
gate) covers:

- VERSION regression check
- Release package content and non-claim language
- Stale report path detection in partner_acceleration_boundaries.md
- Tag existence and no-movement assertion
- Doctor human output, JSON structure, `--run-smoke` end-to-end, and doc wiring
- Evidence index 10-app coverage, current path validation, evidence report file
  existence, non-authorizing flags, markdown output, and doc wiring
- Bundle local preflight step names, artifact file creation, hardware-flag
  gating, non-authorizing flags, and runbook wiring
- Bootstrap probe JSON contract, human output, `--strict` mode, and runbook
  wiring

**What remains before a fresh pod run:**

1. The pod bootstrap probe must report `status: ready` on the target pod.
   This requires NVIDIA GPU visibility, `nvcc`, `make`/`g++`, OptiX headers,
   and a built `librtdl_optix.so`.
2. Run `scripts/rtdl_v2_10_pod_validation_bundle.py --run-front-door
   --run-scale-profile` and verify `bundle_summary.json` shows all steps
   `pass`.
3. Optionally run `--run-partner-comparison` to refresh the CuPy/Numba
   partner comparison evidence.
4. All ten front-door app rows must pass claim-flag checks (no forbidden true
   flags). The bundle's `_find_forbidden_true_flags` scan handles this
   automatically.

None of those steps are authorization gates for this source-tree hardening
chain — they are the next hardware-dependent work, as the handoff states.

---

## Boundary Check

This review explicitly does not authorize any of the following:

- Release, tag movement, or public speedup wording
- Package-install wording
- Broad RT-core speedup wording
- Paper-reproduction wording
- Automatic partner selection
- True zero-copy or device-residency product claims
- AMD/HIPRT performance wording
- App-specific native-engine logic

The next hardware-dependent step is a fresh pod run of the v2.10 bundle on
current `main`.

---

## Summary

The five-goal chain correctly cleans up post-tag documentation artifacts,
adds safe default-off tooling, and wires everything into the learner path
without widening any claim boundary. The tag position is guarded, the scripts
are safe by default, the docs are stale-path-clean, and the test suite is
appropriately scoped to the cleanup work. The one minor observation (hardcoded
local path in the bootstrap probe) is non-blocking.

**Verdict: accept**
