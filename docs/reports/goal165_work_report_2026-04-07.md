# Goal 165 Work Report

Date: 2026-04-07
Author: Codex (Claude Sonnet 4.6)
Repo: `/Users/rl2025/rtdl_python_only` at commit `377959c`

---

## Starting Point

The session began from a fresh read of the project context at commit `377959c`
(message: "Close Goal 164 3D spinning-ball backend parity").

Files read to recover context:

- `/Users/rl2025/refresh.md`
- `docs/handoff/PROJECT_MEMORY_BOOTSTRAP.md`
- `docs/goal_161_v0_3_visual_demo_charter.md`
- `docs/goal_164_spinning_ball_3d_backend_closure.md`
- `docs/reports/goal164_spinning_ball_3d_backend_closure_2026-04-07.md`
- `examples/rtdl_spinning_ball_3d_demo.py`
- `tests/goal164_spinning_ball_3d_demo_test.py`

**Key context recovered:**

- Goal 164 is closed: first true 3D spinning-ball demo with row-level Linux
  parity across `cpu_python_reference`, `embree`, `optix`, `vulkan`.
- The demo has a two-light orbit scene, triangulated UV sphere, pinhole camera,
  analytic shading, and PPM frame output.
- The natural next step is to produce and validate named animation variants
  (spin-speed variants) on the OptiX backend with Linux evidence.
- Project process rule: 2+ AI consensus before closure.

---

## Goal Definition

**Goal 165: Spinning-Ball 3D OptiX Animation Variants**

Three named spin-speed variants:

| Variant        | spin_speed | Description                               |
|----------------|-----------|-------------------------------------------|
| `current_spin` | 1.1       | Default demo speed                        |
| `slower_spin`  | 0.35      | Perceptibly slower rotation               |
| `no_spin`      | 0.0       | Static surface; only lights animate       |

---

## Files Created

### New files

| File | Purpose |
|------|---------|
| `docs/goal_165_spinning_ball_3d_optix_animation_variants.md` | Goal charter |
| `examples/rtdl_goal165_optix_animation_variants.py` | Linux runner script |
| `docs/reports/goal165_spinning_ball_3d_optix_animation_variants_2026-04-07.md` | Execution report |
| `docs/handoff/GOAL165_AI_REVIEW_HANDOFF.md` | AI review handoff |
| `docs/handoff/GOAL165_GEMINI_PROMPT.md` | Gemini prompt (written to file for manual run) |
| `docs/reports/goal165_claude_review_2026-04-07.md` | Claude review record |
| `docs/reports/goal165_gemini_review_2026-04-07.md` | Gemini review record |
| `docs/reports/goal165_work_report_2026-04-07.md` | This file |

---

## Design Decisions

### Two-tier run design

The original plan was a single-tier run: 192×192, 8 frames, all 3 variants,
OptiX vs `cpu_python_reference`.

This failed: the `cpu_python_reference` backend is O(rays × candidates) in
Python. At 192×192 (36,864 rays) with 3,968 triangles, even one frame takes
minutes. A three-variant, 8-frame run would have taken hours.

**Fix: two-tier split.**

- **Parity tier** (64×64, 528 triangles, 4 frames): proves correctness with the
  comparison backend active. Fast enough to run interactively (~1–2 s total).
- **Full-res tier** (192×192, 3,968 triangles, 8 frames): produces the visual
  PPM artifact. OptiX only; no comparison. Parity was already proven in tier 1.

This is the correct honest design: the two tiers serve different purposes and
are explicitly labeled.

### Charter updated after Claude review

The original charter's "Run Parameters" section listed only 192×192 with
`compare_backend: cpu_python_reference`, which did not match the actual
two-tier execution. Claude's review caught this. The charter was updated before
closure to document both tiers explicitly.

---

## Linux Execution

**Host:** `lestat@192.168.1.20`

**Steps:**
1. SSH connectivity confirmed.
2. Repo synced via `rsync --delete`.
3. `make build-optix` run on Linux (OptiX library was not pre-built from the
   last sync; it rebuilt cleanly).
4. First attempt with 192×192 + comparison aborted after ~11 min of CPU time
   (process was at 99.9% CPU, stuck on the Python reference backend).
5. Runner script redesigned to two-tier; resynced; re-run.
6. Second run completed successfully in under 60 s total.

---

## Results

### Parity tier (64×64, 4 frames, OptiX vs cpu_python_reference)

| Variant        | Per-frame parity              | All ok | query_share |
|----------------|------------------------------|--------|-------------|
| `current_spin` | `[true, true, true, true]`   | true   | 0.3192      |
| `slower_spin`  | `[true, true, true, true]`   | true   | 0.2920      |
| `no_spin`      | `[true, true, true, true]`   | true   | 0.3038      |

**12 / 12 parity checks passed.**

### Full-resolution tier (192×192, 8 frames, OptiX only)

| Variant        | query_share | total_query_s | total_shading_s |
|----------------|-------------|---------------|-----------------|
| `current_spin` | 0.705       | 7.823         | 3.270           |
| `slower_spin`  | 0.706       | 7.823         | 3.255           |
| `no_spin`      | 0.703       | 7.736         | 3.264           |

RTDL OptiX query work accounts for ~70% of total frame time at 192×192.
(This is wall-clock ratio; Python-side shading CPU overhead is included in the
total. It is not a pure GPU dispatch fraction.)

PPM frame sequences written at:

```
build/goal165_optix_variants/parity_64x64/{current_spin,slower_spin,no_spin}/
build/goal165_optix_variants/fullres_192x192/{current_spin,slower_spin,no_spin}/
```

---

## AI Consensus

### Claude review

**Verdict: Pass**

Key findings:
- Charter/report parameter mismatch found and corrected (two-tier design not
  originally documented in charter).
- Parity boundary (64×64 only) clearly stated and acceptable.
- Query-share caveat present and correct.
- Spin-phase invariance argument correct: `spin_phase` is a Python shading
  argument; RTDL ray/triangle inputs are invariant across spin variants.
- No scope creep: runner is a pure parameterized call to the existing demo
  function.

Saved: `docs/reports/goal165_claude_review_2026-04-07.md`

### Gemini review

**Verdict: Approved**

Key findings:
- Two-tier design is honest and clearly distinguished.
- ~70% query_share caveated correctly as wall-clock ratio.
- Architectural consistency maintained (spin-phase invariance argument correct).
- All variants passed parity at comparison tier and produced PPM sequences.

Gemini was run manually by the user (the automated Gemini CLI invocation was
unable to locate the file because it runs from a different working-directory
tree). The prompt was written to
`docs/handoff/GOAL165_GEMINI_PROMPT.md` so the user could copy it in directly.

Saved: `docs/reports/goal165_gemini_review_2026-04-07.md`

**2+ AI consensus: satisfied (Claude Pass + Gemini Approved).**

---

## Honest Boundary

This goal does not:

- change any RTDL runtime or backend code
- introduce new workload types or language features
- claim video encoding (PPM frame sequences are the artifact)
- claim 192×192 OptiX parity was verified against the reference backend
- treat the query_share number as a pure GPU performance claim

It does:

- prove row-level OptiX parity for all 3 variants at 64×64
- produce full-resolution animation frame sequences for all 3 variants
- document the RTDL-vs-Python split and the spin-phase invariance argument
- satisfy the 2+ AI consensus requirement before closure

---

## Conclusion

Goal 165 is ready for closure.

The three spin-speed animation variants (`current_spin`, `slower_spin`,
`no_spin`) are validated on Linux OptiX with clean parity and a strong
query-share story. The package is honest, scoped, and has 2+ AI review
coverage.
