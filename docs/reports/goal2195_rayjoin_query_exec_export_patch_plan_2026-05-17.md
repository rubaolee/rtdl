# Goal2195 RayJoin Query-Exec Export Patch Plan

Date: 2026-05-17

Status: external RayJoin export patch prepared; build/run validation requires
the next RTX pod.

## Purpose

Goal2192 added the RTDL same-query stream consumer. Goal2195 prepares the
matching external RayJoin patch needed for the next pod run: RayJoin
`query_exec` should export the exact generated PIP or LSI query stream it uses
internally, then RTDL should consume that exported stream.

This closes the protocol mismatch identified in Goal2188/Goal2191:

- before: RayJoin generated queries internally, RTDL consumed bounded CDB slices;
- after this patch is validated: RayJoin and RTDL can consume the same base CDB
  and same query stream.

## Patch Artifact

Prepared patch:

- `docs/reports/goal2195_rayjoin_query_exec_export_patch_2026-05-17.diff`

The patch targets RayJoin commit:

- `02bf6220d6d20b04af77ee20364eced75cc029c9`

It was produced from a disposable checkout under:

- `scratch/goal2195_rayjoin_patch/RayJoin`

The scratch checkout is not part of the committed source tree.

Local patch hygiene:

- `git apply --check docs/reports/goal2195_rayjoin_query_exec_export_patch_2026-05-17.diff`
  passed against a clean checkout reset to
  `02bf6220d6d20b04af77ee20364eced75cc029c9`.

## What The Patch Adds

The patch adds a RayJoin flag:

- `-query_stream_output=<path>`

When set, RayJoin `query_exec` writes a JSON stream using:

- `schema: rtdl.rayjoin.same_query_stream.v1`
- `producer: rayjoin_query_exec_export_patch`
- `same_contract_with_rayjoin_query_exec: true`

For `-query=pip`, it exports:

- generated query point id,
- unscaled `x`,
- unscaled `y`.

For `-query=lsi`, it exports:

- generated query edge id,
- unscaled `x0`,
- unscaled `y0`,
- unscaled `x1`,
- unscaled `y1`.

The IDs are intentionally RayJoin-native zero-based IDs:

- PIP point id uses the generated point index.
- LSI segment id uses RayJoin's generated `edge.eid`.

This avoids a later off-by-one adapter problem when comparing against RayJoin
outputs.

## Boundary

The patch is for the disposable external RayJoin comparison checkout only. It
must not be copied into RTDL native code.

It is intended to be observational:

- no RayJoin traversal algorithm change,
- no RayJoin refinement algorithm change,
- no RTDL native engine change,
- no app-specific RTDL native symbol,
- no performance claim by itself.

## Next Pod Command Shape

After applying the patch in the RayJoin checkout and rebuilding:

```bash
release/bin/query_exec \
  -poly1="$DATA/br_county_clean_25_odyssey_final.txt" \
  -query=lsi \
  -mode=rt \
  -gen_n=100000 \
  -gen_t=0.1 \
  -seed=2184 \
  -warmup=1 \
  -repeat=3 \
  -query_stream_output=/root/goal2184_pod/artifacts/rayjoin_lsi_gen100k_stream.json
```

Then feed the stream to RTDL:

```bash
PYTHONPATH=src:. python3 scripts/goal2192_rayjoin_same_query_stream_runner.py run-stream \
  --query-stream /root/goal2184_pod/artifacts/rayjoin_lsi_gen100k_stream.json \
  --output docs/reports/goal2196_rtdl_lsi_same_rayjoin_stream_pod_2026-05-17.json \
  --backends cpu,embree,optix \
  --warmups 1 \
  --repeats 3
```

Repeat for `-query=pip`.

## What Remains Blocked

This patch has not yet been compiled or run on the RTX pod. Therefore it does
not yet prove:

- RayJoin export build compatibility,
- RayJoin-exported stream validity,
- RTDL same-RayJoin-stream performance,
- RTDL-vs-RayJoin speedup,
- full RayJoin paper reproduction,
- v2.0 release readiness.

## Verdict

Goal2195 is ready for pod validation.

The next meaningful step requires an RTX pod because the patch must be applied
to RayJoin, rebuilt with OptiX, run to export real query streams, and then used
by RTDL for same-query timing.
