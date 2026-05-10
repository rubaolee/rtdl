# Goal1659 v1.6.11 Performance Matrix 3-AI Consensus

## Verdict

`ACCEPT_AS_PRE_POD_RELEASE_CANDIDATE_MATRIX`

Codex, Claude, and Gemini agree that the `v1.6.11` performance matrix is an
acceptable preparation artifact for the final Python+RTDL-only release
candidate before Python+partner+RTDL.

This consensus does not publish `v1.6.11`, authorize a release tag, authorize
public speedup wording, promote `COLLECT_K_BOUNDED`, or claim whole-app
performance.

## Codex Verdict

Accept as a pre-pod performance matrix. The matrix covers every public app,
marks frozen/demo surfaces explicitly, records the active pod command batch,
keeps release/tag flags false, and requires real NVIDIA OptiX pod evidence
before final release consideration.

## Claude Verdict

Claude passed the matrix as a preparation artifact and explicitly did not clear
tag or release. Claude required four hardening changes:

- add `true_zero_copy` to the validator-level blocked-claim check;
- document that `outlier_detection` and `dbscan_clustering` share the Goal757
  fixed-radius prepared fixture;
- explain `--skip-validation` for `facility_knn_assignment` and
  `robot_collision_screening`;
- define binary pod pass criteria before the pod run.

All four required changes were applied.

## Gemini Verdict

Gemini approved the matrix as well-prepared, fail-closed, and honest. Gemini
agreed that it covers all 18 public apps, separates frozen/proof surfaces,
keeps release and tag authorization false, and correctly requires pod execution
before final performance evidence exists.

## Consensus Boundary

`v1.6.11` is accepted only as a release-candidate performance-test plan at this
stage. The next step is a pod run only after the user provides a pod window.
The pod pass rule is strict: all 16 active pod rows must produce accepted
artifacts, the robot positive-control row must complete, and every completed
artifact must include parity/strict status, phase timing, baseline contract,
and claim boundary.

Positive public speedup wording remains blocked until same-contract evidence
and separate 3-AI review accept each row.
