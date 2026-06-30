# Goal4010 Claude Review: Goal4009 Root Path-Halving Candidate Rejection

Date: 2026-06-08
Reviewer: Claude (external review, read-only)
Scope: `docs/reports/goal4009_root_path_halving_candidate_rejection_2026-06-08.md`,
`tests/goal4009_root_path_halving_candidate_rejection_test.py`,
`src/native/optix/rtdl_optix_core.cpp`,
pod artifacts in `docs/reports/goal4007_grouped_union_root_read_telemetry_pod/`,
`docs/reports/goal4009_root_path_halving_candidate_pod/`,
`docs/reports/goal4002_direct_side_effect_app_probe_pod/`, and
`docs/reports/goal4009_root_path_halving_app_signature_pod/`.

## Verdict

`accept`

## Summary

Goal4009 took the obvious next step after Goal4007's root-read telemetry: it
patched `find_grouped_union_root_readonly` with a conservative path-halving
walk and measured both the raw grouped-union micro-path and the app-level
column-signature/timing gate. The candidate sped up the raw kernel and cut
parent-link steps, but it changed the `clustered3d` app signature
(`core_count: 65536` → `65535`) and produced a mixed/regressed app-timing
picture. The report rejects the candidate as a default, keeps the committed
helper readonly, and closes release/performance wording. I recomputed every
number in both report tables directly from the cited artifacts and they match
to displayed precision; the source diff and claim-boundary checks also hold.

## Findings

### Q1 — Raw telemetry vs. app-level promotion readiness

Correctly distinguished. The report is explicit that "[t]he raw native signal
is real" (raw kernel sped up, parent-link steps fell) but that "raw telemetry
speed is not a substitute for same-contract app output," and frames the
app-level signature probe as "the important story." This is the right
ordering of evidence: a micro-path speedup is necessary but not sufficient for
promotion, and the report does not let the former substitute for the latter.

### Q2 — Do the artifacts support "reduced parent-link steps, failed/regressed app evidence"?

Confirmed by direct recomputation from `last_telemetry[9]`
(`root_find_parent_link_steps`) and `median_native_elapsed_sec` /
`median_elapsed_sec` in the `same_root_on_direct_off` variant of each pair of
pod files:

| Profile | Baseline steps (Goal4007) | Candidate steps (Goal4009) | Step ratio | Baseline elapsed | Candidate elapsed | Elapsed ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 708,889,367 | 547,824,139 | 0.773x | 0.214375 | 0.184106 | 0.859x |
| `road3d` | 304,914,824 | 171,683,904 | 0.563x | 0.066684 | 0.050932 | 0.764x |
| `ngsim_dense` | 33,227,681 | 24,647,991 | 0.742x | 0.019155 | 0.016571 | 0.865x |

All six ratios match the report's "Raw Telemetry Result" table exactly. The
app-level table is equally well supported — I compared
`docs/reports/goal4002_direct_side_effect_app_probe_pod/*_default.json` against
`docs/reports/goal4009_root_path_halving_app_signature_pod/*_candidate.json`:

| Profile | `signature` equal? | Default `elapsed_sec` | Candidate `elapsed_sec` | Ratio |
| --- | --- | ---: | ---: | ---: |
| `clustered3d` | no (`core_count` 65536 vs 65535; `cluster_sizes` and `noise_count` identical) | 0.120874 | 0.142098 | 1.176x |
| `road3d` | yes (`cluster_sizes`, `core_count`, `noise_count` byte-identical) | 0.069482 | 0.068086 | 0.980x |
| `ngsim_dense` | yes (byte-identical) | 0.045522 | 0.048954 | 1.075x |

This matches the "App-Level Gate" table to displayed precision and supports
the report's framing: raw telemetry improved across the board (0.563x–0.773x
step ratio, 0.764x–0.865x elapsed ratio), while app-level evidence is mixed at
best (`road3d` ~flat, `clustered3d`/`ngsim_dense` regress) and broken for
`clustered3d` (signature mismatch).

### Q3 — Is the `clustered3d` signature mismatch sufficient to reject?

Yes. I read both `clustered3d` signature blocks directly:
default = `{"cluster_sizes": {"1": 16384, "2": 16384, "3": 16384, "4": 16384},
"core_count": 65536, "noise_count": 0}` with `all_core_flags_true: true`;
candidate = the same `cluster_sizes`/`noise_count` but `"core_count": 65535`
and `all_core_flags_true: false`. The cluster partition itself is unchanged,
but one point's `is_core` flag flipped — and `is_core` is one of the four
typed result-stream columns the front door promises
(`result_columns: ["point_ids", "component_labels", "is_core",
"neighbor_counts"]`). A patch that changes any committed output column for
identical input, seed, and radius is a correctness regression regardless of
how small the delta looks, and the report's framing ("component-label
semantics are part of the contract... raw telemetry speed is not a substitute
for same-contract app output") correctly treats this as disqualifying on its
own — independent of the separate timing-regression argument it also makes.
The interpretation section's explanation (path halving mutates parent links
during reads, which can shift the timing/visibility of convergence enough to
change a borderline point's neighbor count across the `min_neighbors`
threshold) is a plausible, mechanistically grounded account of how a
"conservative" read-time optimization produced an observable correctness
difference in a concurrent any-hit/intersection context.

### Q4 — Does committed source keep the helper readonly with no mutating remnant?

Confirmed. `find_grouped_union_root_readonly`
(`src/native/optix/rtdl_optix_core.cpp:4838-4849`) is:

```cpp
extern "C" __device__
int find_grouped_union_root_readonly(int* parent, int item) {
    grouped_union_telemetry_add(8u, 1ull);
    int root = item;
    int guard = 0;
    while (parent[root] != root && guard < 4096) {
        grouped_union_telemetry_add(9u, 1ull);
        root = parent[root];
        ++guard;
    }
    return root;
}
```

This contains `root = parent[root];` and nothing resembling the candidate's
`grand`/`atomicMin` lines — matching the test's positive/negative string
assertions (`test_committed_source_keeps_root_find_readonly`). No new
`__global__` entry point or mutating helper was introduced or retained
anywhere between this function and `union_grouped_min_root`. The
`union_grouped_min_root` / `union_grouped_min_root_with_telemetry` callers
(lines 4852-4906) still call only the readonly helper.

### Q5 — Overclaim / wording-boundary check

Clean. The report uses `reject-as-default` as its verdict, repeats "raw
telemetry speed is not a substitute for [same-contract app output]" verbatim
(satisfying the test's overclaim guard), and its "Boundary" section disclaims
release, public/broad-RT-core/whole-app speedup, paper-reproduction,
true-zero-copy, automatic partner/backend selection, and app-specific
native-engine wording — consistent with `claim_boundary` flags I spot-checked
in the artifacts (`performance_claim_authorized: false`,
`release_authorized: false`, `telemetry_is_diagnostic: true` in the raw
telemetry pods; `public_speedup_claim_authorized: false`,
`release_authorized: false` in the app-signature pods). The hardware/commit
provenance line ("NVIDIA RTX 4000 Ada Generation, driver 550.127.05... Base
code commit `94bf59a4`") matches `gpu` and `source_commit` fields recorded in
`docs/reports/goal4009_root_path_halving_candidate_pod/clustered3d_65536.json`.

## Test Coverage

`tests/goal4009_root_path_halving_candidate_rejection_test.py` checks: (1) the
raw candidate reduces `root_find_parent_link_steps` and
`median_native_elapsed_sec` relative to the Goal4007 baseline for all three
profiles; (2) the `clustered3d` app signature differs and its elapsed ratio
exceeds 1.1x, while `road3d`/`ngsim_dense` signatures match exactly; (3) the
committed helper body retains the readonly walk and excludes the
`grand`/`atomicMin` path-halving lines; (4) the report contains the rejection
verdict, the no-substitute framing, the "do not promote" decision, the
partition-convergence-hybrid forward pointer, and the closed-boundary phrase.
Every assertion in the test matches what I independently verified against the
source and the cited artifacts; I did not re-execute the suite (would require
pod/GPU access and out-of-scope command approval for this read-only review),
but all string, numeric-comparison, and structural assertions hold against the
current tree.
