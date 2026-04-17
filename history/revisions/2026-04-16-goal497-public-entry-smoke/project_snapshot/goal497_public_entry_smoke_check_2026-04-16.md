# Goal 497: Public Entry Smoke Check

Date: 2026-04-16

Status: PASS

## Scope

This check validates the public entry path after Goal 496:

- front page
- docs index
- current architecture
- quick tutorial
- release-facing examples
- examples index
- feature guide/index
- graph and DB tutorials
- complete history map
- revision dashboard

## Public Docs Checked

- `README.md`
- `docs/README.md`
- `docs/current_architecture.md`
- `docs/quick_tutorial.md`
- `docs/release_facing_examples.md`
- `examples/README.md`
- `docs/features/README.md`
- `docs/rtdl_feature_guide.md`
- `docs/tutorials/README.md`
- `docs/tutorials/db_workloads.md`
- `docs/tutorials/graph_workloads.md`
- `history/COMPLETE_HISTORY.md`
- `history/revision_dashboard.md`

## New-User Commands Run

All commands were run from the repository root with `PYTHONPATH=src:.`.

| Check | Command | Result |
| --- | --- | --- |
| Hello world | `python examples/rtdl_hello_world.py` | PASS |
| Geometry example | `python examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16` | PASS |
| Graph example | `python examples/rtdl_graph_bfs.py --backend cpu_python_reference` | PASS |
| DB kernel example | `python examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference` | PASS |
| DB app demo | `python examples/rtdl_v0_7_db_app_demo.py --backend auto` | PASS |

The DB app demo selected the local `embree` backend automatically on this macOS
host and completed successfully.

## Link And Wording Checks

Result:

- broken relative links in checked public docs: `0`
- missing required public-positioning phrases: `0`
- unsupported "10x runtime speedup" claim: not found
- required "10x authoring-burden" framing: present
- required v0.7 support-matrix / release-boundary pointers: present

## Machine Evidence

Machine-readable result:

- `docs/reports/goal497_public_entry_smoke_check_2026-04-16.json`

Summary from JSON:

- `valid`: `true`
- `link_failures`: `[]`
- `phrase_failures`: `[]`
- all command results returned `ok: true`

## Verdict

Goal 497 public-entry smoke check is PASS. The pushed public docs are consistent
with the current v0.7 state and the refreshed RTDL user-value framing.
