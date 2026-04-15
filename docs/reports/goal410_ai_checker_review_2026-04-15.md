# Goal 410 AI Checker Review

**Date:** 2026-04-15  
**Role:** Checker  
**Verdict:** No blockers. Goal 410 is acceptable within its stated honesty boundary.

---

## Files Read

- `docs/goal_410_tutorial_and_example_cross_platform_check.md`
- `docs/reports/goal410_tutorial_and_example_cross_platform_check_2026-04-15.md`
- `docs/reports/goal410_macos_tutorial_example_check_2026-04-15.json` (header + summary)
- `docs/reports/goal410_linux_tutorial_example_check_2026-04-15.json` (header + summary)
- `docs/reports/goal410_windows_tutorial_example_check_2026-04-15.json` (header + summary)
- `README.md`
- `docs/quick_tutorial.md`
- `docs/release_facing_examples.md`
- `docs/tutorials/README.md`
- `docs/tutorials/graph_workloads.md`
- `examples/README.md`
- `examples/rtdl_graph_bfs.py`
- `examples/rtdl_graph_triangle_count.py`
- `scripts/goal410_tutorial_example_check.py`

---

## Check: Fresh-Checkout Setup Instructions

**Status: Correct on all three platforms.**

The README and `quick_tutorial.md` both now use a local virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows coverage is complete: both `cmd.exe` and PowerShell variants are shown
with `py -3 -m venv`. The Debian/Ubuntu `ensurepip` failure case is called out
with the exact fix (`sudo apt install python3-venv`). The Linux GPU backend
build steps (`make build-optix`, `make build-vulkan`) appear in both the README
and `quick_tutorial.md`. The three public entry-point docs (README,
`quick_tutorial.md`, `release_facing_examples.md`) are consistent — no
divergence in setup steps.

---

## Check: Tutorial And Release-Facing Example Surface

**Status: Runnable and honestly described.**

The tutorial ladder in `docs/tutorials/README.md` now has 7 steps (0–6), with
graph workloads at step 5 pointing to the new `graph_workloads.md`. All
commands shown in `graph_workloads.md` are exercised in the harness. The
expected output excerpts in the tutorial match what the example CLIs emit (JSON
with `app` and `rows` fields).

`release_facing_examples.md` covers three released lines:
- v0.2.0 geometry workloads (segment/polygon)
- v0.4.0 nearest-neighbor workloads
- v0.6.1 graph workloads

Commands are consistent with what the harness tests. The nearest-neighbor
honesty boundary is explicitly stated: OptiX and Vulkan are functional in the
runtime but are not exposed via the public top-level nearest-neighbor CLIs
today. That boundary note is present and clear.

---

## Check: New Graph Examples As Bounded Release-Facing CLIs

**Status: Properly bounded.**

Both `rtdl_graph_bfs.py` and `rtdl_graph_triangle_count.py`:
- Accept `--backend` via `argparse` over all five choices
  (`cpu_python_reference`, `cpu`, `embree`, `optix`, `vulkan`)
- Use a fixed small test case (4 vertices, 5–6 edges)
- Print JSON to stdout and exit cleanly via `raise SystemExit(main())`
- Do not claim to be full graph algorithms — the tutorial explicitly notes that
  BFS expansion is one bounded kernel step and that multi-level iteration stays
  in Python

The kernels follow the standard RTDL shape (`input -> traverse -> refine ->
emit`), consistent with the rest of the released surface.

---

## Check: Consolidated Report vs. Raw Machine Reports

**Status: Exact match.**

| Machine            | Raw JSON summary                          | Consolidated report claim       |
|--------------------|-------------------------------------------|---------------------------------|
| macos-local        | 29 passed / 0 failed / 6 skipped / 35 total | 29 passed / 0 failed / 6 skipped |
| linux-lestat-lx1   | 35 passed / 0 failed / 0 skipped / 35 total | 35 passed / 0 failed / 0 skipped |
| windows-lestat-win | 29 passed / 0 failed / 6 skipped / 35 total | 29 passed / 0 failed / 6 skipped |

Backend availability in the JSON headers matches the consolidated report
exactly: macOS and Windows have `optix=false` and `vulkan=false`; Linux has
both `true`. The 6 skipped cases on macOS and Windows are the six
`linux_only=True` entries in the harness: `hello_world_optix`,
`hello_world_vulkan`, `graph_bfs_optix`, `graph_bfs_vulkan`,
`graph_triangle_optix`, `graph_triangle_vulkan`. This matches exactly what the
script encodes.

---

## Check: Harness Case Count

`public_cases()` in `goal410_tutorial_example_check.py` defines exactly 35
entries, matching `total: 35` in all three machine reports. Manually verified:

- 6 hello-world variants (2 linux_only)
- 1 sorting_demo
- 4 segment/polygon
- 6 nearest-neighbor (3 fixed_radius, 3 knn)
- 10 graph (5 per workload × 2 workloads; 4 of the 10 are linux_only)
- 4 app-style (service_coverage, event_hotspot, facility_knn, road_hazard)
- 4 visual demo (lit_ball, hidden_star, smooth_camera, render_chunked_video)

Total: 6 + 1 + 4 + 6 + 10 + 4 + 4 = 35. Correct.

---

## Check: Public Claims

No overstated claims found.

- README "OS Support At A Glance" correctly marks Linux as primary and
  macOS/Windows as bounded.
- "Current Limits" section is explicit: visual demos are not a renderer claim;
  PostGIS is not an RTDL backend; backend availability is not identical on
  every machine.
- The graph line does not claim full graph algorithms — only the bounded RT
  kernel steps (`bfs_expand`, `triangle_match`).
- The v0.6.1 label is consistently applied wherever the graph surface is
  mentioned.

---

## Minor Observations (Not Blockers)

1. `release_facing_examples.md` presents v0.4.0 nearest-neighbor before
   v0.2.0 geometry. The version ordering is reversed but the sections are
   clearly labeled and the content is correct.

2. The Linux machine JSON uses `/usr/bin/python3` rather than a venv Python.
   The consolidated report discloses this honestly: "the host already had the
   required Python packages available for the validation run." This is a
   legitimate one-time machine state, not a contradiction of the setup docs.

3. The macOS JSON uses a temp path (`/private/tmp/rtdl_goal410_venv_mac/...`)
   rather than a repo-local `.venv`. The public docs correctly instruct users
   to create `.venv` in the checkout root; the temp path is a test-run choice,
   not a doc contradiction.

---

## Verdict

**Goal 410 is acceptable within its stated honesty boundary.**

Required outcomes per goal spec:

- Correct fresh-checkout setup for macOS, Linux, Windows ✓
- Real public graph example CLIs under `examples/` ✓
- Tutorial ladder and release-facing docs pointing to runnable commands ✓
- Public command surface checked on all three maintained machines ✓
- `cpu_python_reference` and `cpu` on all machines ✓
- `embree` on all machines ✓
- `optix` and `vulkan` on the Linux GPU host ✓

No misleading public claims. No failures in any machine run. No blocker.
