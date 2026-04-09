# Revision Report: Front-Door Cleanup And Example Naming

Date: 2026-04-05
Status: complete

## Purpose

This revision report records the final cleanup work applied after the larger
RTDL v0.1 packaging/reproduction push. The goal of this slice was not to change
backend semantics or performance. It was to make the repository front door more
professional, less confusing, and more aligned with the current project state.

The work covered three user-facing areas:

1. front-page bibliography and ownership wording
2. removal of repository-level paper packaging that is no longer part of the
   project surface
3. renaming the sorting example files so they read like examples rather than
   internal goal artifacts

## Why This Revision Was Needed

Before this cleanup:

- the GitHub front page still showed paper-package files and an old tracked
  `paper/rtdl_rayjoin_2026/` tree
- the README future-direction bibliography used redundant title links even
  though DOI links already served as the canonical paper links
- the README ownership wording was still informal
- the sorting example that users were supposed to learn from still had
  `goal97`-style names in the example, script, and test paths

None of those issues changed RTDL correctness, but together they made the repo
look more like an internal milestone workspace than a clean public project
front door.

## Changes Applied

### 1. README bibliography and ownership cleanup

Updated:

- `/Users/rl2025/rtdl_python_only/README.md`

Changes:

- kept the future-direction papers in chronological order
- removed redundant title hyperlinks
- kept DOI links as the canonical link target
- added a formal bottom-line ownership notice:
  - `Copyright (c) 2026 Rubao Lee. All rights reserved. RTDL and this repository are owned and maintained by Rubao Lee.`

### 2. Paper package removal

Removed from the live repo surface:

- root-level `rtdl_paper*` files
- root-level `rtdl_paper_assets/`
- tracked legacy paper tree:
  - `/Users/rl2025/rtdl_python_only/paper/rtdl_rayjoin_2026/`

Also cleaned live references in:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/handoff/CURRENT_STATUS.md`

Result:

- the repo front door no longer advertises a paper package
- GitHub root listing is cleaner
- live docs no longer point to removed paper files

### 3. Sorting example rename

Renamed canonical user-facing files:

- example:
  - `/Users/rl2025/rtdl_python_only/examples/rtdl_goal97_ray_hit_sorting.py`
  - to:
  - `/Users/rl2025/rtdl_python_only/examples/internal/rtdl_sorting.py`
- compact single-file example:
  - now:
  - `/Users/rl2025/rtdl_python_only/examples/internal/rtdl_sorting_single_file.py`
- demo script:
  - `/Users/rl2025/rtdl_python_only/scripts/goal97_ray_hit_sorting_demo.py`
  - to:
  - `/Users/rl2025/rtdl_python_only/scripts/rtdl_sorting_demo.py`
- test:
  - `/Users/rl2025/rtdl_python_only/tests/goal97_ray_hit_sorting_test.py`
  - to:
  - `/Users/rl2025/rtdl_python_only/tests/rtdl_sorting_test.py`

Updated the tutorial accordingly:

- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`

Behavioral intent:

- keep the same RTDL sorting example
- remove internal milestone naming from the canonical public-facing learning path

Boundary:

- this cleanup renamed the main example, compact single-file example, demo
  script, and test
- it did **not** rename every auxiliary Goal 97 variant file that still exists
  under `examples/`

## Validation

### Live-doc consistency checks

Verified:

- front-door docs no longer point to removed paper paths
- root-level `paper` and `rtdl_paper*` paths are gone from the repo surface

### Sorting example checks

Ran:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 examples/internal/rtdl_sorting_single_file.py 3 1 4 1 5 0 2 5
```

Observed result:

- ascending and descending outputs matched Python sorting

Ran:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.rtdl_sorting_test
```

Observed result:

- `11` tests
- `OK`
- `4` skipped

Environment note:

- on the local Mac, the same pre-existing `geos_c` linker noise still appears
  before the final passing unittest result
- that is an environment issue already known from earlier local runs, not a new
  regression introduced by this rename/cleanup work

## What This Revision Does Not Claim

- no backend performance improvement
- no new workload closure
- no new correctness result
- no new release claim

This is a repository polish and consistency revision, not a system-capability
goal.

## Final Result

This revision succeeds because the repo now presents a cleaner public face:

- the front page is more professional
- ownership language is explicit
- the obsolete paper packaging is removed
- the canonical sorting example paths now read like user-facing examples
  instead of internal goal bookkeeping

That makes the repo easier to browse, easier to teach from, and easier to keep
aligned going forward.
