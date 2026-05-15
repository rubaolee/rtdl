# RTDL Scripts

This directory contains maintenance tooling. It is not the learner path.

## Use First

| Need | Start here |
| --- | --- |
| Run examples | `../examples/README.md` |
| Learn RTDL | `../docs/learn/README.md` |
| Check docs/examples organization | `python -m unittest tests.goal2101_frontpage_navigation_link_audit_test tests.goal2102_examples_directory_organization_audit_test` |
| Build native backends | `../Makefile` targets such as `build-embree` and `build-optix` |

## What Lives Here

| Group | Meaning |
| --- | --- |
| `goal*.py` / `goal*.sh` | Historical and current goal-specific audit, benchmark, intake, and pod-runner scripts. |
| report generators | Scripts that turn measured artifacts into Markdown/JSON evidence. |
| audit utilities | Scripts that scan docs, source, release claims, or consensus state. |
| `schemas/` | Script-owned schemas, such as the system-audit SQLite schema. |

## Rule

Do not treat every script as a public command. Normal users should start from
the front page, docs, and examples. Reviewers can use this directory when a
report or runbook names an exact script.

