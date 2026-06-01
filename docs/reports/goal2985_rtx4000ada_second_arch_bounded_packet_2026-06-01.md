# Goal2985 RTX 4000 Ada Second-Architecture Bounded Packet

Date: 2026-06-01

Status: second-architecture bounded packet passed; no release authorization

## Purpose

Goal2985 runs the Goal2855 seven-app packet on the RTX 4000 Ada pod after
Goal2984 made the Barnes-Hut second-architecture profile explicit.

This closes the operational part of the Goal2977 gap: the second architecture
now has a clean 7/7 packet artifact at current main, while preserving the
truth that the Barnes-Hut row used the bounded second-architecture profile
rather than the full 8192-body Embree CPU baseline profile.

## Pod Packet

Artifact directory:

`docs/reports/goal2985_second_arch_bounded_packet_pod/`

Command shape:

```text
python3 scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py \
  --output-dir /tmp/goal2984_second_arch_bounded_packet \
  --summary-name goal2855_summary.json \
  --timeout-seconds 2400 \
  --compact-child-output \
  --barnes-hut-case-profile second_arch_bounded
```

## Summary

| Field | Value |
| --- | --- |
| GPU | NVIDIA RTX 4000 Ada Generation, driver `565.57.01` |
| Source commit | `20b62a3eb21607a4e313b58fd8804de91e681f4e` |
| Packet status | `pass` |
| `all_pass` | `true` |
| Artifact count | `7 / 7` |
| Barnes-Hut profile | `second_arch_bounded` |
| Dirty artifacts | `{}` |
| Claim-boundary violations | `{}` |
| Packet elapsed sec | `242.754` |

## Barnes-Hut Row

| Bodies | Embree total median sec | OptiX total median sec | OptiX total speedup | OptiX membership speedup | Rows match |
| ---: | ---: | ---: | ---: | ---: | --- |
| 512 | `2.994` | `0.503` | `5.955x` | `177.221x` | true |
| 2048 | `59.169` | `3.773` | `15.681x` | `696.740x` | true |

The Goal2803 command in the packet summary records only:

```text
--case 512:16 --case 2048:32
```

It does not record or imply that `8192:32` was run on this second-architecture
packet.

## Partner Selection

Barnes-Hut vector-sum continuation selected CuPy by same-contract timing:

| Partner fact | Value |
| --- | --- |
| Selected partner | `cupy` |
| Selected partner median sec | `0.000418` |
| Triton preview promoted | `false` |

This keeps the v2.5 primitive-first and partner-by-measurement doctrine intact.

## Interpretation

Goal2985 improves the release position:

- the RTX 4000 Ada second-architecture packet now has 7/7 artifacts at current
  main;
- the Barnes-Hut second-architecture evidence is clean, bounded, and explicit;
- no public speedup, broad RT-core speedup, whole-app speedup, true zero-copy,
  paper-reproduction, package-install, or release claim is authorized;
- the full 8192-body Barnes-Hut Embree CPU baseline remains unmeasured on this
  second architecture.

The remaining release question is now policy and review, not missing execution:
can a future v2.5 release packet state that second-architecture Barnes-Hut
evidence uses the bounded profile while the full Barnes-Hut profile remains
available from prior/current packets on the primary architecture?

## Boundary

Goal2985 does not authorize:

- v2.5 release or release tag action;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- package-install wording;
- Triton preview auto-selection;
- paper reproduction claims;
- app-specific native engine customization.

External review should verify that the profile boundary is clear enough before
any release packet uses this second-architecture evidence.
