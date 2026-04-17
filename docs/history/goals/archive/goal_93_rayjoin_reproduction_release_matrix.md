# Goal 93: RayJoin Reproduction Release Matrix

## Objective

Produce the final v0.1 release-facing RayJoin-style experiment matrix.

This goal is not about proving a new backend capability. It is about closing
the reproduction story into one release-ready package that states:

- what RTDL reproduced
- what timing boundaries were used
- which dataset families were accepted
- which dataset families were skipped or unavailable
- what claims are safe for v0.1

## Scope

Include only stable, reviewable, already accepted workload families and
boundaries.

Primary focus:

- `county_zipcode`
- `blockgroup_waterbodies`
- bounded `LKAU ⊲⊳ PKAU`
- bounded `overlay-seed analogue`

Compared systems where applicable:

- PostGIS
- RTDL + OptiX
- RTDL + Embree
- RTDL + Vulkan
- trusted oracle envelopes where they are part of the accepted package

## Required outputs

- one consolidated reproduction matrix report
- one machine-readable summary artifact
- one explicit skipped/unavailable surface list
- one short release-facing claim summary

## Constraints

- do not silently mix timing boundaries
- do not silently omit unavailable families
- do not broaden beyond accepted evidence
- keep “paper-identical reproduction” and “bounded accepted reproduction” clearly
  separated

## Acceptance

Goal 93 is done when:

- the v0.1 reproduction story can be read from one package
- included and skipped surfaces are explicit
- the claims are consistent with published goal artifacts
- the package has 2+ AI review before publish
