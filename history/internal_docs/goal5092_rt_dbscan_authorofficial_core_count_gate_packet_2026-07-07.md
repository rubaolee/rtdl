# Goal5092 RT-DBSCAN AuthorOfficial Core-Count Gate Packet

Date: 2026-07-07

## Verdict

`completed_pod_ready_authorofficial_core_count_gate_packet__not_executed`

Goal5092 creates a POD-ready AuthorOfficial comparator packet for the first
bounded RT-DBSCAN paper-app target. It does not claim full paper reproduction or
performance. The packet is prepared and locally smoke-tested, but the patched
author binary has not yet been built or run on CUDA/OWL hardware.

## Objective

Convert the RT-DBSCAN scaffold from "author artifact located" to "bounded
AuthorOfficial core-count gate ready to run."

The first bounded target is:

```text
same input, same epsilon, same minPts, integer core_count equality
```

This targets the author's call-1 core point identification phase only.

## Author Artifact

Pinned candidate:

```text
repository: https://github.com/vani-nag/OWLRayTracing
branch: rt-dbscan
commit: 92749fe82ed001e5b7303265d4a2a73aa1bbf529
sample: samples/cmdline/s02-rtdbscan
command: ./sample02-rtdbscan [inFile] [size] [eps] [minPts] [outFile]
```

The author sample reads 3D points, runs two launches, and normally appends only
execution time to the output file. The packet therefore adds a minimal
AuthorOfficial patch that exposes `core_count` after call 1.

## Added Files

```text
Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/tiny3d_core_count.csv
Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/tiny3d_core_count_expected.json
Paper-reproduction-apps/rt-dbscan-paper/author_patches/goal5092_authorofficial_core_count_output.patch
Paper-reproduction-apps/rt-dbscan-paper/scripts/setup_authorofficial_core_count.sh
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_core_count_gate.py
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_core_count_gate_local_cpu_summary.json
tests/goal5092_rt_dbscan_authorofficial_gate_packet_test.py
```

Docs updated:

```text
Paper-reproduction-apps/rt-dbscan-paper/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/README.md
Paper-reproduction-apps/rt-dbscan-paper/results/README.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
```

## Fixture

`tiny3d_core_count.csv` is a bounded synthetic 3D input:

```text
point_count=8
epsilon=0.35
minPts=3
expected_core_count=7
```

It is not an exact paper input. It exists to establish the first same-input
AuthorOfficial gate.

## AuthorOfficial Patch

Patch:

```text
author_patches/goal5092_authorofficial_core_count_output.patch
```

It does two things:

1. Replaces an absolute local include path in `deviceCode.cu` with the generic
   OWL include path.
2. Changes only author-side output in `hostCode.cpp`, adding a JSON line with:

```text
schema
point_count
epsilon
min_points
core_count
core_points_time_sec
cluster_formation_time_sec
build_time_sec
total_time_sec
```

It does not change the author's device kernels, traversal logic, or union logic.

## Gate Runner

Runner:

```text
scripts/run_authorofficial_core_count_gate.py
```

Modes:

- `--backend cpu_reference`: local RTDL-side reference for script/fixture
  validation.
- `--backend optix`: POD RTDL path using
  `prepare_optix_fixed_radius_count_threshold_3d` and
  `fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns`.
- optional `--author-binary`: runs patched `sample02-rtdbscan` and compares
  exact integer `core_count`.

The runner returns nonzero if an author binary is supplied and the integer
counts do not match.

## Local Verification

Commands run:

```text
git -C %TEMP%/OWLRayTracing_rt_dbscan_goal5092 reset --hard 92749fe82ed001e5b7303265d4a2a73aa1bbf529
git -C %TEMP%/OWLRayTracing_rt_dbscan_goal5092 apply Paper-reproduction-apps/rt-dbscan-paper/author_patches/goal5092_authorofficial_core_count_output.patch
git -C %TEMP%/OWLRayTracing_rt_dbscan_goal5092 diff --check

py Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_core_count_gate.py --backend cpu_reference --summary Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_core_count_gate_local_cpu_summary.json

py -m unittest tests.goal5092_rt_dbscan_authorofficial_gate_packet_test
```

Observed:

```text
patch applies: yes
git diff --check: pass
local CPU gate: core_count=7
author_comparator_used: false
Goal5092 tests: Ran 3, OK
```

The local Python runtime prints `Could not find platform independent libraries
<prefix>` before successful Python commands. Return codes were zero for the gate
and tests.

## Claim Boundary

Authorized:

- bounded same-input core-count gate packet is ready for POD execution;
- local RTDL CPU-reference gate passes with `core_count=7`;
- author patch is output-only for the bounded comparator, plus an include-path
  portability fix.

Not authorized:

- full RT-DBSCAN paper reproduction;
- exact paper input reproduction;
- full DBSCAN labels or cluster expansion parity;
- author performance comparison;
- whole-program speedup;
- native DBSCAN ABI;
- automatic route selection;
- any public performance claim.

## Next Step

Goal5093 should run the packet on a CUDA/OWL-capable POD:

1. run `scripts/setup_authorofficial_core_count.sh`;
2. run `scripts/run_authorofficial_core_count_gate.py --backend optix --author-binary ...`;
3. require `author_comparator_used=true`, `matched=true`, and
   `rtdl.core_count == author.core_count == 7`;
4. keep all non-claims above intact.
