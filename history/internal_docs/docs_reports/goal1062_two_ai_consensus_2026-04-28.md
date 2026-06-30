# Goal1062 Two-AI Consensus: Blocked RTX Wording Rerun Manifest

Date: 2026-04-28

## Verdict

ACCEPT.

Goal1062 is a valid local-only preparation step for the next RTX pod session.
It targets only the two remaining `public_wording_blocked` NVIDIA RTX rows:

- `facility_knn_assignment / coverage_threshold_prepared`
- `robot_collision_screening / prepared_pose_flags`

## Consensus Inputs

- `scripts/goal1062_blocked_rtx_wording_rerun_manifest.py`
- `tests/goal1062_blocked_rtx_wording_rerun_manifest_test.py`
- `scripts/goal1062_blocked_rtx_wording_rerun_runner.sh`
- `docs/reports/goal1062_blocked_rtx_wording_rerun_manifest_2026-04-28.json`
- `docs/reports/goal1062_blocked_rtx_wording_rerun_manifest_2026-04-28.md`
- `docs/reports/goal1062_claude_review_2026-04-28.md`

## Agreement

Claude accepted the manifest. Codex accepts the same result after running the
local tests and checking the generated manifest.

The manifest has the required split:

- Two correctness-validation rows, both without `--skip-validation`.
- Two large timing-repeat rows, both with an explicit `0.100` second timing
  floor and with `--skip-validation` limited to timing-only collection.

The robot validation row deliberately uses `python_objects` plus `pose_flags`
because the packed `pose_count` mode rejects oracle validation. The robot large
timing row uses `packed_arrays` plus `pose_count` to avoid Python flag/row
materialization during the timing-floor repeat.

## Non-Authorization

This goal does not run a pod, create cloud resources, authorize release, or
authorize public RTX speedup wording. Future promotion still requires:

- pod artifacts copied back from `docs/reports/goal1062_blocked_rtx_wording_rerun/`;
- artifact-intake checks;
- same-semantics baseline review;
- another 2+ AI consensus before any public wording status changes.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1062_blocked_rtx_wording_rerun_manifest_test
```

Result: `3 tests OK`.

## Boundary

Vulkan/HIPRT/Apple RT parity work is intentionally outside Goal1062. This goal
only prepares the remaining blocked NVIDIA RTX wording rerun commands so a
future paid pod can run both apps in one session.
