# Codex V4 M1 Cross-Stream Event-Wait 2-AI Consensus

Date: 2026-06-19.
Scope: V4.0 M1 `fixed_radius_count_threshold_2d` only.

## Decision Request

Should V4.0 M1 replace the current fail-closed behavior for different nonzero
prepare/query CUDA streams with a narrow native prepare-ready event contract?

Proposed contract:

- the prepared fixed-radius handle owns a CUDA event;
- native prepare records that event after prepare-dependent CUDA/OptiX work;
- native query waits on that event when the query stream differs from the
  prepare stream;
- prepare and query still synchronize before returning to Python;
- no async, full external stream ownership, public true-zero-copy, package,
  PyTorch, full Numba, DLPack, stable SDK, or speedup claim is authorized.

## Reviewer Verdicts

Archimedes: APPROVE with narrow scope. The blocker may close only for the
fixed-radius M1 prepare/query bridge if native code records a prepare-ready
event, waits from the different query stream, keeps synchronous host return,
and leaves async/full ownership/public performance claims blocked.

Epicurus: AMEND. The direction is acceptable only if event creation, record,
wait, and destroy are explicit fail-closed native behavior; same-stream,
different-stream, zero/default-stream, metadata, and claim-guard tests must
remain in place.

Hegel: no verdict returned before timeout.

## Consensus

Proceed with the narrow M1 contract:

> V4.0 M1 supports fixed-radius prepare/query ordering across distinct nonzero
> CUDA streams by recording a native prepare-ready event on the prepared handle
> and waiting on it from the query stream. Native calls remain synchronized
> before returning.

Do not generalize this to:

- async or nonblocking completion;
- caller-owned public event handles;
- full external stream ownership;
- general cross-stream behavior outside the fixed-radius M1 route;
- public true-zero-copy;
- PyTorch route support;
- full Numba partner surface;
- arbitrary/full DLPack route support;
- stable SDK/package/PyPI/wheel support;
- RT-core, RTX, or public speedup claims.

## Required Gates

- Unit tests prove different prepare/query streams no longer fail closed and
  metadata marks the event wait as required.
- Source guard proves `cuEventCreate`, `cuEventRecord`, `cuStreamWaitEvent`,
  and `cuEventDestroy` remain in the native fixed-radius prepared handle path.
- GPU evidence proves two distinct CuPy streams produce correct outputs and a
  query-stream consumer checksum.
- Same-stream evidence still passes and reports no unnecessary event wait.
- Release-candidate blocker manifest closes only the narrow fixed-radius M1
  stream-ordering blocker.
