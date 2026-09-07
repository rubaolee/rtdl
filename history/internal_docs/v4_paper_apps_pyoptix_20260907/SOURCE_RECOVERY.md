# V4 paper-application source recovery

## Recovery result

The repository now contains all nine historical `Paper-reproduction-apps`
directories, including their app-local dependencies. The recovered tree has
134 non-cache files. `SOURCE_MANIFEST.json` records every byte, size, and
SHA-256 and is regenerated or verified by
`scripts/build_v4_paper_apps_source_manifest.py`.

The one copied source was the read-only historical snapshot at:

`/home/lestat/work/goal5782_clean_validation_v5/source/Paper-reproduction-apps`

The same nine `v4_whole_app.py` byte cohort was observed in 42 historical work
directories. This is evidence of copy consistency, not 42 independent source
authorities.

The recovered bytes deliberately preserve their original line endings. In
particular, 116 of the 134 files contain CRLF records, so an all-path
`git diff --check` reports the retained carriage returns as whitespace. They
are not normalized because doing so would invalidate the recorded source
hashes. The staged diff outside `Paper-reproduction-apps/` passes
`git diff --check` without exception.

## Identity boundary

| App | Recovered V4 SHA-256 | Identity status |
| --- | --- | --- |
| Particle Tracking | `e2d26dd9a67025066ca77d1c57f358c34a8e4446a679b32f772a228ee52712a4` | Matches the independently retained historical hash and consumer binding. |
| Triangle Counting | `8ab4f4ad6c5913483633b06e70035a26637bc2b2a0589ce470623504d86e6210` | Matches the independently retained historical hash and consumer binding. |
| LibRTS | `2952d38b341525d5b529a4391949df5b1ab59cd463c752f4da4df0823e40b987` | Matches the independently retained historical hash and consumer binding. |
| RayDB | `f482f409fbd6cd565d661d8440886835bdc7417e9d934e89f3fad67f664cbc05` | Recovered candidate source for a new experiment; old authority is not claimed. |
| X-HD | `7eb1b7b4c994d5d30a87d214a09fbdcc15e97243720b70b196357d554039d2db` | Recovered candidate source for a new experiment; old authority is not claimed. |
| RTNN | `9ac2119998bf787500177ae02a6beba9172f0230a890f7966094b4a888f7f1f1` | Recovered candidate source for a new experiment; old authority is not claimed. |
| RT-DBSCAN | `8136260817b2e1f4735fd437c603a990c8bab450a441785fa5aebe676547b338` | Recovered candidate source for a new experiment; old authority is not claimed. |
| Spatial RayJoin | `968365001aa3393e782e9404d9432dd56abf605a450c8bddfd5717d0ff569df5` | Recovered candidate source for a new experiment; old authority is not claimed. |
| RT-BarnesHut | `98c0f922d50d64f07f1b10af2118924a0b69ebe1bb59096c040a8912d915bc61` | Recovered candidate source for a new experiment; old authority is not claimed. |

The expected final Goal5785 source archive, SHA-256
`75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41`,
has not been recovered. An earlier source archive exists but has different
bytes and may not be relabelled. Its absence does not prevent the six named
candidate sources from acquiring a new source and experiment identity.

## Checks performed on this checkout

All nine recovered `v4_whole_app.py` modules import successfully with Python
3.12.14, NumPy 2.4.4, Numba 0.65.1 and `PYTHONPATH=src:scripts:.`. Eighteen
focused existing tests covering recovered front doors, runtime inputs,
Particle, AABB-count lowering and triangle device columns pass. No GPU was used
for these checks, so `bytes present`, `imports`, `GPU runnable`, and `executed`
remain separate properties.

The exact real-scale data archive remains available read-only on `lestat-lx1`
at `/home/lestat/work/goal5776_real_scale_data_bundle_20260813.tar.gz`. It is
1,155,932,998 bytes with SHA-256
`f84ed4396dd9e5928bd222f50fca57af2db727a6d994abfc5844a9b1b12981ad`.
Its inventory covers all nine applications. The local GTX 1070 has no RT cores
and is not an authority host for the planned performance comparison.

No historical execution result, performance result, or public claim is created
by source recovery.
