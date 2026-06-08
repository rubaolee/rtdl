# Goal4009 Root Path-Halving Candidate Rejection

Date: 2026-06-08

## Verdict

`reject-as-default`

Goal4007 showed that the accepted grouped-union route performs large root-read
traffic. Goal4009 tested the obvious next idea: add conservative path halving
inside the generic union-find root helper so future root reads walk fewer parent
links.

The candidate is rejected. Raw grouped-union telemetry improved, but app-level
signature and timing evidence failed the promotion gate.

## Candidate Patch Tested

The pod candidate temporarily changed `find_grouped_union_root_readonly` from a
readonly parent walk to a path-halving walk:

```cpp
const int next = parent[root];
const int grand = parent[next];
if (grand != next) {
    atomicMin(parent + root, grand);
}
root = next;
```

This patch was not retained in source. The current committed helper remains
readonly.

## Pod Evidence

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05.

Base code commit: `94bf59a4` plus the temporary uncommitted path-halving
candidate patch described above.

Artifacts:

- Raw telemetry candidate:
  - `docs/reports/goal4009_root_path_halving_candidate_pod/clustered3d_65536.json`
  - `docs/reports/goal4009_root_path_halving_candidate_pod/road3d_65536.json`
  - `docs/reports/goal4009_root_path_halving_candidate_pod/ngsim_dense_65536.json`
- App signature candidate:
  - `docs/reports/goal4009_root_path_halving_app_signature_pod/clustered3d_candidate.json`
  - `docs/reports/goal4009_root_path_halving_app_signature_pod/road3d_candidate.json`
  - `docs/reports/goal4009_root_path_halving_app_signature_pod/ngsim_dense_candidate.json`

## Raw Telemetry Result

Rows compare the accepted Goal4007 default route with the temporary path-halving
candidate, using `same_root_on_direct_off`.

| Profile | Default elapsed sec | Candidate elapsed sec | Candidate / default | Parent-link step ratio |
| --- | ---: | ---: | ---: | ---: |
| `clustered3d` | 0.214375 | 0.184106 | 0.859x | 0.773x |
| `road3d` | 0.066684 | 0.050932 | 0.764x | 0.563x |
| `ngsim_dense` | 0.019155 | 0.016571 | 0.865x | 0.742x |

The raw native signal is real: path halving reduces parent-link steps and speeds
the grouped-union kernel micro-path.

## App-Level Gate

The app-level column-signature probe tells the important story.

| Profile | Signature match vs accepted default | Accepted app elapsed sec | Candidate app elapsed sec | Candidate / accepted |
| --- | --- | ---: | ---: | ---: |
| `clustered3d` | no | 0.120874 | 0.142098 | 1.176x |
| `road3d` | yes | 0.069482 | 0.068086 | 0.980x |
| `ngsim_dense` | yes | 0.045522 | 0.048954 | 1.075x |

The `clustered3d` signature mismatch is enough to reject the candidate:
component-label semantics are part of the contract, and raw telemetry speed is
not a substitute for same-contract app output.
Put plainly: raw telemetry speed is not a substitute for same-contract app
output.

Even ignoring that correctness failure, the app timing is mixed: only `road3d`
gets a small improvement, while `clustered3d` and `ngsim_dense` regress.

## Interpretation

Path halving is not safe as an invisible default in the current concurrent
OptiX any-hit/intersection union path. It mutates parent links during root reads,
which can alter the timing and visibility of component-root convergence enough
to change clustered component signatures.

The lesson is not that root-read traffic is unimportant. Goal4007 remains valid:
root-read traffic is large. The lesson is that the fix must be designed as an
explicit deterministic convergence primitive, not as opportunistic path
compression hidden inside readonly root checks.

## Decision

Do not promote root path halving as the default grouped-union route.

Do not replace `find_grouped_union_root_readonly` with a mutating helper.

The next viable route remains the Goal4005 partition-convergence hybrid, with
an explicit deterministic component-root policy and convergence/staleness
counters.

## Boundary

Goal4009 does not authorize release, public speedup wording, broad RT-core
speedup wording, whole-app acceleration wording, paper-reproduction wording,
true-zero-copy wording, automatic partner/backend selection, or app-specific
native-engine logic.
