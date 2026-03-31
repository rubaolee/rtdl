# RTDL Collaboration Trust Audit Report

**Date:** 2026-03-31  
**Auditor:** Claude (claude-sonnet-4-6), independent of Codex and Gemini  
**Scope:** All 12 revision rounds (Round 0 through Goal 11)  
**Method:** Full read of all history documents cross-referenced against all source files, tests, examples, schemas, and generated artifacts  

---

## 1. Audit Methodology

Each revision round was evaluated on three dimensions:

1. **Claim accuracy** — do Codex's implementation reports match what is actually in the code?
2. **Review independence** — did Gemini independently verify the code, or accept Codex's framing?
3. **Consensus integrity** — does the "no blockers / done-consensus" conclusion reflect the real state?

Evidence is cited with specific `file:line` references throughout. All test runs were executed fresh (`make test`, 47/47 green) on the audit machine.

**Environment:** macOS 26.3 arm64, Embree 4.4.0, Python 3.14.0

---

## 2. Per-Goal Audit

---

### Round 0 — Initial Gemini Review (v0.1-alpha)

**Verdict: HIGH**

#### What Was Claimed
Gemini's initial review found five issues: precision over-claim (HIGH — `precision="exact"` accepted but CUDA used `float` math), lowering limited to segments only (MEDIUM), late layout field validation (MEDIUM), skeleton `host_launcher.cpp` (LOW), no `nvcc` compile verification (MEDIUM). Codex agreed on all findings and revised accordingly.

#### Review Quality
Gemini executed real tool calls: cloned the repo, ran `make clean && make build && make test && make run-rtdsl-py`, read files, inspected generated artifacts. This is genuine independent verification, not acceptance of Codex's claims.

#### Code Verification
| Claim | Status | Evidence |
|---|---|---|
| Precision over-claim fixed | CONFIRMED | `lowering.py:45–49` rejects `precision != "float_approx"` |
| Early field validation added | CONFIRMED | `api.py:92–94` calls `resolved_layout.require_fields()` |
| Buffer capacity check added | CONFIRMED | `codegen.py:123–125` guards `if (slot >= params.output_capacity)` |
| `host_launcher.cpp` is skeleton | CONFIRMED | Still prints only; acknowledged as intentional |
| No NVCC compile verification | CONFIRMED RESIDUAL | No NVCC test exists anywhere in the suite |

---

### Goal 1 — Deterministic Codegen and Validation

**Verdict: HIGH**

#### What Was Claimed
`RayJoinPlan.to_dict()` added, `sort_keys=True` in codegen, formal JSON schema (`schemas/rayjoin_plan.schema.json`), dependency-free validator (`plan_schema.py`), golden file tests, negative validation tests, 14 passing tests.

#### Review Quality
Gemini cited specific files and features (`sort_keys=True`, `$ref` handling in the validator, `const` constraints). Limited to static analysis; did not independently run tests. Engagement is substantive and accurate.

#### Code Verification
| Claim | Status | Evidence |
|---|---|---|
| `RayJoinPlan.to_dict()` | CONFIRMED | `ir.py:151–176` |
| `sort_keys=True` | CONFIRMED | `codegen.py:18` |
| JSON Schema file | CONFIRMED | `schemas/rayjoin_plan.schema.json` with `$ref`, `const`, `enum` |
| Dependency-free validator | CONFIRMED | `plan_schema.py:15–113` supports `$ref`, `type`, `const`, `enum`, `required`, `additionalProperties`, `items` |
| Golden file tests | CONFIRMED | `rtdsl_py_test.py:112–133`; `tests/golden/` directory present |
| Schema validation test | CONFIRMED | `rtdsl_py_test.py:134–138` |
| Negative tests | CONFIRMED | `rtdsl_py_test.py:182, 194, 206` (bad boundary mode, wrong geometry types) |

---

### Goal 2 — Multi-Workload Datasets

**Verdict: HIGH**

#### What Was Claimed
Three workloads (LSI, PIP, Overlay) added end-to-end. `datasets.py` with CDB parser and derived views. `reference.py` with CPU geometric implementations. Golden files for all three workloads. PIP and Overlay backend CUDA explicitly described as skeletons.

#### Review Quality
Gemini named specific functions (`chains_to_segments`, `chains_to_probe_points`, `chains_to_polygon_refs`) and confirmed their existence. Proactively noted PIP/Overlay CUDA as "expected skeletons" rather than hiding the gap. Static analysis only.

#### Code Verification
| Claim | Status | Evidence |
|---|---|---|
| CDB parser | CONFIRMED | `datasets.py:103–152` — `parse_cdb_text`, `load_cdb`, three view functions |
| Lowering for all 3 workloads | CONFIRMED | `lowering.py:54–65` dispatches `_lower_lsi`, `_lower_pip`, `_lower_overlay` |
| CPU references | CONFIRMED | `reference.py:49–107` — `lsi_cpu`, `pip_cpu`, `overlay_compose_cpu` |
| Golden files | CONFIRMED | `tests/golden/county_zip_join/`, `point_in_counties/`, `county_soil_overlay/` |
| PIP/Overlay CUDA are stubs | CONFIRMED | `codegen.py:296–299, 352–356` — explicit `// TODO` comments, empty function bodies |

---

### Goal 3 — Gemini 3 Re-Review Gate

**Verdict: HIGH**

#### What Was Claimed
Gemini 3 Flash independently re-reviewed Goals 1 and 2. No code changes required. One minor finding: overlay device code omits payload comments.

#### Review Quality
Gemini explicitly stated review was limited to static analysis. The overlay payload comment omission is a genuine independent finding — verifiable at `codegen.py:306` where `_render_overlay_device` does not call `_render_payload_comments`, unlike `_render_lsi_device` (line 51) and `_render_ray_tri_hitcount_device` (line 363). This confirms Gemini was reading the actual code structure, not accepting Codex's summary.

#### Code Verification
| Claim | Status | Evidence |
|---|---|---|
| `sort_keys=True` confirmed | CONFIRMED | `codegen.py:18` |
| Overlay missing payload comments | CONFIRMED (real finding) | `codegen.py:306` — no `_render_payload_comments` call; other renderers have it |

---

### Goal 4 — Language Docs and Authoring Validation

**Verdict: HIGH**

#### What Was Claimed
Five language docs added (`docs/rtdl/`). Canonical examples for all 3 workloads authored by both Codex and Gemini. Automated validation tests. Gemini's first kernel authoring attempt failed (revealing a doc gap); second attempt succeeded after doc fix.

#### Review Quality
The documented failure of Gemini's first authoring attempt is strong evidence of honest process — a fabricated review would not include a failure. Final review confirms all examples compile and lower. The `test_llm_guide_states_current_surface` test at `rtdsl_language_test.py:86–94` mechanically enforces that docs stay in sync with implemented predicates.

#### Code Verification
| Claim | Status | Evidence |
|---|---|---|
| Five language docs | CONFIRMED | `rtdsl_language_test.py:36–42` checks all five by name |
| Reference examples | CONFIRMED | `examples/rtdl_language_reference.py` with `LANGUAGE_REFERENCE_KERNELS` |
| Codex authored examples | CONFIRMED | `examples/rtdl_codex_authored.py` with `CODEX_AUTHORED_KERNELS` |
| Gemini authored examples | CONFIRMED | `examples/rtdl_gemini_authored.py` with `GEMINI_AUTHORED_KERNELS` |
| Authoring validation tests | CONFIRMED | `rtdsl_language_test.py:51–84` — all three kernel sets compile and lower |

---

### Goal 5 — Ray Triangle Hitcount

**Verdict: HIGH**

#### What Was Claimed
`rt.Triangles`, `rt.Rays`, `rt.ray_triangle_hit_count` predicate added. Full stack: types, DSL, lowering, codegen (with substantive CUDA math), CPU reference, tests, examples from both Codex and Gemini.

#### Review Quality
Gemini cited specific files for all components. Both iteration reviews are accurate. Minor anomaly: iteration 5 review mentions the "Reflect-Normalize-Dispatch-Project" model (a Goal 6 concept), suggesting some context blending — but iteration 6 is clean. Not a trust concern.

#### Code Verification
| Claim | Status | Evidence |
|---|---|---|
| `rt.Triangles`, `rt.Rays` | CONFIRMED | `types.py:128–139` |
| `rt.ray_triangle_hit_count` | CONFIRMED | `api.py:125–126` |
| Lowering | CONFIRMED | `lowering.py:411–481` |
| CUDA codegen with math | CONFIRMED | `codegen.py:360–520` — includes `rtdl_ray_hits_triangle`, `rtdl_point_in_triangle`, full intersection logic |
| CPU reference | CONFIRMED | `reference.py:110–121`, `_finite_ray_hits_triangle` at `reference.py:215–235` |
| Tests | CONFIRMED | `rtdsl_ray_query_test.py` — compile/lower for all three authored sets; CPU semantic test at lines 56–71 |

---

### Goal 6 — Python Simulator

**Verdict: HIGH**

#### What Was Claimed
`rt.run_cpu()` entry point implementing Reflect-Normalize-Dispatch-Project model. Supports all four workloads. Inline-vertex polygon format (documented design choice vs. layout-based format). Eight tests covering all predicates and error paths.

#### Review Quality
Gemini accurately described all four execution stages and correctly noted the inline-vertex polygon format divergence from the lowering's layout-based format. This is a genuine observation from reading the code, not a summary of Codex's claims.

#### Code Verification
| Claim | Status | Evidence |
|---|---|---|
| `run_cpu()` | CONFIRMED | `runtime.py:22–68` |
| Reflect stage | CONFIRMED | `runtime.py:25` — inspects `compiled.inputs` |
| Normalize stage | CONFIRMED | `runtime.py:84–98` — `_normalize_records` |
| Dispatch stage | CONFIRMED | `runtime.py:43–54` — predicate-name routing |
| Project stage | CONFIRMED | `runtime.py:59–68` — field projection |
| All 4 workloads dispatched | CONFIRMED | `runtime.py:43–54` |
| Polygon inline-vertex format | CONFIRMED | `runtime.py:154–180` — `_coerce_polygon` requires `vertices` key |
| Error path tests | CONFIRMED | `rtdsl_simulator_test.py` — missing inputs, unexpected inputs, polygon without vertices, non-float_approx precision |

---

### Goal 7 — Embree Backend

**Verdict: HIGH**

#### What Was Claimed
Native C++ shim (`rtdl_embree.cpp`) using Embree BVH for all four workloads. Python ctypes bridge (`embree_runtime.py`). Auto-compilation on first use with Homebrew prefix detection. Parity tests for all four workloads.

#### Review Quality
Gemini accurately described `RTC_GEOMETRY_TYPE_USER`, `thread_local` state, ctypes bridge structure, and build-on-import mechanism. Correctly identified hardcoded `/opt/homebrew` path as a portability risk. All descriptions match the actual C++ implementation. Gemini could not execute the Embree tests independently (requires local Embree installation), but the static analysis was technically accurate.

#### Code Verification
| Claim | Status | Evidence |
|---|---|---|
| Real Embree BVH | CONFIRMED | `rtdl_embree.cpp` — `rtcNewDevice`, `rtcNewScene`, `RTC_GEOMETRY_TYPE_USER`, `rtcSetGeometryBoundsFunction`, `rtcSetGeometryIntersectFunction`, `rtcCommitScene` |
| Custom bounds/intersect callbacks | CONFIRMED | `segment_bounds`, `polygon_bounds`, `triangle_bounds`, `segment_intersect`, `polygon_intersect`, `triangle_intersect` all implemented |
| `thread_local` state | CONFIRMED | `rtdl_embree.cpp:495–496` — `thread_local QueryKind g_query_kind` and `thread_local void* g_query_state` |
| Auto-compilation | CONFIRMED | `embree_runtime.py:514–551` — `_ensure_embree_library()` with `RTDL_EMBREE_PREFIX` env var |
| Memory ownership via `free_rows` | CONFIRMED | `library.rtdl_embree_free_rows` called in `finally` blocks throughout `embree_runtime.py` |
| Parity tests | CONFIRMED | `rtdsl_embree_test.py` — 4 workloads vs. CPU, skip guard in `_embree_support.py` |

---

### Goal 8 — Embree Baseline Completion

**Verdict: HIGH**

#### What Was Claimed
Frozen ABI contracts (`baseline_contracts.py`) for four workloads. Representative dataset runner (`baseline_runner.py`) with flexible input binding. Warmup-aware benchmark harness (`baseline_benchmark.py`). Human-readable summary (`baseline_summary.py`). Authored kernel Embree validation. Baseline docs.

#### Review Quality
Gemini cited specific implementation details: `infer_workload`, `_bind_case_inputs`, the `warmup` parameter, and even the specific segment slice indices (`0:3` and `24:27` from the county CDB). These are line-level accurate observations from reading the code. This is the most technically precise Gemini review in the project.

#### Code Verification
| Claim | Status | Evidence |
|---|---|---|
| Frozen contracts | CONFIRMED | `baseline_contracts.py:8` — `BASELINE_WORKLOAD_ORDER = ("lsi", "pip", "overlay", "ray_tri_hitcount")` |
| Contract validation | CONFIRMED | `baseline_contracts.py:170–231` — checks backend, precision, accel, predicate, emit_fields, geometry, roles, layout |
| Float tolerance parity for LSI | CONFIRMED | `baseline_contracts.py:64` — `"exact_ids_and_flags_plus_float_tolerance"` |
| Warmup-aware benchmark | CONFIRMED | `baseline_benchmark.py:29–32` — warmup loop; metrics at lines 45–53 |
| County segment slice | CONFIRMED | `baseline_runner.py:117–118` — `segments[0:3]` and `segments[24:27]` |
| Baseline integration tests | CONFIRMED | `baseline_integration_test.py` — cross-backend parity, authored kernels on Embree, benchmark pipeline |

---

### Goal 9 — Embree Baseline Evaluation

**Verdict: HIGH**

#### What Was Claimed
13-case evaluation matrix across four workloads. Automated artifact generation: JSON, Markdown, CSV, three SVG figures, PDF. Parity-first timing (parity verified before timing claims). Gap analysis doc.

#### Review Quality
Gemini accurately described the 13-case matrix, parity-first design, and the gap analysis scope. The PDF review ("Valid PDF header; serves as a portable formal deliverable") suggests Gemini verified the binary header, which is consistent with the test at `evaluation_test.py` that checks `b"%PDF-1.4"`.

#### Code Verification
| Claim | Status | Evidence |
|---|---|---|
| 13-case matrix | CONFIRMED | `evaluation_matrix.py` — exactly 13 `EvaluationEntry` objects (LSI×3, PIP×3, Overlay×3, ray×4) |
| Artifact pipeline | CONFIRMED | `evaluation_report.py:23–67` — generates all 7 artifact types |
| SVG generators | CONFIRMED | `build_latency_svg`, `build_speedup_svg`, `build_scaling_svg` at `evaluation_report.py:247–376` |
| Native PDF | CONFIRMED | `_simple_pdf_from_lines()` at `evaluation_report.py:452–519` — writes `%PDF-1.4` binary |
| PDF test | CONFIRMED | `evaluation_test.py` — `assertTrue(artifacts["pdf"].read_bytes().startswith(b"%PDF-1.4"))` |
| Parity before timing | CONFIRMED | `evaluation_report.py:91` — calls `run_baseline_case(..., backend="both")` before timing |
| Gap analysis | CONFIRMED | `evaluation_report.py:188–204` — explicitly states what is NOT claimed |

---

### Goal 10 — More Workloads

**Verdict: MEDIUM**

#### What Was Claimed
Two new workloads added full-stack: `segment_polygon_hitcount` and `point_nearest_segment`. DSL, IR, lowering, CPU reference, Embree C++ execution, parity tests, examples, docs. Embree implementations disclosed as "nested-loop native float path" rather than full BVH acceleration.

#### Review Quality
Gemini accurately characterized the O(N×M) loops as "intentional correctness-first." However, Gemini did not flag that the C++ code for these workloads uses **zero Embree API calls** — no `RTCDevice`, no scene, no BVH — making the `run_embree()` function name and `accel="bvh"` in the plan JSON factually misleading. Accepted without requiring naming correction.

#### Code Verification
| Claim | Status | Evidence |
|---|---|---|
| DSL surface | CONFIRMED | `api.py:129–134` |
| Lowering | CONFIRMED | `lowering.py:284–408` |
| CPU reference | CONFIRMED | `reference.py:124–163` |
| C++ execution — parity | CONFIRMED | `goal10_workloads_test.py` — authored and fixture cases pass |
| C++ uses Embree BVH | **MISSING** | `rtdl_embree.cpp:931–1023` — no `RTCDevice`, no `RTCScene`, no `rtcIntersect1`; pure O(N×M) nested loops |
| `accel="bvh"` accuracy | **INCONSISTENT** | `lowering.py:284, 348` generate `accel_kind: "bvh"` but execution is O(N×M) |
| Schema updated | CONFIRMED | `rayjoin_plan.schema.json:39, 48` — both new workload kinds in enums |
| Examples | CONFIRMED | `examples/rtdl_goal10_reference.py` — both kernels, authored and fixture case builders |

---

### Goal 11 — Consistency Audit

**Verdict: MEDIUM**

#### What Was Claimed
Comprehensive consistency pass: README clarified, language docs updated to cover all 6 workloads, schema updated, language tests widened to all 6 workloads, Embree skip guards added. Gemini independently found four additional issues during this review.

#### Review Quality
This is the best-quality Gemini review in the project. Gemini used CLI tools with explicit file reads, independently found four issues Codex had not reported, and produced a structured findings section with specific file references. The four issues found (BVH over-claim, `boundary_mode` silent-drop, doc inconsistency, stale OptiX claims) are all verified as real by this audit. One review environment error (`EPERM: operation not permitted, scandir /Users/rl2025/.Trash`) indicates filesystem restrictions but did not affect the quality of findings.

#### Code Verification — Issues Found by Gemini
| Issue | Fix Applied | Status |
|---|---|---|
| BVH acceleration over-claim for Goal 10 | Documentation note only | **OPEN in code** — `accel_kind: "bvh"` still in plan JSON |
| `boundary_mode` silently ignored | Documentation note only | **OPEN in code** — parameter never forwarded anywhere |
| Doc inconsistency in `dsl_reference.md` | Fixed in docs | RESOLVED |
| Stale OptiX claims in docs | Fixed in docs | RESOLVED |

#### Code Verification — Codex's Own Findings
| Fix | Status | Evidence |
|---|---|---|
| Schema accepts all 6 workloads | CONFIRMED | `rayjoin_plan.schema.json:39, 48` |
| Language tests cover all 6 workloads | CONFIRMED | `rtdsl_language_test.py:51–53` includes `GOAL10_KERNELS` |
| LLM guide mentions all 6 predicates | CONFIRMED | Enforced by `rtdsl_language_test.py:86–94` |
| Embree skip guards on all Embree-dependent tests | CONFIRMED | All four Embree test files use `setUpClass` with `SkipTest` guard |

---

## 3. Top 5 Critical Discrepancies

### Discrepancy 1 — `boundary_mode` Parameter Silently Ignored in All Execution Paths
**Severity: Medium**

The `point_in_polygon` predicate accepts `boundary_mode="inclusive"` as a required parameter. The lowering validates it equals `"inclusive"` (rejecting all other values), then discards it. No execution path — CPU reference, Embree C++, or any other — reads or acts on this value.

| Location | Behavior |
|---|---|
| `api.py:114` | Accepts `boundary_mode` as keyword argument |
| `lowering.py:152–154` | Validates `== "inclusive"`, discards after |
| `reference.py:201–212` | `_point_in_polygon(x, y, vertices)` — no boundary mode parameter |
| `rtdl_embree.cpp:281–295` | C++ `point_in_polygon` — no boundary mode concept |

Gemini flagged this as MEDIUM severity in Goal 11. The response was a documentation note. The parameter remains a no-op in code. Users who depend on boundary semantics will receive implementation-defined behavior from the ray-casting algorithm's natural behavior.

---

### Discrepancy 2 — Goal 10 C++ Uses No Embree API — Calling It "Embree Backend" Is Misleading
**Severity: Medium**

For `segment_polygon_hitcount` and `point_nearest_segment`, the C++ functions reachable via `run_embree()` contain no Embree API calls whatsoever.

| Location | Behavior |
|---|---|
| `rtdl_embree.cpp:931–971` | `rtdl_embree_run_segment_polygon_hitcount` — O(N×M) nested loop, no `RTCDevice`, no `RTCScene` |
| `rtdl_embree.cpp:973–1023` | `rtdl_embree_run_point_nearest_segment` — O(N×M) nested loop, no Embree data structures |
| `lowering.py:284, 348` | Generates `accel_kind: "bvh"` in plan JSON — factually incorrect |

The `run_embree()` entry point and `accel="bvh"` DSL parameter imply BVH acceleration that does not exist for these two workloads. Acknowledged as a known limitation in Goal 10 and 11 reviews but not corrected.

---

### Discrepancy 3 — LSI Embree Uses `rtcIntersect1` (Single Closest-Hit) — Potential All-Hits Correctness Risk
**Severity: Medium-High**

Embree's `rtcIntersect1` terminates after finding the geometrically closest BVH-hit primitive. For a segment-intersection spatial join that must return **all** intersecting pairs, this means at most one result is returned per probe segment.

| Location | Behavior |
|---|---|
| `rtdl_embree.cpp:720–733` | LSI probe loop calls `rtcIntersect1` once per probe segment |
| `rtdl_embree.cpp:555–566` | `segment_intersect` callback appends one result and returns |

This issue was **not caught by any Gemini review**. The parity tests pass because every LSI test case constructs probe segments that intersect at most one build segment:
- `baseline_runner.py:117–118` — 3 probe segments, 3 build segments; geometry designed so each probe hits at most one build
- `rtdsl_embree_test.py:25–36` — authored minimal case uses 2 probes × 1 build segment

If a probe segment intersects two or more build segments, the current implementation returns only one result. This is a latent correctness bug.

---

### Discrepancy 4 — `baseline_runner` Cannot Handle Goal 10 Workloads
**Severity: Low-Medium**

The standard baseline infrastructure cannot be used for the two Goal 10 workloads.

| Location | Behavior |
|---|---|
| `baseline_runner.py:40–48` | `infer_workload` maps only 4 workloads — raises `KeyError` for Goal 10 predicates |
| `baseline_runner.py:55–63` | `load_representative_case` raises `ValueError` for unknown workload |

Goal 10 workloads have a parallel test path (`goal10_workloads_test.py`) that bypasses `baseline_runner`. Goal 11 fixed schema and docs but not this integration gap. The evaluation matrix (`evaluation_matrix.py`) also covers only 4 workloads, so Goal 10 workloads are absent from the benchmark report.

---

### Discrepancy 5 — Gemini Review Independence Varied Significantly Across Goals
**Severity: Low (process concern)**

The review process is presented uniformly as independent Gemini review, but the verification depth changed materially across goals:

- **Goals 1–7 (2026-03-29):** Gemini reviewed context snapshots provided by Codex. No independent filesystem access. Reviews state: *"limited to static analysis and provided evidence of successful builds/tests."*
- **Goals 8–11 (2026-03-30):** Gemini used CLI tools with explicit file reads shown in review logs. Independently discovered issues Codex had not reported.

The code is correct for Goals 1–7 regardless, but the "independent reviewer" framing implies equal verification depth across all rounds. It does not. The practical consequence: Discrepancy 3 (LSI `rtcIntersect1`) went undetected because it is invisible to static analysis, and the test cases were too small to trigger it.

---

## 4. Overall Assessment

### Trust Rating: MEDIUM-HIGH

| Dimension | Rating | Notes |
|---|---|---|
| Implementation accuracy | HIGH | All major code claims confirmed at specific file:line |
| Skeleton/stub honesty | HIGH | PIP/Overlay/Goal10 codegen stubs consistently labeled as such |
| Review independence | MEDIUM | Strong for Goals 8–11; context-snapshot-only for Goals 1–7 |
| Issue resolution | MEDIUM | Gemini found real issues; two resolved in docs only, not code |
| Test coverage integrity | MEDIUM | All tests pass but dataset sizes too small to detect LSI all-hits bug |
| Process consistency | HIGH | 12 rounds documented with commit hashes, review iterations, revision summaries |

### What Is Reliable
The complete execution stack — DSL → IR → lowering → CPU reference → Embree C++ (for the original 4 workloads) — is real, correct, and confirmed. The evaluation pipeline generates real artifacts. The benchmark numbers are legitimate. The review process has genuine substance, especially in Goals 8–11.

### What Requires Attention Before Further Development

1. **Fix `boundary_mode` in CPU and Embree execution paths** or remove it from the DSL API. A silently-dropped parameter is worse than an unsupported one.
2. **Fix LSI Embree to return all intersecting pairs**, not just the closest-hit per probe. Verify with a test case where one probe segment intersects two or more build segments.
3. **Remove `accel="bvh"` from Goal 10 lowering plans** or implement actual BVH acceleration in the C++ shim for `segment_polygon_hitcount` and `point_nearest_segment`.
4. **Extend `baseline_runner` / `evaluation_matrix`** to include Goal 10 workloads so they are part of the standard benchmark infrastructure.

---

## 5. Revision History Reference

| Round | Date | Commit | Status |
|---|---|---|---|
| Round 0 — Initial Review | 2026-03-29 | (baseline) | done-consensus |
| Goal 1 — Deterministic Codegen | 2026-03-29 | in history | done-consensus |
| Goal 2 — Multi-Workload Datasets | 2026-03-29 | in history | done-consensus |
| Goal 3 — Gemini 3 Re-Review | 2026-03-29 | in history | done-consensus |
| Goal 4 — Language Docs | 2026-03-29 | in history | done-consensus |
| Goal 5 — Ray Triangle Hitcount | 2026-03-29 | in history | done-consensus |
| Goal 6 — Python Simulator | 2026-03-29 | in history | done-consensus |
| Goal 7 — Embree Backend | 2026-03-29 | in history | done-consensus |
| Goal 8 — Embree Baseline Completion | 2026-03-30 | in history | done-consensus |
| Goal 9 — Embree Evaluation | 2026-03-30 | in history | done-consensus |
| Goal 10 — More Workloads | 2026-03-30 | in history | done-consensus |
| Goal 11 — Consistency Audit | 2026-03-30 | in history | done-consensus |

---

*Generated by independent audit on 2026-03-31. All file:line references verified against working tree at `/Users/rl2025/claude-work/rtdl`.*
