# Goal4150 - Direct-Status Single-Pass Scale Sweep

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4150 extends the Goal4149 single-pass candidate check from the 1M packet to
the earlier RT-DBSCAN route-guidance scales: 65k, 131k, 262k, and 524k points.
All rows use the explicit user-selected partition cell factor `0.25`.

## Artifact

`docs/reports/goal4150_direct_status_single_pass_scale_sweep_factor025_pod.json`

Setup:

- Source commit: `e90081f7`
- Point counts: 65,536 / 131,072 / 262,144 / 524,288
- Repeat: 2
- Warmup: 1
- Factor: `0.25`
- Profiles: `clustered3d`, `road3d`, `ngsim_dense`

## Result Compared With Stable Direct-Status

Ratio below is `until_stable / single_pass_candidate`; values above `1.0x`
mean the single-pass candidate is faster.

| Points | Profile | Same signature | Replay ratio | Total ratio |
| ---: | --- | --- | ---: | ---: |
| 65,536 | clustered3d | yes | 1.945x | 8.851x |
| 65,536 | road3d | yes | 2.017x | 1.654x |
| 65,536 | ngsim_dense | yes | 1.944x | 1.111x |
| 131,072 | clustered3d | yes | 2.121x | 1.308x |
| 131,072 | road3d | yes | 2.069x | 1.255x |
| 131,072 | ngsim_dense | yes | 1.849x | 1.117x |
| 262,144 | clustered3d | yes | 2.046x | 1.506x |
| 262,144 | road3d | yes | 2.102x | 1.502x |
| 262,144 | ngsim_dense | yes | 1.996x | 1.176x |
| 524,288 | clustered3d | yes | 2.076x | 1.659x |
| 524,288 | road3d | yes | 2.086x | 1.681x |
| 524,288 | ngsim_dense | yes | 2.010x | 1.218x |

Minimum replay speedup: `1.849x`.

Minimum prepare-plus-replay total speedup: `1.111x`.

## Interpretation

The single-pass candidate is not a 1M-only artifact. Across 12 additional rows,
it matches the stable-loop component-size signature and roughly halves the replay
work. Total timing remains positive on every row despite prepare-time variation.

The candidate still skips the no-change convergence proof. Every candidate row
records `candidate_final_changed_flag = 1`, so the evidence is empirical
same-signature parity against the stable loop for the measured scale/profile
packet, not a universal theorem.

## Boundary

Goal4150 supports updating internal route guidance to mention
`single_pass_candidate` as an explicit measured option for the tested
component-signature route. It does not make it the default, does not hide the
choice from users, and does not authorize automatic factor or convergence-mode
selection.

This goal does not authorize release, public speedup wording, broad RT-core
wording, whole-app benchmark claims, paper reproduction, hidden dispatch,
automatic partner selection, automatic partition-cell-factor selection,
app-specific engine logic, native ABI additions, AMD claims, or true-zero-copy
claims.
