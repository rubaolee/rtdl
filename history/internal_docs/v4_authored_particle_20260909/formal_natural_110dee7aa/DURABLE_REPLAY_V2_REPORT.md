# Particle durable replay-path successor

Date: 2026-09-09

## Finding

Independent inspection of the immutable `bbbf7ed1a` metadata package found a
real path-contract defect in
`tools/run_postformal_particle_replay_from_durable_110dee7aa.sh`. The script
passes `data/base_particle` as `--base-particle-dir`. The original
reconstruction tool resolves that directory, passes its parent to
`load_particle`, and that loader appends `particle`. It therefore seeks
`data/particle/MANIFEST.json`, while the recorded handoff contains
`data/base_particle/MANIFEST.json` and no recorded alias.

The old script, old 47-file handoff, old metadata package and their identities
remain unchanged. The defective durable command was never executed. The saved
post-formal 160M output was produced by the original `/tmp`-backed command,
whose stdout, receipt and output identity remain retained. Formal workers,
timings, statistics and the original post-formal GPU replay are unaffected.

## Successor contract

`POSTFORMAL_PARTICLE_RECONSTRUCT_DURABLE_V2.py` defines
`--base-particle-dir` as the exact directory containing `MANIFEST.json`. It no
longer relies on the source loader's implicit `particle/` suffix. Before any
GPU work it verifies:

- exact clean source commit and tree;
- the formal archive's one eight-worker program/executable identity set;
- every base member's size, SHA-256, shape and dtype;
- the transition-ensemble schema and binding to the base manifest;
- every ensemble member's size, SHA-256, shape and dtype;
- exact 160M query and oracle shapes.

`--data-preflight-only` exits after those checks and does not require native,
CUDA, OptiX or output arguments. The full successor command is retained in
`RUN_POSTFORMAL_PARTICLE_REPLAY_FROM_DURABLE_V2.sh` with distinct default
output names, so it cannot overwrite the earlier replay.

## Executed validation

The CPU-only preflight ran against the network-volume handoff and exact clean
`110dee7aa` source. It passed with:

- base manifest SHA-256 `c6678099ecff9581726781a765213d5b0890f20ada70561b09dd6dd94a4009af`;
- ensemble manifest SHA-256 `637436a97a913e329d68a0901798e320d37b2a56c37493cd8cbdb1295af7865f`;
- triangles `[3392530,3]`, vertices `[314587,3]`;
- queries `[160000000,7]`, expected output `[160000000,3]`;
- formal program identity `da62ce40ed6e51db638eb916c842161e6025d764abedb4932dfe84f3db710530`;
- formal executable identity `0663bfeefefac2b389c31edbe6d331adbc7fa54f4c7632db666cc6a87a4fa19c`;
- `gpu_execution_performed: false`.

The retained output is `DURABLE_DATA_PREFLIGHT_V2.json`, 982 bytes, SHA-256
`7b10e19f8007dbf0cc0275fd46b44aaca532bdd7d9951815982888bed8bdaa39`.

## Boundary

The successor full GPU replay command has **not** been executed. This work
proves that the new command reaches and validates the exact durable data under
an explicit direct-directory contract; it does not prove the subsequent GPU
compile/execute path, create a second output, or close independent complete
array replay. It creates no performance evidence and changes no latency or
memory conclusion.

The immutable six-file successor packet retains the earlier report byte that
omitted the final `c` from the displayed executable identity. Its included
machine JSON contains the correct 64-digit value. The packet was not rebuilt;
this repository report is the explicit documentation correction.
