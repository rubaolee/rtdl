# Goal4149 - Direct-Status Single-Pass Candidate Pod Result

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4149 measures the Goal4148 `single_pass_candidate` mode for the RT-DBSCAN
prepared direct-status component-signature path. The test compares the candidate
against the default `until_stable` convergence loop at 1,048,576 points and
partition cell factor `0.25`.

## Artifact

`docs/reports/goal4149_direct_status_single_pass_1m_factor025_pod.json`

Setup:

- Source commit: `771704fa`
- Point count: 1,048,576
- Repeat: 2
- Warmup: 1
- Factor: `0.25`
- Profiles: `clustered3d`, `road3d`, `ngsim_dense`

## Result Compared With Stable Direct-Status

Ratio below is `until_stable / single_pass_candidate`; values above `1.0x`
mean the single-pass candidate is faster.

| Profile | Same signature | Stable replay (s) | Single-pass replay (s) | Replay ratio | Stable total (s) | Single-pass total (s) | Total ratio |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d | yes | 5.674403 | 2.855665 | 1.987x | 7.185739 | 3.868795 | 1.857x |
| road3d | yes | 5.139699 | 2.471521 | 2.080x | 5.962705 | 3.281554 | 1.817x |
| ngsim_dense | yes | 1.245002 | 0.619553 | 2.010x | 2.272641 | 1.645867 | 1.381x |

All three rows matched the stable-loop component-size signature.

## Interpretation

This is the first large Goal414x direct-status change that materially improves
the hot replay path. The stable route used two union iterations; the candidate
uses one. That nearly halves the component-signature replay time on all three
1M profiles.

The candidate is still bounded because `direct_status_final_changed_flag` is
`1` after the single pass. In other words, the candidate does not prove general
convergence by running the second no-change scan. The evidence is same-signature
parity against the stable loop on the measured profiles.

## Boundary

This result supports a follow-up route-guidance experiment across the existing
65k/131k/262k/524k/1M packets. It does not yet promote `single_pass_candidate`
as a universal default and does not authorize hidden dispatch or automatic
partition-cell-factor selection.

This goal does not authorize release, public speedup wording, broad RT-core
wording, whole-app benchmark claims, paper reproduction, hidden dispatch,
automatic partner selection, automatic partition-cell-factor selection,
app-specific engine logic, native ABI additions, AMD claims, or true-zero-copy
claims.
