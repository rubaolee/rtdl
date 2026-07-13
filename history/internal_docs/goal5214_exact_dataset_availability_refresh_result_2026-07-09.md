# Goal5214 Exact Dataset Availability Refresh Result

Date: 2026-07-09

## Verdict

```text
completed_exact_dataset_availability_refresh__level_c_still_blocked
```

## Purpose

After the Goal5213 midterm packet, the next real full-reproduction question is
not another route micro-optimization. It is:

```text
Do we now have the exact X-HD paper input files, hashes, or deterministic
author conversion provenance required for Level-C exact paper reproduction?
```

This goal refreshes that answer against the current POD and the author
paper-branch log index.

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5214_exact_dataset_availability_refresh_2026-07-09.json
```

## POD Probe

POD:

```text
host = 213.173.108.24
port = 13502
container = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
```

Checked paths:

| path | status |
|---|---|
| `/local` | missing |
| `/local/storage` | missing |
| `/local/storage/shared` | missing |
| `/local/storage/shared/HDDatasets` | missing |
| `/root/rtdl_goal5093/Paper-reproduction-apps/x-hd-paper/data` | exists |
| `/root/rtdl_goal5093/Paper-reproduction-apps/x-hd-paper/results` | exists |

Conclusion:

```text
The current POD does not contain the author paper input data root.
```

## Author Paper-Branch Log Index

Source artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
```

The log index contains:

```text
run_all_record_count = 4535
categories:
  BraTS2020_ValidationData = 2500
  ModelNet40 = 2000
  graphics = 20
  geo = 15
input_root_counts:
  /local/storage/shared = 9070 file references
```

Examples:

| category | sample pair | author path root | input availability |
|---|---|---|---|
| graphics | `dragon.ply` -> `asian_dragon.ply` | `/local/storage/shared/HDDatasets/graphics/...` | log path known, input file not available |
| geo | `USADetailedWaterBodies.wkt` -> `USACensusBlockGroupBoundaries.wkt` | `/local/storage/shared/HDDatasets/geo/...` | log path known, input file not available |
| ModelNet40 | `airplane_0036.off` -> `airplane_0515.off` | `/local/storage/shared/HDDatasets/ModelNet40/...` | log path known, input file not available |
| BraTS | `BraTS20_Validation_001_flair.nii` -> `BraTS20_Validation_033_flair.nii` | `/local/storage/shared/HDDatasets/BraTS2020_ValidationData/...` | log path known, input file not available |

The logs are useful: they identify paper-branch workload paths, dimensions,
point counts, bounding boxes, and author HDResult values. They are not enough
for Level-C exact paper dataset reproduction because the files themselves are
not present and no file hashes / byte-identical converted point sets are
available.

## Exact Dataset Rule

Level-C exact paper dataset reproduction still requires one of:

```text
author-provided input files
retained hashes for converted point sets
byte-identical converted point sets
documented author script that deterministically regenerates the same point
sets from pinned public source files
```

Not sufficient:

```text
paper dataset name
author log path
point count
bounding box
Gini/statistics
same public source family
```

## Conclusion

Current status:

```text
exact paper input files available in current POD = false
paper log paths known = true
paper log paths resolvable in current POD = false
Level-C exact paper dataset reproduction supported = false
current best supported level = Level B same-source representative reproduction
```

This refresh confirms the earlier Goal5131 conclusion under the current POD.
The project should not claim exact paper reproduction or full X-HD reproduction
from the current evidence.

## Next Recommendation

Proceed in this order:

1. Send Goals5211-5214 and the midterm packet for strict review.
2. Consolidate the Level-B representative packet if review approves.
3. Continue exact-input acquisition only if a credible source can provide:

```text
files
hashes
or deterministic conversion provenance
```

Do not spend the next goal on route micro-tuning unless the review rejects the
current Level-B route.

## Claim Boundary

Allowed:

```text
The author paper-branch logs identify exact path names and workload metadata,
but the current POD does not contain the corresponding input files. Level-C
exact paper reproduction remains blocked; Level-B representative reproduction
is the strongest currently supported claim.
```

Not authorized:

```text
full X-HD paper reproduction
exact paper dataset reproduction
author-vs-RTDL performance ratio
author parity
treating same-source public Stanford data as exact paper input
```
