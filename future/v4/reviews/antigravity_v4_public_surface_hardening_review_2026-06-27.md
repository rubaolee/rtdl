# Antigravity V4 Public Surface, API, Tutorial, And Packaging Hardening Review

Date: 2026-06-27
Reviewer: Antigravity

This document contains the final external review result for the public surface hardening requested in `future/v4/reviews/call_for_review_v4_public_surface_api_docs_packaging_hardening_2026-06-27.md`.

## 1. Verdict
**Verdict Label:** `block_public_surface_until_fixed`

The current public surface hardening is rejected. The API module design is fundamentally flawed and will result in a terrible user experience in modern IDEs, and the "learning path" code is just a JSON-dumping validation script masquerading as a tutorial.

## 2. Top Critics & Methodological Flaws (P0 / P1)

**[P0] ARCHITECTURAL FLAW: IDE Autocomplete Pollution in `src/rtdsl/v4.py`**
The main AI claims that limiting `__all__` and overriding `__dir__()` successfully hides internal maintainer symbols (the `v4_goal...` garbage) from the user. **This is a rookie Python mistake.**
While `dir()` hides symbols in a basic REPL, **modern IDEs (VSCode/Pylance, PyCharm, Jedi) use static analysis.** They will parse `v4.py`, see the 150+ `from .v4_goalXXXX import YYY` statements at the top of the file, and completely flood the user's autocomplete dropdown with internal release-process symbols.
**A public front-door module must be pristine.** It should *only* import what it intends to expose. You cannot use the main `v4.py` entrypoint as both the public API and the maintainer's internal compatibility garbage dump.

**[P1] METHODOLOGICAL FLAW: `benchmark_app_recipes.py` is NOT a tutorial**
The AI claims that `examples/v4/benchmark_app_recipes.py` is "the clean first code path for learning how all 10 benchmark apps map to V4 operators."
**This is false.** The file is just a script that constructs a hardcoded Python dictionary of operator names and dumps them to `sys.stdout` as a JSON payload (`json.dumps(payload)`).
Users do not learn how to use a Python eDSL by reading a JSON-dumper script. This script looks like it was written solely to pass an automated JSON validation gate, not to teach a human. It fails completely as a pedagogical tool.

## 3. Required Fixes Before Approval

1. **Purge `v4.py` of Internal Imports**: Remove ALL `from .v4_goal...` imports from `src/rtdsl/v4.py`. Move all maintainer-compatibility exports into a separate module (e.g., `src/rtdsl/v4_internal.py` or `v4_maintainer.py`). The `v4.py` file must contain *only* the imports required for the public API.
2. **Rewrite the Recipe Example**: Change `examples/v4/benchmark_app_recipes.py` from a JSON-dumping script into actual commented, idiomatic Python code that demonstrates *how* to invoke these operators in a realistic (even if mocked) sequence. It must look like user code, not a CI test harness.

Do not allow the V4.0 public surface to proceed until the public API module is genuinely clean for static analysis and IDEs.
