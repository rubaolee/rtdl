# RTDL v0.3 — External Usage Test Report

**Date:** 2026-04-09
**Scope:** Release-facing usability and correctness check from the perspective of a new technical user.
**Method:** Fresh remote read of all front-door docs and source files via GitHub (`rubaolee/rtdl`, `main` branch). Live code execution was not possible from the review environment (isolated sandbox unavailable); issues requiring a running interpreter are noted explicitly.

---

## Verdict

**Not ready for external release without fixes.**

The core RTDL v0.2 workload surface and documentation framing are solid and honest. The four accepted workloads (`segment_polygon_hitcount`, `segment_polygon_anyhit_rows`, `polygon_pair_overlap_area_rows`, `polygon_set_jaccard`) are clearly described, their boundaries are explicitly stated, and the distinction between RTDL-as-geometric-query-core and the visual demo as a proof-of-capability layer is well-maintained throughout the docs.

What blocks release is not the code — it is the repo presentation. A new technical user cloning `main` today will hit a broken copy-paste command on the most prominent example page, will find no dependency or install instructions anywhere, will see internal machine names in a public support matrix, and will encounter internal goal-tracking file names leaking into release-facing imports. These are concrete release blockers, not polish items.

---

## Friction Points

### 1. `release_facing_examples.md` uses a broken placeholder path

Every run command in the canonical example index reads:

```bash
cd /path/to/rtdl_python_only
```

The repo is cloned as `rtdl` (`git clone https://github.com/rubaolee/rtdl.git`). The string `/path/to/rtdl_python_only` is a stale internal placeholder that was never updated. A new user copy-pasting any command from this page will hit a `No such file or directory` error immediately. The main README and quick tutorial correctly say `cd rtdl`, making the inconsistency worse. This is the page linked from the main README as the canonical place to find examples.

### 2. No dependency or installation instructions anywhere

There is no `requirements.txt`, `pyproject.toml`, or `setup.py` in the repository. The public docs never state what Python packages are required (e.g. `numpy` is imported as an optional fast-path in the visual demo), what Python version is required, or how to install any native dependencies (Embree, OptiX SDK, Vulkan SDK, GEOS/PostGIS). A new user on a fresh machine does `git clone` and has no idea what to `pip install` before any command will succeed.

### 3. The package is named `rtdsl` but the repo is named `rtdl`, and this is never explained

Every example file begins with `import rtdsl as rt`. A user who cloned `rtdl` and looks at the first line of any example will wonder: is `rtdsl` a PyPI package? A local package? The docs never surface this distinction. The `PYTHONPATH=src:.` prefix resolves it silently, but that mechanism is never explained as the thing making `rtdsl` importable from `src/rtdsl/`.

### 4. `PYTHONPATH=src:.` is required on every command but never explained

New users see this prefix on every quick-start and example command, but the docs never explain why it is necessary, whether there is a `pip install -e .` alternative, or what error they will get if they forget it. Running `python3 examples/rtdl_hello_world.py` directly without the prefix produces `ModuleNotFoundError: No module named 'rtdsl'` with no hint on how to fix it.

### 5. Release-facing examples import from an internal goal-numbered file

The primary workload example `rtdl_segment_polygon_hitcount.py` contains:

```python
from examples.reference.rtdl_goal10_reference import segment_polygon_hitcount_reference
```

`rtdl_goal10_reference.py` is an internal development artifact with a goal-tracking name. It is exposed to external users without explanation. A new user following the import chain lands in a file that reads as internal scaffolding.

### 6. The `examples/` directory mixes release-facing and internal files with no separation

Alongside the four documented release-facing examples, a fresh `ls examples/` reveals: `rtdl_codex_authored.py`, `rtdl_gemini_authored.py`, `rtdl_gemini_embree_program.py`, `rtdl_gemini_ray_query.py`, `rtdl_codex_ray_query.py`, `rtdl_goal97_agent_variant_a.py`, `rtdl_goal97_agent_variant_b.py`, `rtdl_goal165_optix_animation_variants.py`, `rtdl_sorting.py`, `rtdl_simulator_demo.py`, and others. There is no README or label in `examples/` telling a new user which files are release-facing and which are internal process artifacts. The goal-numbered and AI-model-named files read as internal development history, not as user-facing material.

### 7. The support matrix names a private internal machine

`docs/release_reports/v0_2/support_matrix.md` lists the primary validation platform as:

> `Linux (lestat@192.168.1.20 and clean-clone equivalents)`

A private hostname and username appear in a public release document. Any external reviewer reading the support matrix will immediately identify this as an unreviewed internal artifact.

### 8. The Makefile exposes internal development targets to every user

Targets including `run-goal15-compare`, `run-goal18-compare`, `run-goal19-compare`, `run-goal23-reproduction`, `eval-section-5-6-publish-2026-03-31`, `report-rtdl-paper`, and `report-goal14-section-5-6-estimate` are all visible when a new user runs `make` or reads the Makefile. There is no documented distinction between user-facing and internal targets.

### 9. Two internal status artifacts sit at the repo root

A fresh `ls` of the cloned repo shows `rtdl_status_summary.js` and `rtdl_status_summary.pptx` at the top level. Neither is mentioned in the README. They look like internal process documents and are the first thing a new user sees after cloning.

### 10. The visual demo has no quick-test invocation in the docs

`rtdl_smooth_camera_orbit_demo.py` defaults to 320 frames at 1024×1024. On the CPU Python reference backend, this will take an extremely long time. The docs point users to this script but never provide a small invocation (e.g. `--frames 4 --width 240 --height 240 --backend cpu_python_reference`) for a first sanity check. The script also imports from `rtdl_orbiting_star_ball_demo.py` without documenting this dependency chain.

### 11. The `build/` directory is required but not created for direct script runs

The lit ball demo command in `release_facing_examples.md` writes to `build/rtdl_lit_ball_demo_hq.pgm`. In a fresh clone, `build/` does not exist. The Makefile creates it via `mkdir -p $(BUILD_DIR)`, but a user following the documented Python command directly will get a `FileNotFoundError` on output. This is not mentioned anywhere.

### 12. v0.3 version identity is unclear at clone time

The handoff asks for a "v0.3 external test," but the repo has no v0.3 tag, no v0.3 release docs, and no v0.3 support matrix. The main README explains the two-layer model (v0.2.0 stable workload surface + v0.3 application/demo proof on top), but a new user cloning `main` has no immediate way to confirm which version they are running. A version string, a `version.py`, or a visible tag would resolve this.

---

## Release Risks

**Broken copy-paste on the most prominent example page.** The `/path/to/rtdl_python_only` placeholder in `release_facing_examples.md` will cause immediate failure for any user following the canonical example index. This page is the first place the main README sends users who want runnable examples.

**Zero dependency guidance.** A user on a fresh machine cannot know what to install before the first command succeeds. If `numpy` is absent the visual demo emits a warning and falls back. If GEOS or native libraries are missing, native backends fail with cryptic C-level errors. No front-door doc mentions any of this.

**`rtdl` vs `rtdsl` mismatch with no explanation.** A user who infers from `import rtdsl` that they should `pip search rtdsl` or `pip install rtdsl` will find nothing and be stuck with no recovery path documented.

**Internal example files will generate confused questions.** A new user who sees `rtdl_gemini_authored.py` or `rtdl_codex_ray_query.py` in the examples directory will try to run them or ask what they are. Their presence implies these are user-facing patterns, which they are not.

**`lestat@192.168.1.20` in a public release document.** Any external reviewer reading the support matrix will flag this. It undermines the professional credibility of the release package even if the technical content is correct.

**No v0.3 identity anchor.** Without a tag or visible version string, a user cannot confirm they are on the intended release state. If the repo HEAD moves between their clone and their test, they have no way to know.

---

## Summary

RTDL v0.3 is **not ready for external release in its current state.**

The underlying workload surface is genuine, the honesty boundaries in the docs are well-handled, and the framing of RTDL as a geometric-query core is consistent throughout the materials. The visual demo layer and its relationship to the stable v0.2.0 surface are clearly explained.

What is blocking release is entirely in the repo presentation layer. The five most urgent fixes, in priority order:

1. **Fix the placeholder path in `release_facing_examples.md`** — change `/path/to/rtdl_python_only` to `rtdl` (or the correct cloned directory name) on every command in that file.
2. **Add a dependency section to the README** — even a minimal one: Python version floor, required `pip install` packages, a pointer to the Makefile for native backend prerequisites.
3. **Explain `PYTHONPATH=src:.` once, clearly** — one sentence in the README or quick tutorial explaining why the prefix is needed and what happens without it.
4. **Remove or clearly segregate internal artifacts** — internal examples (goal-numbered, AI-model-named), internal Makefile targets, and the root-level status files should either be removed from `main` before release or explicitly marked as non-public.
5. **Sanitize the support matrix** — replace `lestat@192.168.1.20` with a generic description (e.g. "Linux development host" or "validated Linux environment").

Secondary but important before release: add a v0.3 tag or version string, add a one-line `README` inside `examples/` pointing to the release-facing files, and add a quick-test invocation for the visual demo.

None of these require changing the RTDL core or workload logic. They are all doc and repo hygiene fixes that should take a day or less to apply cleanly.
