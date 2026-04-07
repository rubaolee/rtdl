# RTDL v0.2 Support Matrix

Date: 2026-04-07
Status: released as `v0.2.0`

## Reading Guide

Status wording used below:

- `accepted`: part of the released bounded v0.2 claim surface
- `accepted, bounded`: supported under an explicit narrower contract or
  fallback boundary
- `limited local`: usable on this Mac only as a local support path, not as the
  primary release-validation host

## Platform Roles

| Platform | Role | Current status |
| --- | --- | --- |
| Linux (`lestat@192.168.1.20` and clean-clone equivalents) | primary v0.2 validation platform | accepted |
| This Mac | local development/doc/focused-test platform | limited local |

## Backend Roles

| Backend | Role | Current status |
| --- | --- | --- |
| PostGIS | external indexed comparison baseline | accepted |
| Python reference | correctness / trust reference | accepted |
| native CPU / oracle | practical correctness and fallback backend | accepted |
| Embree | primary CPU performance backend on accepted mature surfaces | accepted |
| OptiX | primary NVIDIA backend on accepted mature surfaces | accepted |
| Vulkan | portable correctness-preserving backend | accepted, bounded |

## Accepted v0.2 Workload / Boundary Status

| Workload family | Boundary | Linux | Mac local | Claim status |
| --- | --- | --- | --- | --- |
| `segment_polygon_hitcount` | feature closure + Linux/PostGIS evidence | accepted | accepted, limited local | strongest live v0.2 segment/polygon surface |
| `segment_polygon_anyhit_rows` | feature closure + Linux/PostGIS evidence | accepted | accepted, limited local | strongest live v0.2 segment/polygon surface |
| `polygon_pair_overlap_area_rows` | narrow pathology/unit-cell contract | accepted | accepted, limited local | accepted, bounded |
| `polygon_set_jaccard` | narrow pathology/unit-cell contract | accepted | accepted, limited local | accepted, bounded |

## Jaccard Backend Boundary

| Backend surface | Current status on Jaccard line |
| --- | --- |
| Python reference | accepted |
| native CPU / oracle | accepted |
| PostGIS | accepted as external checker on accepted packages |
| Embree | accepted, bounded through documented native CPU/oracle fallback |
| OptiX | accepted, bounded through documented native CPU/oracle fallback |
| Vulkan | accepted, bounded through documented native CPU/oracle fallback |

## Honest Summary

- the segment/polygon line is the strongest current mature live v0.2 surface
- the Jaccard line is real and accepted, but under a narrower workload and
  backend-maturity boundary
- Linux is the canonical place to validate the released v0.2 package
- this Mac remains a useful local platform, but not the primary final release
  validation host
