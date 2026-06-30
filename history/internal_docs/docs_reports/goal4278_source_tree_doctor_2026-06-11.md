# Goal4278 Source-Tree Doctor

Status: local onboarding hardening for the current v2.10 source-tree surface.

## Purpose

After the v2.10 release-artifact alignment, the next practical blocker for new
users is environment confusion. RTDL is source-tree first, optional native
backends are platform-dependent, and partners such as CuPy and Numba are
optional. The project needed one small command that explains this before users
try benchmark apps.

## Delivered

| File | Action | Reason |
| --- | --- | --- |
| `scripts/rtdl_source_tree_doctor.py` | Added source-tree doctor CLI. | Checks version marker, required tree paths, `rtdsl`, `numpy`, optional CuPy/Numba/imageio modules, optional OptiX/Embree library hints, and optional hello-world smoke. |
| `docs/learn/source_tree_doctor.md` | Added learner-facing setup page. | Gives a clean explanation of `PASS`, `WARN`, optional partners, and optional native libraries. |
| `README.md` | Added doctor command to `Start Fast`. | Puts the sanity check before users attempt examples. |
| `docs/README.md` and `docs/learn/README.md` | Added source-tree doctor links. | Keeps the docs and Learn doors aligned with the onboarding path. |
| `tutorials/current/01_source_tree_first_run.md` | Added doctor as the first runnable check. | Teaches users to validate their environment before backend examples. |
| `tests/goal4278_source_tree_doctor_test.py` | Added focused tests. | Verifies human output, JSON output, smoke command behavior, and public docs links. |

## Boundary

The doctor is not a package installer, performance benchmark, pod validator, or
native build system. Optional warnings do not fail the source-tree check unless
the user passes `--strict`.

## Validation

Focused validation command:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal4278_source_tree_doctor_test \
  tests.goal4277_v2_10_release_artifact_alignment_test \
  tests.goal4271_v2_10_user_doc_cleanup_test \
  tests.goal4274_current_doc_recheck_test \
  tests.goal4276_top_level_tutorial_reorganization_test
```

Focused doctor/doc gate: 19 tests ran, all passed.

Expanded v2.10 release-alignment gate including Goal4267/Goal4270 release
packet tests: 27 tests ran, all passed.
