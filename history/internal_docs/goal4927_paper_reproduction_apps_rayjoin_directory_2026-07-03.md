# Goal4927: Paper-Reproduction Apps RayJoin Directory

Date: 2026-07-03

## Purpose

Create a first-class paper-reproduction app line that is parallel to the
benchmark app line. The first app is the RayJoin paper reproduction app, with
Section 5.2, Section 5.3, and bounded Section 5.7 programs collected under one
reader-facing directory.

## Files Added

| Path | Purpose |
| --- | --- |
| `Paper-reproduction-apps/README.md` | Defines the paper-reproduction app line and distinguishes it from benchmark apps. |
| `Paper-reproduction-apps/rayjoin-paper/README.md` | User-facing RayJoin app guide, commands, design boundary, and evidence links. |
| `Paper-reproduction-apps/rayjoin-paper/section52_lsi.py` | Section 5.2 LSI count runner over `prepare_planar_map_lsi_2d_optix`. |
| `Paper-reproduction-apps/rayjoin-paper/section53_pip.py` | Section 5.3 directed point-location/PIP runner over `prepare_planar_map_point_location_2d_optix`. |
| `Paper-reproduction-apps/rayjoin-paper/section57_overlay.py` | Section 5.7 overlay-output runner over public LSI + point-location primitives plus app-owned output-chain logic. |
| `Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py` | Section 5.7 runner with optional Numba helpers for selected app-layer continuation work. |
| `Paper-reproduction-apps/rayjoin-paper/rayjoin_numba_overlay_kernels.py` | Numba/fallback helper kernels used by the optional Section 5.7 Numba route. |

The top-level `README.md` now links to `Paper-reproduction-apps/README.md` and
lists `Paper-reproduction-apps/` in the repository layout.

## Source Provenance

The programs were promoted from the previously reviewed RayJoin reproduction
work:

- Section 5.2: public LSI front door runner.
- Section 5.3: public directed point-location/PIP front door runner.
- Section 5.7: public LSI + public point-location overlay harness.
- Section 5.7 + Numba: optional app-layer continuation wrapper and kernels.

In the promoted directory, user-facing names were changed from internal goal
identifiers to stable paper-reproduction names. The new directory contains no
`goalNNNN` or `history/internal_docs` references.

## Boundaries

- This is not the benchmark app line.
- These programs do not import or call `rtdsl.rayjoin_overlay`.
- RTDL provides public planar-map LSI and point-location primitives.
- RayJoin-specific output-chain assembly remains app code.
- Full data reproduction still requires local CDB inputs and author comparator
  outputs; those are not fabricated by this directory.
- No broad RayJoin-system speedup claim is made by the directory.

## Validation

Windows source-tree checks:

- `py -3 -m py_compile` passed for all five Python files.
- `--help` passed for `section52_lsi.py`, `section53_pip.py`,
  `section57_overlay.py`, `section57_overlay_numba.py`, and
  `rayjoin_numba_overlay_kernels.py`.
- Numba helper synthetic parity passed through the available fallback path:
  `midpoint_pairs_match`, `dedupe_mask_match`, `chain_has_xsects_match`,
  `chain_keep_match`, and `writer_skip_decision_match` were all `true`.
- Local link existence checks passed for the README targets and referenced
  release-report pages.
- Public scan over `Paper-reproduction-apps/` and root `README.md` found no
  internal goal identifiers or `history/internal_docs` references.

Local Linux smoke:

- A temporary copy of `src/` plus `Paper-reproduction-apps/` was made under
  `/tmp/rtdl_paper_repro_smoke` on `192.168.1.20`.
- Linux `python3 -m py_compile` passed for all five Python files.
- Linux `--help` passed for the four user-facing runner entrypoints.
- Linux Numba/fallback synthetic parity passed:
  `chain_has_xsects_match`, `chain_keep_match`, `dedupe_mask_match`,
  `midpoint_pairs_match`, and `writer_skip_decision_match` were all `true`.
- The temporary Linux copy was removed after the smoke.

## Exit Label

`completed_paper_reproduction_apps_rayjoin_directory_created_and_smoked`
