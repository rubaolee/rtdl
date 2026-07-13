# Goal5295 - X-HD Figures 7 / 8 / 10 POD Dataset Availability Decision

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goals5292-5294 showed that Figures 7, 8, and 10 are blocked by missing
author-side numeric matrices:

```text
Figure 7: lb_comparison matrix missing
Figure 8: tune_radius matrix missing
Figure 10: scalability matrix missing
```

Goal5295 checks whether the current POD has the author datasets needed to
regenerate those missing matrices with the author scripts.

This goal does not run RTDL, does not regenerate author matrices, and does not
claim any figure reproduction.

## POD Preflight

Required wrapper command:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Result:

```text
POD_OK
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

This confirms the POD is usable through the project wrapper.

## Author Environment

The current POD has the existing author checkout and build:

```text
/tmp/xhd-goal5112/author
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

The author `expr/common.sh` still points to:

```text
DATASET_ROOT=/local/storage/shared/HDDatasets
SERIALIZE_ROOT=/local/storage/shared/HDDatasets/ser
```

But the current POD does not have:

```text
/local/storage/shared
/local/storage/shared/HDDatasets
```

Therefore exact author-script regeneration cannot proceed as-is.

## Required Dataset Paths

### Figure 7

Author script:

```text
/tmp/xhd-goal5112/author/expr/run_lb.sh
```

Required graphics files:

```text
/local/storage/shared/HDDatasets/graphics/dragon.ply
/local/storage/shared/HDDatasets/graphics/asian_dragon.ply
/local/storage/shared/HDDatasets/graphics/thai_statuette.ply
/local/storage/shared/HDDatasets/graphics/happy_buddha.ply
```

Current POD status:

```text
all missing
complete_for_author_regeneration_on_current_pod = false
```

### Figure 8

Author script:

```text
/tmp/xhd-goal5112/author/expr/run_radius_tuning.sh
```

Required geo files:

```text
/local/storage/shared/HDDatasets/geo/dtl_cnty.wkt
/local/storage/shared/HDDatasets/geo/uszipcode.wkt
/local/storage/shared/HDDatasets/geo/USADetailedWaterBodies.wkt
/local/storage/shared/HDDatasets/geo/USACensusBlockGroupBoundaries.wkt
/local/storage/shared/HDDatasets/geo/lakes.bz2.wkt
/local/storage/shared/HDDatasets/geo/parks.bz2.wkt
```

Required graphics files:

```text
/local/storage/shared/HDDatasets/graphics/dragon.ply
/local/storage/shared/HDDatasets/graphics/asian_dragon.ply
/local/storage/shared/HDDatasets/graphics/thai_statuette.ply
/local/storage/shared/HDDatasets/graphics/happy_buddha.ply
```

Current POD status:

```text
all missing
complete_for_author_regeneration_on_current_pod = false
```

### Figure 10

Author script:

```text
/tmp/xhd-goal5112/author/expr/run_scalability.sh
```

Required scalability input:

```text
/local/storage/shared/HDDatasets/geo/all_nodes.wkt
```

Current POD status:

```text
missing
complete_for_author_regeneration_on_current_pod = false
```

## Partial Temporary Inputs

The current POD does have a partial temporary graphics subset:

```text
/tmp/xhd_goal5234/data/dragon.ply
/tmp/xhd_goal5234/data/asian_dragon.ply
/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply
```

It does not have:

```text
/tmp/xhd_goal5234/data/thai_statuette.ply
/tmp/xhd_goal5234/data/happy_buddha.ply
```

Interpretation:

```text
This partial Dragon/Asian subset is not enough to regenerate the full author
Figure 7 or Figure 8 graphics matrices and does not cover Figure 10
all_nodes.wkt. It must not be promoted to exact paper input status.
```

## Decision

Goal5295 reports:

```text
status = pod_dataset_availability_checked__exact_hddatasets_missing__figures7_8_10_regeneration_blocked
figures7_8_10_exact_author_regeneration_possible_on_current_pod = false
figure7_reproduced = false
figure8_reproduced = false
figure10_reproduced = false
```

Current blocker:

```text
The current POD has the author build and scripts but does not have
/local/storage/shared/HDDatasets or the required graphics/geo/all_nodes input
files used by the author Figure 7, Figure 8, and Figure 10 scripts.
```

## Claim Boundary

Allowed:

```text
The current POD is usable through the wrapper.
The current POD lacks /local/storage/shared/HDDatasets.
The current POD cannot regenerate exact author Figure 7/8/10 matrices as-is.
Partial temporary Dragon/Asian inputs exist but are not exact paper inputs.
```

Not authorized:

```text
Figure 7 reproduced
Figure 8 reproduced
Figure 10 reproduced
author matrix regenerated
exact paper dataset reproduction
RTDL/author performance ratio
partial tmp inputs claimed as paper inputs
POD is broken
```

## Validation

Commands run:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "hostname; pwd; ls -ld /local/storage/shared/HDDatasets /local/storage/shared /tmp/xhd-goal5112 /tmp/xhd_goal5234 /tmp/rtdl_goal5281 2>&1"
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "cd /tmp/xhd-goal5112/author && sed -n '1,220p' expr/run_lb.sh && sed -n '1,220p' expr/run_radius_tuning.sh && sed -n '1,220p' expr/run_scalability.sh"
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "test -e ... required paths ..."
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5295_figures7_8_10_pod_dataset_availability_2026-07-09.json
py -m unittest tests.goal5295_xhd_figures7_8_10_pod_dataset_availability_test
```

Local Python may print the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

## Next Recommended Step

Choose one:

```text
1. If the owner can mount or provide /local/storage/shared/HDDatasets on a POD,
   rerun the author scripts or equivalent commands to regenerate Figure 7,
   Figure 8, and Figure 10 numeric matrices.
2. If exact inputs remain unavailable, define separately named Level-B
   diagnostics using available public / temporary inputs. Do not call those
   diagnostics Figure 7, Figure 8, or Figure 10 reproduction.
3. Move to another paper blocker whose author-side denominator can be recovered
   from available data.
```

Do not spend RTDL comparison work on Figures 7/8/10 until an author-side numeric
denominator exists.
