# Goal5215 Public Artifact Availability Sweep Result

Date: 2026-07-09

## Verdict

```text
completed_public_artifact_sweep__source_logs_scripts_available__exact_inputs_not_available
```

## Purpose

Goal5214 proved the current POD does not contain the paper input root:

```text
/local/storage/shared/HDDatasets
```

Goal5215 asks the next question:

```text
Can we get the exact X-HD paper inputs from public web/repository artifacts,
or can the author repository deterministically regenerate them?
```

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5215_public_artifact_availability_sweep_2026-07-09.json
```

## Public Sources Checked

Checked:

```text
https://github.com/pwrliang/X-HD
https://gengl.me/publications/ics26/
https://rubaolee.github.io/paper_pdfs/2026-xhd.pdf
web search for X-HD / HDDatasets / dataset terms
```

Findings:

```text
The GitHub repository is a source-code release.
The GitHub page reports no releases and no packages.
The publication page identifies the paper but does not expose a dataset
download.
The paper PDF points to the source-code repository, not a dataset archive.
Search found source/paper pages and unrelated HD results, but no public
HDDatasets archive or exact paper input bundle.
```

## Git Metadata Sweep

Remote refs:

| ref | commit |
|---|---|
| main | `7bf41c8442d059c94f4178355c6d5a10571d9658` |
| paper | `8c3846866052e1e8755210021f23fac2cbe8c3d6` |
| hybrid | `4d9046a9e55d87f35daf81dd718444029fab56ce` |

Tags:

```text
none
```

Tracked tree audit:

| branch | tracked paths | dataset-like assets | JSON logs | scripts/logs available? |
|---|---:|---:|---:|---|
| main | 380 | 0 | 281 | yes |
| paper | 41,888 | 0 | 41,755 | yes |
| hybrid | 121 | 0 | 0 | yes |

Dataset-like assets here means tracked files ending in common paper input
extensions:

```text
.ply, .off, .wkt, .nii, .nii.gz, .tar, .zip, .gz, .bz2, .7z, .csv
```

Result:

```text
No tracked input datasets were found in the public repository branches.
```

## Interpretation

What exists:

```text
source code
author scripts
author logs
paper-branch workload paths and HDResult metadata
public same-source Stanford graphics files acquired by our app
```

What does not exist in current public evidence:

```text
author paper input bytes
file hashes for the paper input bytes
byte-identical converted point sets
deterministic public reconstruction provenance proving exact identity
GitHub release/package containing HDDatasets
```

Therefore:

```text
Level-C exact paper dataset reproduction remains unsupported.
Level-B same-source representative reproduction remains the strongest current
supported status.
```

## What This Means For "Can We Copy It?"

We can copy and run:

```text
author source code
author build system
author CLI
author scripts
author JSON logs
```

We cannot copy from the public repository:

```text
the exact paper input datasets
the /local/storage/shared/HDDatasets tree
the serialized input cache under /local/storage/shared/HDDatasets/ser
```

Without those files, full paper reproduction cannot honestly be closed. The
best available route is representative reproduction on public same-source
inputs plus a precise statement that exact paper input identity remains open.

## Claim Boundary

Allowed:

```text
The public repository and web artifacts provide source, scripts, and logs, but
not the exact paper input datasets. The current project can support Level-B
same-source representative reproduction, not Level-C exact paper dataset
reproduction.
```

Not authorized:

```text
full X-HD paper reproduction
exact paper dataset reproduction
author-vs-RTDL performance ratio
author parity
treating public Stanford files as exact paper input bytes without file/hash
proof
```

## Next Recommendation

Stop searching the same public source-code repository for datasets unless new
evidence appears. Next useful work should be:

1. send Goals5211-5215 and the midterm packet for review;
2. consolidate the Level-B representative reproduction packet;
3. if the owner wants Level-C, pursue external acquisition of exact inputs or
   author-provided hashes / deterministic conversion provenance.
