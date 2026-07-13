# Goal5090 RT-DBSCAN Requirements Audit And First Target

Date: 2026-07-07

## Verdict Label

```text
completed_rt_dbscan_requirements_audit_and_core_count_first_target
```

## Purpose

Goal5090 audits the RT-DBSCAN paper-app requirements after the Goal5089
scaffold and decides the first bounded target.

The goal is not full paper reproduction. It is to choose the first executable
gate that can advance the paper app without overclaiming.

## Author Artifact Status

Located candidate author artifact:

```text
repository: https://github.com/vani-nag/OWLRayTracing
branch: rt-dbscan
commit: 92749fe82ed001e5b7303265d4a2a73aa1bbf529
sample path: samples/cmdline/s02-rtdbscan
```

Evidence:

- `git ls-remote --heads https://github.com/vani-nag/OWLRayTracing.git`
  reports `refs/heads/rt-dbscan` at
  `92749fe82ed001e5b7303265d4a2a73aa1bbf529`.
- GitHub tree inspection for that commit shows
  `samples/cmdline/s02-rtdbscan`.
- The repository README identifies the project as general-purpose computation
  on RT cores and lists RT-DBSCAN as an implemented clustering application.

Boundary:

- The author artifact has not been cloned or built in this goal.
- No AuthorOfficial comparator is established yet.
- Exact paper inputs remain unpinned.

## First Bounded Target Decision

Chosen first target:

```text
fixed-radius core-count smoke
```

Why:

- It exercises the RTDL fixed-radius/count-threshold surface relevant to
  RT-DBSCAN.
- It is smaller and cleaner than full DBSCAN labels or component signatures.
- Existing RTDL app code already exposes `--output-mode core_count`.
- It can be checked by exact integer equality against the RTDL CPU
  reference/oracle path.

The next stronger target should be:

```text
prepared fixed-radius core-count or core-flag AuthorOfficial gate
```

only after the author artifact is built and an input/comparator policy is
chosen.

## Local Smoke Gate

Added:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_core_count_smoke.py
```

The wrapper reuses:

```text
examples/current/apps/ml/rtdl_dbscan_clustering_app.py
```

Command:

```text
py Paper-reproduction-apps/rt-dbscan-paper/scripts/run_core_count_smoke.py
```

Result:

```text
status: pass
backend: cpu_python_reference
copies: 1
point_count: 8
core_count: 7
oracle_core_count: 7
matches_oracle: true
```

This is a local RTDL/oracle smoke only. It is not an author-comparator gate and
not a paper reproduction result.

## Additional Local Checks

Existing benchmark CPU reference:

```text
py examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode cpu_reference --dataset tiny
```

Result:

```text
matches_reference: true
point_count: 9
core_count: 8
noise_count: 1
```

SciPy external baseline check:

```text
py examples/current/apps/ml/rtdl_dbscan_clustering_app.py --backend scipy --copies 1 --output-mode core_count
```

Result:

```text
blocked locally: SciPy is not installed
```

Therefore SciPy is not used as a local requirement gate in this batch.

## Manifest Update

Updated:

```text
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
Paper-reproduction-apps/rt-dbscan-paper/README.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/README.md
```

The manifest now records:

- candidate author artifact repository, branch, commit, and sample path,
- first local smoke comparator as RTDL CPU reference/oracle,
- first output policy as exact integer `core_count`,
- exact paper input and AuthorOfficial comparator as pending.

## Claim Boundary

This goal does not claim:

- RT-DBSCAN paper reproduction,
- exact paper input reproduction,
- author comparator success,
- whole-program DBSCAN speedup,
- native DBSCAN engine ABI,
- automatic route selection,
- performance result.

## Next Recommended Goal

Goal5091 should prepare an AuthorOfficial build/run plan:

1. clone `vani-nag/OWLRayTracing` at
   `92749fe82ed001e5b7303265d4a2a73aa1bbf529`,
2. inspect `samples/cmdline/s02-rtdbscan`,
3. identify its command-line input/output protocol,
4. decide whether a small same-input core-count comparator can be extracted,
5. avoid full DBSCAN or performance claims until that comparator exists.
