# Goal 515: Public Docs Command Truth Closure

Date: 2026-04-17

Status: accepted with 3-AI consensus

## Scope

Goal515 audits the public commands that real users see in:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/*.md`

The goal is to ensure every public runnable command is either mechanically
covered by a command gate or explicitly classified as a gated platform/backend
validation command.

## Changes Made

- Added `/Users/rl2025/rtdl_python_only/scripts/goal515_public_command_truth_audit.py`.
- Added `/Users/rl2025/rtdl_python_only/tests/goal515_public_command_truth_audit_test.py`.
- Updated `/Users/rl2025/rtdl_python_only/scripts/goal410_tutorial_example_check.py` to cover DB commands that public docs already advertised:
  - `rtdl_db_conjunctive_scan.py` on `cpu_python_reference`, `cpu`, `embree`, `optix`, and `vulkan`
  - `rtdl_db_grouped_count.py` on `cpu_python_reference`, `cpu`, `embree`, `optix`, and `vulkan`
  - `rtdl_db_grouped_sum.py` on `cpu_python_reference`, `cpu`, `embree`, `optix`, and `vulkan`
  - `rtdl_sales_risk_screening.py` on `cpu_python_reference`, `cpu`, `embree`, `optix`, and `vulkan`
  - `rtdl_v0_7_db_app_demo.py --backend auto`
  - `rtdl_v0_7_db_kernel_app_demo.py --backend auto`
  - `scripts/rtdl_generate_only.py` for the release-facing generated-bundle command
- Added `rtdl_feature_quickstart_cookbook.py` to the broad harness after
  external review noted that it was only covered by the narrower Goal513 smoke
  gate.
- Tightened the audit to distinguish exact command coverage from command-family
  coverage, so intentional size/output-path substitutions are visible.

## Audit Result

Generated inventory:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal515_public_command_truth_audit_2026-04-17.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal515_public_command_truth_audit_2026-04-17.md`

Summary:

- Public docs scanned: `14`
- Runnable public commands found: `216`
- Uncovered commands: `0`
- Coverage counts:
  - `goal410_harness_exact`: `199`
  - `goal410_harness_family`: `11`
  - `goal513_front_page_smoke_exact`: `5`
  - `postgresql_validation_command`: `1`
- Classification counts:
  - `portable_python_cpu`: `131`
  - `optional_native_backend_gated`: `44`
  - `linux_gpu_backend_gated`: `33`
  - `visual_demo_or_optional_artifact`: `7`
  - `linux_postgresql_gated`: `1`

## Validation

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result: `valid: true`.

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal515_public_command_truth_audit_test tests.goal514_tutorial_example_harness_refresh_test -v
```

Result: `Ran 3 tests`, `OK`.

Command:

```bash
python3 scripts/goal410_tutorial_example_check.py --machine local-goal515 --output build/goal515_tutorial_example_check.json
```

Result: `53 passed`, `0 failed`, `20 skipped`, `73 total`.

Command:

```bash
PYTHONPATH=src:. python3 -m py_compile scripts/goal515_public_command_truth_audit.py scripts/goal410_tutorial_example_check.py tests/goal515_public_command_truth_audit_test.py && git diff --check
```

Result: passed.

## Current Verdict

Goal515 is accepted. Public documentation commands are now covered by a
machine-readable inventory that fails if any runnable public command is not
mechanically covered or explicitly gated.

## AI Review Consensus

- Claude review: `PASS`; Claude accepted the audit mechanism and identified
  three non-blocking precision notes. The two actionable notes were addressed:
  the feature cookbook was promoted into the broad harness, and the audit now
  distinguishes exact command coverage from family coverage.
- Gemini Flash review: `ACCEPT`; Gemini accepted the final exact/family
  coverage split and zero-uncovered-command result.
- Codex conclusion: `ACCEPT`; Goal515 gives the public docs a repeatable
  command-truth audit instead of relying on manual spot checks.
