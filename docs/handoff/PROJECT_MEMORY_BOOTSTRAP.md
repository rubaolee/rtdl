# RTDL Project Memory Bootstrap

Date: 2026-04-07
Purpose: one-file context recovery for future Codex sessions

## 1. What This Repo Is

RTDL is a Python-hosted DSL and runtime for non-graphical ray-tracing-style
workloads. The project started with a RayJoin-heavy v0.1 trust-anchor slice and
now has a broader live v0.2 line on `main`.

Current local repo:

- `/Users/rl2025/rtdl_python_only`

Current live branch position when this bootstrap was written:

- `main`
- published through released `v0.2.0` plus post-release doc/demo cleanup

## 2. Current Trust Model

There are two status layers and both matter:

### Archived trust anchor

- `v0.1.0` at frozen commit:
  - `85fcd90a7462ef01137426af7b0224e7da518eb4`
- this is the bounded reviewed RayJoin-heavy baseline

### Live branch

- current `main` is the released `v0.2.0` line
- accepted frozen v0.2 workload surface:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- it is broader than v0.1 and strongly tested on the accepted Linux platform
- it is the released and tagged `v0.2.0` line

## 3. Platform Reality

This is critical. Do not forget it.

### Primary platform

Linux is the primary RTDL development and validation platform.

Use it for:

- PostGIS-backed correctness
- large-scale performance
- OptiX
- Vulkan
- whole-system validation

Primary host used in this project:

- `lestat@192.168.1.20`
- repo path:
  - `/home/lestat/work/rtdl_python_only`

### Local Mac

This Mac is a limited local platform.

Use it for:

- Python reference
- native CPU/oracle where available
- Embree-oriented local work
- documentation
- focused local tests

Do not treat this Mac as the primary validation platform for:

- OptiX
- Vulkan
- Linux/PostGIS large-row evidence
- whole-system final closure

Known local boundary:

- broad local unit surface still hits missing `geos_c` linkage in some groups

## 4. Current Supported Feature Surface

The canonical feature homes are now here:

- [docs/features/README.md](/Users/rl2025/rtdl_python_only/docs/features/README.md)

Supported features:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `point_nearest_segment`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Important feature boundaries:

- `overlay` is still an overlay-seed workload, not full polygon overlay
- the Jaccard line is narrow:
  - orthogonal integer-grid polygons
  - unit-cell area semantics
  - pathology-style usage
  - not generic continuous polygon Jaccard

## 5. The Strongest Current Stories

### v0.1 trust-anchor story

- long exact-source `county_zipcode`
- positive-hit `pip`
- Embree and OptiX faster than PostGIS on accepted prepared/repeated boundaries
- Vulkan parity-clean there but slower

### v0.2 live branch story

- two closed segment/polygon families:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
- Linux/PostGIS-backed correctness and performance
- parity clean through accepted large deterministic rows
- current large-row stress evidence reached `x4096`

Representative accepted `x4096` numbers from Goal 131:

`segment_polygon_hitcount`

- PostGIS `1.167043 s`
- CPU `0.149339 s`
- Embree `0.133990 s`
- OptiX `0.135224 s`
- Vulkan `0.150495 s`

`segment_polygon_anyhit_rows`

- PostGIS `0.419224 s`
- CPU `0.154114 s`
- Embree `0.143328 s`
- OptiX `0.140265 s`
- Vulkan `0.136616 s`

### Narrow Jaccard story

- `polygon_pair_overlap_area_rows` is closed as the first primitive
- `polygon_set_jaccard` is closed in narrow form
- public-data-derived Linux/PostGIS audit exists using MoNuSeg conversion
- strongest implementation/validation story is Python + native CPU + PostGIS
- public `embree`, `optix`, and `vulkan` run surfaces are now accepted on
  Linux through documented native CPU/oracle fallback

Representative accepted public-data-derived Goal 141 row:

- source XML:
  - `TCGA-38-6178-01Z-00-DX1.xml`
- selected nuclei:
  - `16`
- base polygons per side after unit-cell conversion:
  - `8556`
- `copies=1`
  - Python `0.135213 s`
  - CPU `0.061195 s`
  - PostGIS `4.362636 s`
  - parity clean

Representative accepted Goal 146 Linux stress rows:

- `copies=64`
  - Python `8.279358 s`
  - CPU `3.978596 s`
  - Embree `3.699990 s`
  - OptiX `3.670949 s`
  - Vulkan `3.636281 s`
  - all consistency vs Python: `true`
- `copies=128`
  - Python `16.526160 s`
  - CPU `7.673124 s`
  - Embree `7.421700 s`
  - OptiX `7.435530 s`
  - Vulkan `7.400839 s`
  - all consistency vs Python: `true`

## 6. Most Important Completed Goal Lines

### v0.2 planning / process

- Goals `107` to `109`
  - roadmap, scope charter, archived v0.1 baseline separation

### segment/polygon hitcount line

- Goals `110`, `112`, `114`, `115`, `116`, `118`, `119`, `120`, `121`, `122`, `123`
  - feature closure
  - Linux/PostGIS validation
  - backend audit
  - candidate-index redesign
  - all four primary backends now strong on the accepted large deterministic rows

### second segment/polygon family

- Goals `126`, `127`, `128`, `129`
  - `segment_polygon_anyhit_rows`
  - Linux/PostGIS parity/perf
  - generate-only support

### midterm/system closure

- Goals `130`, `131`, `132`, `133`, `134`, `135`
  - test plan and execution
  - Linux stress audit
  - user docs
  - execution report
  - process audit
  - whole-system midterm check

### Jaccard line

- Goals `136`, `137`, `138`, `139`, `140`, `141`, `142`, `146`
  - evaluate feasibility from old paper direction
  - narrow contract charter
  - overlap-area primitive
  - public pathology data conversion path
  - narrow `polygon_set_jaccard`
  - public-data-derived Linux/PostGIS audit
  - docs and generate-only
  - Linux wrapper-surface stress and consistency audit

### feature-home docs

- Goal `143`
  - one canonical docs directory per supported feature

## 7. Current Whole-System State

The best single recent whole-system checkpoint is:

- [goal135_system_midterm_check_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal135_system_midterm_check_2026-04-06.md)

Current honest reading:

- Linux whole-system matrix is green on the accepted primary platform
- local Mac is not broad whole-system green because of `geos_c` linkage gaps
- this is a platform limitation, not a new Linux regression
- the best current release-readiness checkpoint is Goal 150, not just Goal 135

## 7A. Current v0.3 Visual-Demo State

This is the current best short reading:

- Goal 164 already closed the bounded 3D RTDL ray/triangle visual-demo surface
  on Linux across:
  - `embree`
  - `optix`
  - `vulkan`
- Goal 166 produced the first real Windows Embree Earth-like movie
- Goal 167 added a NumPy-backed host-side fast path and a diagonal public movie
  line
- the current recommended public-facing artifact is now the smoother
  `softvis` Windows Embree MP4:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024.mp4`

Important honesty boundary:

- the polished public artifact is currently an Embree-driven Windows movie
- the broader backend target still includes:
  - `embree`
  - `optix`
  - `vulkan`
- the fact that the polished ad artifact is currently Embree-based does not
  erase the already-closed Linux 3D backend surface

## 8. Documentation Surface To Trust First

Read in this order when recovering context:

1. this file
2. [docs/features/README.md](/Users/rl2025/rtdl_python_only/docs/features/README.md)
3. [docs/v0_2_user_guide.md](/Users/rl2025/rtdl_python_only/docs/v0_2_user_guide.md)
4. [docs/rtdl_feature_guide.md](/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md)
5. [docs/rtdl/README.md](/Users/rl2025/rtdl_python_only/docs/rtdl/README.md)
6. [docs/reports/v0_2_feature_status_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/v0_2_feature_status_2026-04-06.md)
7. [docs/reports/goal135_system_midterm_check_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal135_system_midterm_check_2026-04-06.md)

For the Jaccard line specifically:

- [docs/reports/goal136_jaccard_similarity_evaluation_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal136_jaccard_similarity_evaluation_2026-04-06.md)
- [docs/reports/goal140_polygon_set_jaccard_closure_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal140_polygon_set_jaccard_closure_2026-04-06.md)
- [docs/reports/goal141_public_jaccard_linux_audit_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal141_public_jaccard_linux_audit_2026-04-06.md)

## 9. Review Workflow

Normal closure rule:

- internal review coverage plus Codex consensus
- and, when required by the current process bar, external review using:
  - Claude
  - Gemini

Practical external-review rule learned in this project:

- small handoff file
- small explicit file list
- ask only for:
  - `Verdict`
  - `Findings`
  - `Summary`

Claude/Gemini workflow lessons:

- interactive terminal use is more reliable than one-shot subprocess use
- Claude may require a long wait window
- Gemini must be run from the repo directory, not `/Users/rl2025`, because it
  may scan the cwd tree and hit `.Trash` permission errors

Recommended external-review prompt shape:

- “Please read `<handoff>` and review the listed package for repo accuracy,
  technical honesty, and consistency, then return exactly three short sections
  titled `Verdict`, `Findings`, and `Summary`.”

## 10. Remote Execution Workflow

Linux host:

- `lestat@192.168.1.20`

If SSH aliasing is not present, use direct form:

```bash
sshpass -p 'ppppppp' ssh -o StrictHostKeyChecking=no lestat@192.168.1.20 'echo OK'
```

Typical sync:

```bash
sshpass -p 'ppppppp' rsync -av --delete /Users/rl2025/rtdl_python_only/ \
  lestat@192.168.1.20:/home/lestat/work/rtdl_python_only/
```

Typical remote command shape:

```bash
sshpass -p 'ppppppp' ssh -o StrictHostKeyChecking=no lestat@192.168.1.20 '
  cd /home/lestat/work/rtdl_python_only &&
  PYTHONPATH=src:. python3 <script> ...
'
```

When reporting Linux results:

- do not claim them unless they actually ran remotely
- pull artifacts back into `docs/reports/...`
- keep the report honest if a larger run timed out or had to be reduced

## 11. Generate-Only Status

Generate-only is intentionally narrow.

Current accepted support includes:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- one authored `polygon_set_jaccard` entry

Do not describe it as broad general code generation.

## 12. Things Future Codex Should Not Forget

- do not overclaim RT-core maturity from the current segment/polygon speed wins
- do not describe `overlay` as full polygon overlay
- do not describe Jaccard as generic continuous polygon Jaccard
- do not describe the Goal 146 Jaccard stress numbers as native
  Embree/OptiX/Vulkan performance results
- do not treat this Mac as the primary validation platform
- do not regress feature continuity on current `main`
- do not use old stale handoff docs as the current project state

## 13. If Starting A New Session

Do this first:

1. read this file
2. run `git status --short`
3. read `docs/features/README.md`
4. read the most relevant recent goal report for the active feature line
5. verify whether the requested task needs Linux/PostGIS or can be done locally
6. if external review is required, prepare a small handoff file first

## 14. Why This File Exists

This repo has a long history and the conversation context can get large. This
file is meant to be the one compact ignition doc that lets a later Codex
session recover the important memory without replaying the entire thread.
