# Goal3241: RayJoin Overlay RT Failure Isolation

Date: 2026-06-03

## Purpose

Goal3239 established that upstream RayJoin can be built on the pod after CUDA
12.8 compatibility shims, and that `query_exec` can run same-slice LSI/PIP
smokes. The remaining weak point was `polyover_exec -mode=rt`, which crashed on
the bounded public overlay slice.

Goal3241 isolates that failure enough to avoid wasting more pod time on blind
patching.

## Observations

| Probe | Result | Interpretation |
| --- | --- | --- |
| `polyover_exec -mode=rt -check=true` | fails | RT overlay crashes during `MapOverlayRT::LocateVerticesInOtherMap`. |
| `polyover_exec -mode=rt -check=false` | fails | The crash is not caused by the final checker. |
| `polyover_exec -mode=grid -check=true` | fails | Grid overlay checker path also hits a CUDA/Thrust device error. |
| `polyover_exec -mode=grid -check=false` | passes | The CDB inputs and non-RT overlay executable path are usable. |
| RT overlay with `CUDA_VISIBLE_DEVICES=0` | fails | The crash is not fixed by narrowing visible devices. |
| RT overlay with `cudaSetDevice(0)` before `PIPRT::Query` buffer work | fails | The crash is not a simple missing device reset. |
| RT overlay with pre-sized PIP output buffer and logical point-count copy/transform | fails | Avoiding the post-RT `device_vector::resize` does not clear the failure. |

The recurring failure is:

`thrust parallel_for failed: cudaErrorInvalidDevice: invalid device ordinal`

The stack consistently points into `rayjoin::PIPRT::Query()` during
`rayjoin::MapOverlayRT::LocateVerticesInOtherMap()` after the overlay LSI RT
phase.

## Conclusion

The upstream RayJoin overlay RT lane is blocked on this pod/toolchain. The
failure is narrower than "RayJoin cannot build" and narrower than "overlay data
is unusable":

- `query_exec` RT LSI and RT PIP run.
- `polyover_exec` builds.
- `polyover_exec -mode=grid -check=false` runs.
- `polyover_exec -mode=rt` fails during its internal PIP RT subphase.

For RTDL planning, this means Goal3239 can stand as a same-slice build/query
smoke, but not as a same-contract overlay comparison. The next rigorous
cross-system comparison should start with RayJoin `query_exec` LSI/PIP, where
the upstream binary is currently runnable, while overlay should be treated as an
upstream-RayJoin runtime compatibility blocker until someone debugs the RayJoin
overlay RT implementation itself.

## Boundary

This report does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

No RTDL native code was changed for this isolation work. All RayJoin source
edits were local pod-workdir diagnostics against `/root/RayJoin`.
