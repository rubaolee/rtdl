# RTDL v0.4 External UX Review Report

**Review Date**: 2026-04-11  
**Target Check-out**: `/Users/rl2025/worktrees/rtdl_v0_4_release_prep`  
**Reviewer Identity**: External User (macOS/Linux/Windows perspective)

---

## Verdict: **⚠️ PROVISIONAL FAIL**

While the core RTDL engine and the "Start Fast" section of the README are robust, the documentation suite suffers from significant **internal inconsistency** and **broken navigation**. A new user following the tutorial ladder will encounter broken relative links and "Directory not found" errors within the first 15 minutes.

---

## What Worked
- **"Start Fast" Success**: The README and `quick_tutorial.md` correctly prioritize a "First 15 Minutes" experience. Running `examples/rtdl_hello_world.py` worked flawlessly on the first attempt using the provided `PYTHONPATH` logic.
- **Explicit Command Line Syntax**: Providing both `bash` and `cmd.exe` equivalents for the environment variables is excellent and reduces initial frustration for Windows users.
- **Kernel Logic Clarity**: The `hello_world.py` and tutorial code blocks effectively teach the `input -> traverse -> refine -> emit` pattern. The mental model of RTDL as a "query engine" is well-communicated.

---

## Cross-Platform Friction
- **The PYTHONPATH Hurdle**: While documented, the requirement for `PYTHONPATH=src:.` (Unix) or `set PYTHONPATH=src;.` (Windows) remains a friction point. Most modern Python users expect a `pip install -e .` or a self-contained package structure.
- **SDK Manual Setup**: The documentation is honest about needing Embree, OptiX, and Vulkan SDKs, but there is no "Platform Readiness" guidance within the main README to help a user verify their hardware/driver state before they encounter a C++ compilation error.
- **Python Version Ambiguity**: Some docs use `python3`, others use `python`. On Windows, `python3` is rarely the default command name, which may confuse beginners.

---

## Broken Or Misleading Points

### 1. **Fatal Documentation Out-of-Sync**
The user request (and presumably some internal links) refers to:
- `docs/user_guides/tutorials/README.md`
- `docs/user_guides/quick_tutorial.md`

In the actual `v0.4` release-prep repo, these are at:
- `docs/tutorials/README.md`
- `docs/quick_tutorial.md`

Any user following a stale link or searching for "User Guides" in the directory tree will be lost.

### 2. **Broken Relative Links**
In `docs/quick_tutorial.md` (Line 78):
- `[3D Rendering Source](examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)`
This link is **broken**. It is relative to the `docs/` directory, but points to a path as if it were in the root. It should be `../examples/...`.

### 3. **The "cd rtdl" Loop Error**
Almost all example blocks in `docs/release_facing_examples.md` and `docs/v0_4_application_examples.md` start with:
```bash
cd rtdl
```
If a user followed the main README instruction (`git clone ...; cd rtdl`), they are already in the root. Running `cd rtdl` again results in a `bash: cd: rtdl: No such file or directory` error. This makes copy-pasting examples frustrating.

---

## Beginner Programming Experience
- **Graphics Concepts Leak**: The "Hello World" example requires the user to immediately understand that a "Rectangle is two triangles." For a non-graphics user (e.g., a Database Analyst), this is a significant mental leap. RTDL would benefit from a `rt.Rectangles` input role that hides this complexity from the beginner.
- **Naming Confusion**: The package is `rtdsl`, the repo is `rtdl`, and the kernels are decorated with `@rt`. While consistent across the docs, the three-letter shift from `rtdl` to `rtdsl` is a frequent "typo trap" for new programmers.

---

## Release Recommendation

> [!IMPORTANT]
> **DELAY RELEASE** until the following "Final Polish" items are addressed:

1.  **Scrub `cd rtdl`**: Remove redundant directory entry commands from example blocks or standardise them.
2.  **Fix Broken Links**: Audit every relative link in `docs/*.md` to ensure they account for depth (e.g., `../examples/` instead of `examples/`).
3.  **Unified Pathing**: Decide on `docs/tutorials/` vs `docs/user_guides/tutorials/` and ensure all documents reflect the final decision.
4.  **Platform Readiness Tool**: Promote the `check_platform_readiness.py` script mentioned in engineering reports to a visible "First Step" for users attempting to use GPU backends.

---
*Reviewer: External UX Perspective (Simulated)*
