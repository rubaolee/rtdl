# Goal749 Windows OptiX Robot Fix Review

## Verdict

ACCEPT_WITH_NOTES.

The OptiX short-ray root-cause hypothesis is technically coherent, and the proposed interval-local `optixReportIntersection` fix is the right class of fix for 2D ray/triangle any-hit and prepared any-hit count. I found no reason to block the Mac/Linux fix direction.

The main note is scope: a fresh Windows clone of GitHub `origin/main` only contains commit `ed205eb472ad8b097993f93d0abc2ca65c754e11`. The later Mac/Linux commits named in bridge status (`cb42f4f`, `2283013`, `b0cedf8`, `152c3ce`) are not present in the fetched remote, and the Goal748 harness files are absent from this Windows checkout. This review therefore combines direct source inspection of the available OptiX core/tests with review of the request-provided patch/test/harness descriptions.

Windows Codex did not push.

## Checkout

- Checkout path: `C:\Users\Lestat\rtdl_goal749_windows_review`
- Repository: `https://github.com/rubaolee/rtdl.git`
- Commit inspected: `ed205eb472ad8b097993f93d0abc2ca65c754e11`
- Commit short: `ed205eb Add cross-Codex shared bridge protocol`
- GitHub `origin/main` at inspection time: `ed205eb472ad8b097993f93d0abc2ca65c754e11`
- Local scratch edits in checkout: none; `git status --short` was clean.

Unavailable in the fetched Windows clone:

- `cb42f4f Add scaled OptiX robot performance harness`
- `2283013 Fix OptiX short-ray any-hit reporting`
- `b0cedf8 Fix OptiX short segment-polygon reports`
- `152c3ce Record Gemini consensus on OptiX interval fixes`
- `scripts/goal748_optix_robot_scaled_perf.py`
- `tests/goal748_optix_robot_scaled_perf_test.py`
- the new named short-ray tests from the request; the older files exist, but do not contain those test methods in this checkout.

## Antigravity / Gemini 3 Flash / Gemini CLI Attempt

Antigravity is installed:

```text
Antigravity 1.107.0
62335c71d47037adf0a8de54e250bb8ea6016b15
x64
```

The CLI exposes chat modes (`ask`, `edit`, `agent`) but no `--model` flag. The user-visible Antigravity UI showed `Gemini 3 Flash` as a selectable model, but the CLI did not provide a way to force or verify that model.

Exact command attempted:

```powershell
antigravity chat --mode ask --add-file src/native/optix/rtdl_optix_core.cpp --add-file tests/goal637_optix_native_any_hit_test.py --add-file tests/goal671_optix_prepared_anyhit_count_test.py "Goal749 consensus review request: Review whether RTDL OptiX 2D ray_triangle_any_hit using optixReportIntersection(0.5f,0u) is a plausible short-ray bug when raygen normalizes direction and traces tmax=r.tmax*len, whether replacing it with interval-local hit_t=optixGetRayTmin()+1e-6 clamped to optixGetRayTmax is safe for any-hit semantics, whether short-ray CPU-vs-OptiX native/prepared tests would catch the bug, whether a Goal748 robot scaled harness should separate CPU oracle, row materialization, Embree rows, OptiX rows, and OptiX prepared scalar count, whether docs should mark prior robot OptiX evidence suspect, and which other hardcoded optixReportIntersection(0.5f,...) sites are risky. Return concise ACCEPT/BLOCK verdict with findings."
```

Result: process exited 0 with no stdout/stderr. It appears to launch or route the prompt into Antigravity rather than returning a machine-readable model answer. I cannot honestly include an extracted Gemini/Antigravity verdict from Windows CLI output. Availability/auth/quota status is unclear from the CLI.

After user suggestion, Windows Codex also installed Node.js LTS and the official Gemini CLI:

```powershell
winget install --id OpenJS.NodeJS.LTS --source winget --accept-package-agreements --accept-source-agreements --silent
npm.cmd install -g @google/gemini-cli
gemini.cmd --version
```

Observed Gemini CLI version:

```text
0.38.2
```

Headless Gemini 3 Flash smoke attempted:

```powershell
gemini.cmd --model gemini-3-flash --prompt "Reply with exactly: GEMINI_READY" --output-format text
```

Result: blocked by missing Gemini CLI authentication:

```text
Please set an Auth method in your C:\Users\Lestat\.gemini\settings.json or specify one of the following environment variables before running: GEMINI_API_KEY, GOOGLE_GENAI_USE_VERTEXAI, GOOGLE_GENAI_USE_GCA
```

Conclusion: Gemini CLI is now installed, but Windows cannot obtain a headless Gemini verdict until auth is configured. This is clearer than the Antigravity result: the blocker is authentication, not package availability.

## Check 1: Root-Cause Coherence

ACCEPT.

In the inspected source, 2D ray/triangle hit-count raygen normalizes the direction:

```cpp
make_float3(r.dx / len, r.dy / len, 0.0f),
0.0f, r.tmax * len, 0.0f,
```

but `__intersection__rayhit_isect` reports:

```cpp
optixReportIntersection(0.5f, 0u);
```

That is a plausible and direct short-ray correctness bug. If a robot edge has world length `0.25` and `r.tmax == 1`, the traced interval is `[0, 0.25]`; reporting at `t=0.5` lies outside the active interval and the accepted hit is not reported. The exact predicate may decide the ray/triangle overlap is true, but OptiX still requires the reported intersection parameter to be inside the trace interval.

This explains the observed pattern:

- CPU and Embree count: `5742`
- OptiX row/prepared count: `3828`

It also explains why the bug is consistent at smaller scales: the failure is tied to edge length and trace interval, not aggregate workload size.

## Check 2: Proposed Fix Safety

ACCEPT.

The proposed pattern is safe for any-hit semantics:

```cpp
float hit_t = optixGetRayTmin() + 1.0e-6f;
if (hit_t > optixGetRayTmax()) hit_t = optixGetRayTmax();
optixReportIntersection(hit_t, 0u);
```

For 2D any-hit/count workloads, the intersection program has already accepted the analytic predicate, and the any-hit program either increments a count, sets an any-hit bit, ignores the intersection to keep traversing, or terminates when appropriate. The exact hit distance is not consumed as a closest-hit distance or as a user-visible coordinate. Therefore the only necessary property of the reported `t` is that it is a valid interval-local report parameter.

The clamp matters for very short intervals where `tmin + 1e-6` could exceed `tmax`. The code also remains compatible with count semantics: one accepted primitive produces one any-hit callback. It does not change the CPU predicate, the triangle AABB candidate set, or output ordering guarantees.

Small caveat: for future closest-hit or ordered-hit semantics, a synthetic interval-local `t` would be insufficient. This specific fix is appropriate because the reviewed workloads are any-hit/count-only.

## Check 3: Short-Ray Regression Tests

ACCEPT_WITH_NOTES.

The request-described tests are the right regression shape:

- `tests/goal637_optix_native_any_hit_test.py::test_optix_native_any_hit_2d_matches_cpu_for_short_rays`
- `tests/goal671_optix_prepared_anyhit_count_test.py::test_prepared_anyhit_count_matches_cpu_for_short_rays`

They would have caught the old fixed-`0.5f` bug on a native OptiX machine if the short rays have effective trace intervals below `0.5` and a CPU-positive intersection. This is exactly the missing coverage in the older tests present in the fetched Windows checkout: the existing 2D native any-hit test uses rays such as `dx=1.0, tmax=4.0`, which leaves an effective interval greater than `0.5`, and the prepared-count test similarly does not force the short-interval failure.

The two-test split is also good because row materialization and prepared scalar count use different public surfaces and should both be protected. For maximum protection, the test data should include at least:

- one ray with effective `tmax < 0.5` and a positive hit;
- one short vertical edge, matching the robot rectangle failure mode;
- one negative short ray to avoid a permissive count-only false positive;
- CPU oracle equality for rows and scalar blocked-ray count.

## Check 4: Goal748 Harness Design

ACCEPT_WITH_NOTES.

I could not inspect `scripts/goal748_optix_robot_scaled_perf.py` or `tests/goal748_optix_robot_scaled_perf_test.py` because they are not present in the fetched Windows clone. Based on the request description, the intended harness design is sound if it explicitly separates:

- CPU oracle validation;
- row materialization cost;
- Embree row output;
- OptiX row output;
- OptiX prepared scalar count;
- preparation/build time versus repeated query time;
- result parity for each backend before timing claims.

This separation is especially important because the bug affected both OptiX row mode and prepared-count mode. A harness that only compares final app summaries could hide which surface is wrong; a harness that records per-surface parity and timing makes the failure actionable.

Recommended harness gates:

- fail or mark invalid if CPU, Embree, OptiX rows, and OptiX prepared count disagree on hit count;
- record setup/preparation separately from per-query traversal/count;
- label GTX 1070 evidence as OptiX/CUDA traversal correctness and whole-call timing only, not RTX RT-core speedup;
- include the exact commit, GPU, driver, OptiX version, and whether native extension was rebuilt.

## Check 5: Public Docs / Report Impact

ACCEPT: docs/reports should be updated.

Prior robot OptiX performance evidence before the short-ray fix should be marked invalid or at least suspect for correctness-sensitive claims. The most direct target is `docs/reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md`, which says Goal509 accepts CPU/Embree/OptiX for robot collision screening and that OptiX is correct but slower than Embree. Given the `5742` versus `3828` mismatch, the pre-fix OptiX robot rows/counts were not correct for the short-edge robot fixture, so the old OptiX robot correctness/performance evidence cannot remain unqualified.

Other docs that reference robot OptiX as an accepted/candidate app should be nuanced rather than deleted:

- `docs/app_engine_support_matrix.md` can continue to call robot collision a flagship OptiX candidate, but should state that pre-fix robot OptiX evidence was invalid/suspect until rerun after the short-ray fix.
- `docs/release_facing_examples.md` references Goal509 accepting CPU/Embree/OptiX for robot collision; this should point to the post-fix rerun or note the correction.
- broader current-main/backend docs already contain useful caveats about no RTX RT-core speedup claim from GTX 1070 evidence. Those caveats are good but do not replace a correctness erratum for robot OptiX rows/counts.

The doc update should distinguish:

- CPU/Embree robot evidence: still usable unless separately contradicted.
- OptiX robot evidence before the fix: correctness-suspect/invalid for short-edge fixtures.
- OptiX robot evidence after the fix and rebuild: usable if the new regression tests and Goal748 parity gates pass.
- GTX 1070 timing: traversal correctness/whole-call evidence only, not RT-core speedup.

## Check 6: Other Hardcoded `optixReportIntersection(0.5f, ...)` Sites

I found these hardcoded sites in the fetched source:

| Site | Risk | Reason |
| --- | --- | --- |
| `src/native/optix/rtdl_optix_core.cpp:699`, `__intersection__lsi_isect` | Low/medium | Raygen uses unnormalized segment direction with `tmax=1.0f + 1e-4`; `0.5` is inside the interval. Still worth future audit because it is a candidate-report path, not a true hit distance. |
| `src/native/optix/rtdl_optix_core.cpp:830`, positive-only PIP | Low | PIP raygen uses vertical direction with huge `tmax=1e30`; `0.5` is in range. |
| `src/native/optix/rtdl_optix_core.cpp:838`, exact PIP | Low | Same huge vertical trace interval; `0.5` is in range. |
| `src/native/optix/rtdl_optix_core.cpp:984`, overlay LSI candidate | Low/medium | Overlay raygen uses polygon edge vector with `tmax=1.0`; `0.5` is in range. Future audit useful for consistency, but it is not the same short-world-length bug. |
| `src/native/optix/rtdl_optix_core.cpp:1129`, 2D ray-triangle hit-count / any-hit | High | This is the target bug: direction is normalized and `tmax=r.tmax*len`; short rays can have `tmax < 0.5`. |
| `src/native/optix/rtdl_optix_core.cpp:1420`, segment-polygon hitcount | High | Same pattern as the target: segment direction is normalized and `tmax=len`; short segments below `0.5` can lose true hits. Mac/Linux status says a later `b0cedf8` commit fixes short segment-polygon reports; that is consistent with this risk. |
| `src/native/optix/rtdl_optix_core.cpp:1792`, DB scan | Low | Trace direction is fixed z and `tmax` is derived from z-span plus padding, so `0.5` should normally be in range. |

Related non-hardcoded site:

- `src/native/optix/rtdl_optix_core.cpp:1664` reports `params.radius` for fixed-radius count. `trace_tmax` is set to `2 * aabb_radius`; this is not the same fixed-`0.5` bug, but future audits should still verify the reported value is always within `[tmin, tmax]` for very small radii.

## Blockers

No blocker for the proposed OptiX short-ray any-hit fix.

Process limitation only: Windows could not inspect the latest Mac/Linux local commits because they are not fetchable from GitHub `origin/main` at the time of review. If Mac/Linux wants a strict file-by-file review of the exact final Goal748 harness and new tests, it should push those commits or place a patch/bundle in the bridge.

## Follow-Up Recommendations

1. Keep the interval-local report fix for 2D ray/triangle any-hit and prepared-count kernels.
2. Apply the same audit/fix pattern to segment-polygon hitcount if not already fully covered by `b0cedf8`.
3. Add a small helper or convention for candidate-only intersection programs: report a guaranteed interval-local synthetic `t` when distance is not semantically used.
4. Update Goal509/public docs with a clear pre-fix OptiX robot correctness erratum.
5. Rerun Goal748 after native rebuild and publish parity-first results before using any robot OptiX timing.
6. When sharing future Windows review requests, include either pushed commits, a git bundle, or patch files in the bridge if Mac/Linux local commits are not yet on GitHub.

## Final Statement

Windows Codex performed review/report work only. No mainline source was modified, no local scratch edits were left in the checkout, and nothing was pushed.
