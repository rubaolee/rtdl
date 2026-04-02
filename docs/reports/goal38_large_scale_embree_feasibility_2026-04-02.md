# Goal 38 Large-Scale Embree Feasibility

Date: 2026-04-02

## Goal

Determine how far `192.168.1.20` can sustain a serious larger-scale exact-source `County ⊲⊳ Zipcode` workload on the current RTDL Embree backend, using an Embree-only measurement path and treating the first failed step as the host boundary.

## Host

- label: `192.168.1.20`
- OS: Ubuntu 24.04.4 LTS
- CPU class: Intel `i7-7700HQ`
- memory: about `15 GiB`

This is a real Linux Embree workstation for RTDL testing, but not a paper-scale server. The purpose of this goal was to find the current practical boundary, not to overclaim nationwide readiness.

## Workload

Family:

- `County ⊲⊳ Zipcode`

Queries:

- `lsi`: which county boundary segments intersect which zipcode boundary segments
- `pip`: which zipcode probe points fall inside which county polygons

Large-scale rule for this goal:

- the main path is `Embree-only`
- the Python simulator is excluded from the primary large-scale timing path
- the results here are feasibility and scaling measurements, not oracle-parity timings

## Frozen Ladder

The ladder was defined by cumulative state groups:

1. `top1_tx`
2. `top2_tx_ca`
3. `top4_tx_ca_ny_pa`
4. `top8_tx_ca_ny_pa_il_oh_mo_ia`
5. `nationwide`

The active harness checkpoints after each completed point so accepted progress is not lost if the host stops during a later point.

## Accepted Checkpoint Boundary

Accepted completed checkpoint for Goal 38:

- `top4_tx_ca_ny_pa`

Interpretation:

- the Linux host completed `top1`, `top2`, and `top4`
- the run did not complete `top8`
- therefore `top4` is the largest completed large-scale checkpoint from this round

This is the correct honest closure for the evidence collected in this round. It should be read as feasibility-through-`top4`, not as a proof that `top4` is the absolute maximum possible point on this host.

## Measured Results

| Label | States | County Features | Zipcode Features | County Chains | Zipcode Chains | County Segments | Zipcode Segments | `lsi` Embree (s) | `pip` Embree (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `top1_tx` | `TX` | 254 | 1841 | 807 | 3932 | 865140 | 2998646 | 29.988665 | 31.672195 |
| `top2_tx_ca` | `TX,CA` | 312 | 3619 | 993 | 5996 | 1260009 | 6167617 | 49.821633 | 69.104872 |
| `top4_tx_ca_ny_pa` | `TX,CA,NY,PA` | 441 | 7035 | 1612 | 10144 | 1705027 | 9982960 | 80.711857 | 159.431551 |

## Scaling Notes

Observed behavior through the accepted boundary:

- `lsi` remained under about `81s` at `top4`
- `pip` reached about `159s` at `top4`
- conversion stayed manageable through `top4`
- the host still handled nearly `10.0M` zipcode segments at the accepted point

This means the host is already beyond:

- small regional slices
- single-state stress tests
- two-state exact-source ladders

and can sustain a genuinely larger multi-state Embree workload.

## First Unclosed Step

The first unclosed step in the frozen ladder is:

- `top8_tx_ca_ny_pa_il_oh_mo_ia`

What happened:

- `top8` staging directories existed from the run
- the process did not checkpoint a completed `top8` point
- no completed `nationwide` point exists

So the current evidence supports this conclusion:

- `top8` is the first unclosed larger-scale step on `192.168.1.20`
- this round does not justify a nationwide execution claim

## What Goal 38 Proves

Goal 38 proves that:

- RTDL on Embree can now sustain a serious larger exact-source `County ⊲⊳ Zipcode` package on the Linux host
- the host is capable of clearing a meaningful multi-state point, not just tiny regional slices
- `top4` is a valid accepted completed large-scale Embree checkpoint for this machine

## What Goal 38 Does Not Prove

Goal 38 does not prove:

- a completed `top8` run
- a completed nationwide run
- full RayJoin paper-scale reproduction on this Linux host

Those remain future work.

## Next Step

The next correct step after Goal 38 is not another blind nationwide attempt.

It should be one of:

1. accept feasibility-through-`top4` and consolidate it into the final Embree-only reproduction matrix
2. if a broader attempt is still required, treat `top8` as a separate engineering goal with explicit memory/runtime mitigation

## Artifact Sources

This report is based on:

- the live remote checkpoint summary copied from `192.168.1.20`
- [goal_38_large_scale_embree_feasibility.md](/Users/rl2025/rtdl_python_only/docs/goal_38_large_scale_embree_feasibility.md)
- [goal38_linux_county_zipcode_feasibility.py](/Users/rl2025/rtdl_python_only/scripts/goal38_linux_county_zipcode_feasibility.py)
- [goal38_feasibility_test.py](/Users/rl2025/rtdl_python_only/tests/goal38_feasibility_test.py)
