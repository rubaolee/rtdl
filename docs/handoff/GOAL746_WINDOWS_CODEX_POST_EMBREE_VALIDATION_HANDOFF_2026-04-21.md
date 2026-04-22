# Goal 746: Windows Codex Post-Embree Validation Handoff

Clone `https://github.com/rubaolee/rtdl.git` fresh on Windows, set up Python plus Embree x64 Build Tools, then validate Windows portability for the current post-Embree-closure mainline by running Goal742/743 focused tests, public entry smoke, command truth audit, and one large Goal743 Embree run; write a concise report with exact commit hash, environment, commands, pass/fail results, and any Windows-only setup or runtime issues. Do not redesign Linux/OptiX work, do not commit, and do not push; if you find a blocker, report the proposed fix and wait for explicit approval.

## Context

The Embree phase was closed on `main` by Goal745. Windows Codex is being used as an independent portability validator after the Mac-side Embree work is complete.

Important reports:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal745_embree_phase_closure_and_nvidia_pivot_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal743_lsi_pip_cross_machine_large_perf_report_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal744_engine_optimization_lessons_from_lsi_pip_embree_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal741_embree_all_app_compact_perf_closure_2026-04-21.md`

## Required Windows Setup

Use a fresh checkout, not a dirty existing tree.

```powershell
git clone https://github.com/rubaolee/rtdl.git C:\Users\Lestat\rtdl_post_embree_validation
cd C:\Users\Lestat\rtdl_post_embree_validation
git log -1 --oneline
py -3 --version
py -3 -m pip install -r requirements.txt
```

Embree requirements:

- Visual Studio Build Tools with `vcvars64.bat`
- Embree x64 package
- `RTDL_EMBREE_PREFIX` pointing to the Embree prefix
- `RTDL_VCVARS64` pointing to `vcvars64.bat` when needed

Example:

```powershell
$env:RTDL_EMBREE_PREFIX="C:\Users\Lestat\vendor\embree-4.4.0.x64.windows"
$env:RTDL_VCVARS64="C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
$env:PYTHONPATH="src;."
py -3 -c "import rtdsl as rt; print(rt.embree_version())"
```

## Required Commands

Run focused Goal742/743 checks:

```powershell
$env:PYTHONPATH="src;."
py -3 -m unittest -v tests.goal742_lsi_pip_root_perf_test tests.goal743_lsi_pip_large_cross_machine_perf_test
```

Run public docs/app smoke:

```powershell
$env:PYTHONPATH="src;."
py -3 scripts/goal497_public_entry_smoke_check.py
```

Run command truth audit:

```powershell
$env:PYTHONPATH="src;."
py -3 scripts/goal515_public_command_truth_audit.py
```

Run one large Goal743 Embree benchmark:

```powershell
$env:PYTHONPATH="src;."
py -3 scripts/goal743_lsi_pip_large_cross_machine_perf.py `
  --scale large `
  --repeats 3 `
  --output-json docs/reports/windows_goal746_lsi_pip_large_perf_2026-04-21.json
```

## Report Requirements

Write one report under `docs/reports/` in the Windows checkout.

The report must include:

- exact commit hash;
- Windows version, CPU/thread count, Python version, compiler, Embree prefix;
- exact commands run;
- pass/fail status for each command;
- large Goal743 table with LSI sparse, LSI dense, and PIP positive rows;
- any Windows-only setup or runtime issue;
- explicit statement that Windows Codex did not commit or push changes.

## Boundaries

- Do not redesign Linux/OptiX work.
- Do not modify source code unless explicitly approved.
- Do not commit.
- Do not push.
- If a blocker is found, write the blocker and proposed fix, then wait for approval.
