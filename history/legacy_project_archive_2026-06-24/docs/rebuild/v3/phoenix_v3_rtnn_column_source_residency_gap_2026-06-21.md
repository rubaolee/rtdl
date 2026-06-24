# Phoenix V3 RTNN Column-Source Residency Gap

Status: `rtnn_npz_column_source_ready_for_pod_rerun_not_m7`.

This packet keeps RTNN on the V3 engine path: the current hot query is fast,
but the whole-run wall is still dominated by input and preparation. The new
`npz` column-source route is implemented for the serious runner. The npz column-source route is implemented, but it needs
fresh POD evidence before any M7 or public claim; this packet is not M7.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
```

## Current Wall Breakdown

- Hot-query speedup over CuPy grid: `19.437x`
- Cold+query speedup over CuPy grid: `1.214x`
- Runner-wall speedup over CuPy grid: `1.030x`
- Input load / hot query: `358.227x`
- Non-hot wall / hot query: `490.975x`
- Input-load share of runner wall: `72.814%`

## Implemented V3 Surface

- `--point-column-source csv|numpy_csv|npz` on the serious RTNN runner
- default `npz` column-source path for Phoenix reruns
- `rtnn_npz_xyz_columns_v1` source manifest
- source metadata recorded on both OptiX and CuPy phase rows
- no V4 C ABI, embedding, or app-specific native engine

## Not M7

- The existing POD evidence still has only 1.030x runner-wall speedup versus CuPy.
- Input load is 72.8% of the current prepared self-query runner wall.
- The NPZ column-source path is implemented and locally tested, but it still needs a fresh same-hardware RTX POD rerun.
- No external Claude/Gemini review has accepted a rerun as an M7 row.

## POD Rerun Requirements

- Run the serious same-contract RTNN runner with --point-column-source npz on the RTX pod.
- Save optix and cupy_grid full payloads, point_manifest.json, environment.json, and summary.json.
- Require point_column_source=npz on both phase rows.
- Require same-contract integer parity and sum-distance relative error <= 1e-4.
- Require cold-plus-query and runner-wall speedups to clear the material floor before M7 review.
- Send the rerun packet to external AI and record Codex consensus before any public wording.

## Goal-Level Decision Audit

Decision: Move RTNN wall-path work from prose to a V3 NPZ column-source surface and a rerun gate, while keeping current RTNN rows out of M7.

1. Was I foolish? No. This implements a generic V3 ingestion path inside the existing Python-hosted surface and blocks public claims until POD evidence exists.
2. If yes, what actions made the decision foolish? It would be foolish to repackage the 19.437x hot-query number or the 1.030x runner-wall number as proof that V3 solves RTNN.
3. Was there another path that would have avoided getting stuck on that idea? I could wait for external review of AABB or design a new Barnes-Hut primitive, but that would not address the current RTNN wall-path blocker.
4. Can I now try a different path that actually solves the problem? Run the NPZ column-source RTNN evidence path on the pod; only a material same-contract cold/runner result plus review can reopen M7.
