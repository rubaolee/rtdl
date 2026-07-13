# Goal5323 - X-HD External Author Artifact Availability Sweep

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5323 asks the cross-cutting question left after Goals5318-5322:

```text
Does the public X-HD author repository or adjacent GitHub artifact surface
contain exact paper inputs, hashes, releases, LFS pointers, or download
instructions that would unblock full X-HD paper reproduction?
```

This goal is a provenance / availability sweep only. It does not run author
`hd_exec`, RTDL routes, POD code, or performance comparisons.

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5323_external_author_artifact_availability_sweep.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5323.external_author_artifact_availability_sweep.v1
```

## Evidence Checked

Public GitHub API / repository surfaces:

```text
https://github.com/pwrliang/X-HD
https://api.github.com/repos/pwrliang/X-HD
https://api.github.com/repos/pwrliang/X-HD/branches
https://api.github.com/repos/pwrliang/X-HD/releases
https://api.github.com/repos/pwrliang/X-HD/contents?ref=main
https://api.github.com/repos/pwrliang/X-HD/contents/expr?ref=main
https://api.github.com/repos/pwrliang/X-HD/git/trees/main?recursive=1
https://raw.githubusercontent.com/pwrliang/X-HD/main/README.md
https://raw.githubusercontent.com/pwrliang/X-HD/main/.gitignore
```

Local project evidence from Goals5318-5322:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5318_water_bg_exact_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5319_graphics_exact_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5320_county_zcta_source_conversion_investigation.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5321_osm_lakes_parks_allnodes_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5322_brats2020_access_conversion_provenance.json
```

## Repository Snapshot

Checked repository:

```text
full_name = pwrliang/X-HD
default_branch = main
main   = 7bf41c8442d059c94f4178355c6d5a10571d9658
paper  = 8c3846866052e1e8755210021f23fac2cbe8c3d6
hybrid = 4d9046a9e55d87f35daf81dd718444029fab56ce
release_count = 0
```

Top-level repository contents:

```text
.clang-format
.gitignore
.gitmodules
CMakeLists.txt
README.md
cmake/
expr/
src/
thirdparty/
vcpkg.json
```

No top-level `data/`, `datasets/`, or `HDDatasets/` directory was found.

The `.gitattributes` lookup returned 404, so no Git LFS pointer manifest was
found. The `.gitignore` ignores:

```text
*.log
*.pdf
*.zip
*.pkl
```

## Tree Sweep

Recursive tree summary for `main`:

```text
total_paths = 416
expr/logs JSON count = 281
data-like paths = []
input dataset blob extensions = []
```

The `expr/` directory contains paper scripts and checked-in logs:

```text
expr/run_fig5.sh
expr/run_lb.sh
expr/run_mem.sh
expr/run_radius_tuning.sh
expr/run_scalability.sh
expr/logs/
expr/for_the_paper/
```

This is useful paper evidence, but it is not the missing input dataset bundle.

## README Contract

The author README contains the `hd_exec` CLI example and states that
`variant=rt` is the X-HD algorithm in the paper.

It does not provide:

```text
dataset archive URLs;
HDDatasets download instructions;
input file hashes;
converted point-set hashes;
BraTS access/conversion instructions;
ArcGIS/OSM snapshot/export instructions.
```

## Local Workspace Relationship

The local X-HD app has public assets:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford
Paper-reproduction-apps/x-hd-paper/data/generated
```

These are Level-B public/source-matched assets and app-generated WKT/scaled
files. They are not author HDDatasets and do not prove byte identity with the
author's `/local/storage/shared/HDDatasets` inputs.

The current POD HDDatasets root remains absent according to prior provenance
goals; Goal5323 did not use POD because GPU execution cannot create missing
input provenance.

## Relationship To Goals5318-5322

Goal5323 strengthens the row-level blockers:

```text
Goal5318 WaterBodies/BG:
  no author WKT files or hashes found.

Goal5319 graphics:
  no author graphics files, hashes, or preprocessing proof found.

Goal5320 County/ZCTA:
  source/conversion identity remains blocked.

Goal5321 OSM:
  snapshot/filter/conversion identity remains blocked.

Goal5322 BraTS:
  data access and NIfTI-to-point conversion provenance remain blocked.
```

The public author repository does not close any of these gaps. It provides
source, scripts, and logs, not exact paper inputs.

## Exit Label

```text
external_author_dataset_artifacts_not_found__repo_source_logs_only
```

## Interpretation

Current status:

```text
public_author_repo_source_logs_only__exact_input_artifacts_absent
```

This means:

```text
Level-B public/source-matched work remains valid and useful.
Level-C exact dataset reproduction remains blocked.
Full paper reproduction remains unclosed.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5323_external_author_artifact_availability_sweep.json
py -m unittest tests.goal5323_xhd_external_author_artifact_availability_test
py -m unittest tests.goal5317_xhd_figure5_exact_input_gap_matrix_test tests.goal5322_xhd_brats2020_access_conversion_provenance_test tests.goal5323_xhd_external_author_artifact_availability_test
```

Observed:

```text
Ran 7 tests OK
Ran 21 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
The public X-HD author repository currently provides source code, scripts, and
checked-in logs, but no releases, LFS manifest, dataset directory, input blobs,
author input hashes, or HDDatasets bundle.
```

Forbidden:

```text
claiming the public GitHub repository contains exact paper input datasets;
claiming GitHub releases or LFS provide the missing datasets;
claiming checked-in author logs are exact input files;
promoting current Level-B public assets to exact paper inputs;
claiming Figure 5 reproduction;
claiming full X-HD paper reproduction;
claiming author-vs-RTDL performance ratio from this provenance sweep.
```

## POD Use

Goal5323 did not use POD.

POD is not expected until a concrete new input/provenance artifact appears and
needs author `hd_exec` or RTDL verification.
