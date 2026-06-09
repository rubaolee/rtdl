# Goal4165: Mixed-Predicate Policy Variant Probe

Status: accepted diagnostic probe; no route promotion.

## Purpose

Goal4159 treated the `road_sparse_many_noise` mixed-predicate row as a promotion
blocker because the predicate direct-status candidate did not always match the
current grouped-stream component-size signature. Goal4165 tests whether that gap
is explained by a simple grouped-stream configuration switch.

The tested variants were:

- grouped-stream Numba with same-root culling enabled
- grouped-stream Numba with same-root culling disabled
- grouped-stream Numba with direct side effects enabled
- predicate direct-status until-stable candidate

Each variant was run on four mixed-predicate shapes and three seeds:

- `17`
- `123`
- `20260519`

## Artifact

`docs/reports/goal4165_mixed_policy_variant_probe_pod.json`

Environment:

- Commit: `d25eff118d8590068c5aa0ead9c557240ae3a06c`
- GPU: `NVIDIA RTX 4000 Ada Generation, 550.127.05`

## Results

| Reference variant | Exact matches | Canonical component-size matches |
| --- | ---: | ---: |
| grouped stream, same-root culling enabled | 7 / 12 | 11 / 12 |
| grouped stream, same-root culling disabled | 7 / 12 | 11 / 12 |
| grouped stream, direct side effects | 7 / 12 | 11 / 12 |

No grouped-stream variant explains every predicate direct-status result.

The only canonical mismatches are both `road_sparse_many_noise`:

| Seed | Variant that mismatches predicate direct-status canonically |
| ---: | --- |
| 17 | grouped stream with direct side effects |
| 123 | grouped stream with same-root culling enabled or disabled |

## Interpretation

The gap is not simply a same-root-culling switch or a direct-side-effect switch.
The mixed-predicate case exposes a real policy issue: predicate-false items that
touch more than one predicate-true component need an explicit border assignment
policy. Different legal policies can keep the same core/noise counts while
producing different component-size distributions.

Predicate-false items that touch more than one predicate-true component need an explicit border assignment policy.

That means a raw component-size signature is too strict as the only correctness
gate for mixed predicate rows. The runtime should report and test the chosen
policy explicitly.

## Boundary

This diagnostic does not promote predicate direct-status for mixed predicate
rows. It does not authorize release, public speedup wording, whole-app claims, or
route-promotion wording.

This diagnostic does not promote predicate direct-status for mixed predicate rows.

## Next Step

Add a policy-aware RT-DBSCAN semantic signature that separates:

- core count
- noise count
- number of non-noise assigned items
- border assignment policy
- component-size distribution when the policy is part of the contract

Then re-evaluate predicate direct-status as an explicit policy route rather than
forcing it to mimic whichever grouped-stream policy happened to be used as the
previous benchmark reference.
