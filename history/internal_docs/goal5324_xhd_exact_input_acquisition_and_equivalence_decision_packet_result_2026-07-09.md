# Goal5324 - X-HD Exact Input Acquisition And Equivalence Decision Packet

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5324 converts the exact-input blocker established by Goals5318-5323 into a
concrete action and decision packet.

The question is:

```text
If full X-HD paper reproduction is still the objective, what exact artifacts or
external decisions are needed before more route/performance work is meaningful?
```

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5324_exact_input_acquisition_and_equivalence_decision_packet.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5324.exact_input_acquisition_and_equivalence_decision_packet.v1
```

## Source Evidence

Goal5324 is based on the current exact-provenance blocker evidence:

```text
Goal5317 - Figure-5 exact input acquisition gap matrix
Goal5318 - WaterBodies/BG exact-provenance search
Goal5319 - graphics exact-provenance search
Goal5320 - County/ZCTA source-conversion investigation
Goal5321 - OSM Lakes/Parks/AllNodes provenance search
Goal5322 - BraTS2020 access/conversion provenance
Goal5323 - public author repository / artifact availability sweep
```

## Main Decision

The next blocker is:

```text
exact_input_artifacts_or_explicit_exact_equivalence_acceptance
```

The packet explicitly sets:

```text
more_route_performance_work_is_next = false
```

Reason:

```text
The current RTDL route already has strong Level-B scalar evidence. Full paper
reproduction is blocked by exact input identity, not by another immediate route
optimization.
```

## Author Artifact Request

Minimum request:

```text
- checksum manifest for paper-run /local/storage/shared/HDDatasets inputs;
- input files or archived bundle if redistributable;
- hashes plus exact source URLs/snapshot/export parameters if files cannot be
  shared;
- preprocessing/conversion scripts used to produce X-HD-ready point inputs;
- exact paper command-line options where not fully captured by logs.
```

Families covered:

```text
graphics_stanford
geo_wkt
brats2020_validation
```

Examples:

```text
graphics:
  Dragon / HappyBuddha / AsianDragon / ThaiStatuette paper-run file bytes or
  sha256, plus preprocessing/scaling/translation scripts.

geo:
  dtl_cnty.wkt, uszipcode.wkt, USADetailedWaterBodies.wkt,
  USACensusBlockGroupBoundaries.wkt, lakes.bz2.wkt, parks.bz2.wkt, all_nodes
  inputs or hashes, plus WKT conversion/source vintage/precision policy.

BraTS:
  exact validation NIfTI list, NIfTI hashes, author NIfTI-to-point conversion
  function, modality/threshold/mask/coordinate policy, and converted point-set
  hashes if available.
```

## Public Exact-Equivalence Review Protocol

If author files/hashes cannot be obtained, public reconstruction can be
considered only under an explicit review protocol.

Required before exact-equivalence can even be considered:

```text
pinned public source URL or archive identifier;
source snapshot date/version/hash where applicable;
deterministic conversion/export script;
explicit geometry filtering/simplification/precision policy;
generated input file sha256;
author hd_exec rerun on generated inputs matching paper-log scalar;
RTDL route on the same generated inputs matching author rerun;
external review explicitly accepting exact-equivalence or a renamed bounded
public-reconstruction claim.
```

Not sufficient:

```text
matching point counts;
matching MBRs;
matching Gini/statistics;
matching HDResult alone;
matching author rerun on current public service snapshot;
checked-in author logs;
public repository source code without input hashes.
```

## Current Best Exact-Equivalence Candidate

The packet identifies:

```text
geo_waterbodies_blockgroups
```

as the best candidate if the owner wants an external exact-equivalence review.

Why:

```text
WaterBodies and BlockGroups full-public MBRs match paper logs;
point-count deltas are small;
author paper-config rerun with n_points_cell=8 reproduces paper-log HDResult;
RTDL exact-witness float64 aligns with author/paper float32 within the declared
numeric boundary.
```

Why not exact yet:

```text
no author WKT file hashes;
no proof current ArcGIS services are the exact author snapshot;
no byte-identical regeneration proof;
remaining point-count deltas are nonzero.
```

## Stop / Continue Matrix

Goal5324 defines four exits:

```text
author files/hashes acquired:
  run author and RTDL same-input gates, then performance matrix.

byte-identical regeneration pipeline acquired:
  generate files, record hashes, run author and RTDL gates.

external review accepts public reconstruction as exact-equivalent:
  rename claim precisely and run bounded Figure-5 matrix under accepted inputs.

no external artifacts and no exact-equivalence acceptance:
  stop full-paper claims at Level-B; publish blocker packet and avoid more
  performance work as paper reproduction.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5324_exact_input_acquisition_and_equivalence_decision_packet.json
py -m unittest tests.goal5324_xhd_exact_input_acquisition_packet_test
py -m unittest tests.goal5323_xhd_external_author_artifact_availability_test tests.goal5324_xhd_exact_input_acquisition_packet_test
```

Observed:

```text
Ran 7 tests OK
Ran 14 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5324 converts the exact-input blocker into an actionable acquisition and
review-decision packet. Full X-HD paper reproduction remains open, but next
progress must come from author files/hashes, byte-identical regeneration, or
an explicit exact-equivalence decision rather than more route optimization.
```

Forbidden:

```text
claiming exact input acquisition is complete;
claiming public reconstructions are exact without external acceptance;
claiming Figure 5 reproduction;
claiming full X-HD paper reproduction;
claiming author-vs-RTDL performance ratio;
running more performance work as paper reproduction before input identity
changes.
```

## POD Use

Goal5324 did not use POD.

POD is not expected until concrete input/provenance artifacts appear and need
author `hd_exec` or RTDL verification.
