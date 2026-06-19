# RTDL V4.0 M8 External Review Request

Date: 2026-06-19
Status: request for critical external review, not release approval.

Please review the V4.0 M8 packet as aggressively as possible:

`docs/engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md`

Context:

- current user release remains `v3.0.2`;
- V4.0 is an experimental OptiX-backed Python GPU operator track;
- first candidate route is exactly `fixed_radius_count_threshold_2d`;
- source-tree runtime is validated on Linux with CuPy, Numba, PyTorch, and
  OptiX available;
- `v4_release_candidate` exists only as a non-authorizing review gate;
- public true-zero-copy, async, package/PyPI/wheel, stable SDK, public speedup,
  RTX/RT-core speedup, full PyTorch, full Numba, full DLPack, and non-Python
  host claims remain blocked.

Candidate coordinates:

- implementation evidence baseline:
  `bbc43984b74dee7d52c059b295c5eaade0813096`;
- first M8 packet/gate commit:
  `0273d4cba5e38afee099573b0ac47f2f883c1067`;
- external review request commit:
  `eba6f4b6e49152d8da4e545477a1cb125f6bab43`;
- post-review action validation commit:
  `66e6529859a1bac63ce2a72527dc5942e301143d`;
- final release-candidate commit:
  not assigned; release-candidate readiness is still false;
- Linux final smoke on `192.168.1.20` before the package/runtime hygiene
  addendum:
  - `make build-optix`: pass;
  - `scripts/run_test_matrix.py --group v4_release_candidate`: 71 tests, pass;
  - `scripts/v4_0_source_tree_runtime_preflight.py --require-v4-gpu-runtime`:
    pass;
  - `scripts/v4_0_current_front_door_claim_boundary_scan.py`: pass;
  - blocker/preflight JSON parse: pass;
  - `git diff --check`: pass;
  - worktree clean.

Please answer:

1. Is the M8 packet honest enough to be the V4.0 experimental release-candidate
   review baseline?
2. Does any wording overclaim zero-copy, stream ownership, async behavior,
   package/runtime readiness, PyTorch/DLPack breadth, or RT-core performance?
3. Is the first route useful enough as the V4.0 experimental headline, or is it
   still too narrow to be a candidate?
4. Should package/editable install become a hard V4.0 release blocker, or is
   source-tree runtime acceptable for this experimental cut?
5. What exact P0 blockers must close before `release_candidate_ready` can become
   true?

Requested output:

- verdict: accept baseline / accept with blockers / reject;
- P0 blockers with exact file references;
- P1 risks with exact file references;
- P2 polish issues;
- forbidden wording to remove;
- tests or evidence that must be added;
- one explicit recommendation for the next engineering step.
