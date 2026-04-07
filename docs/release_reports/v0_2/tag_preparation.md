# RTDL v0.2 Tag Preparation

Date: 2026-04-07
Status: ready for preparation

## Purpose

This note records the final bounded interpretation of what should happen before
an actual v0.2 tag is created.

## Ready Now

- frozen v0.2 scope is explicitly documented
- release-facing examples are aligned with the frozen scope
- front-door docs are aligned
- release statement and support matrix exist
- final audit report exists
- backend loader robustness was improved after a real external report
- Linux OptiX SDK-path robustness was improved so `make build-optix` discovers
  the accepted host SDK path automatically

## Tag Preparation Checklist

- confirm the desired tag name and release branch policy
- confirm no new feature work is entering before the tag
- optionally rerun the frozen Linux validation package on the final tag commit
- keep the release notes bounded to the frozen four-workload v0.2 surface
- preserve the Linux-primary / Mac-limited wording
- preserve the Jaccard fallback-vs-native wording

## Not Required For Tag Preparation

- no new workload families
- no new PostGIS benchmarks beyond the accepted package
- no native Jaccard Embree/OptiX/Vulkan kernels
- no claim that all historical repo content has equal process strength

## Honest Interpretation

Tag preparation is acceptable now because the release-shaping package is
coherent and audited.

The actual tag action should still be treated as a separate explicit release
step, not implied by this note alone.
